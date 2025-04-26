from django.contrib.auth import login
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.authentication import SessionAuthentication

from .models import User, DoctorProfile, PatientProfile
from .serializers import (
    UserSerializer, UserRegistrationSerializer, LoginSerializer,
    ChangePasswordSerializer, DoctorRegistrationSerializer,
    PatientProfileSerializer, DoctorProfileSerializer,
    PatientProfileUpdateSerializer, DoctorProfileUpdateSerializer
)
from .permissions import IsAdmin, IsPatient, IsDoctor, IsSelfOrAdmin


# Custom session authentication class that doesn't enforce CSRF
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        # Do not enforce CSRF checks for this authentication
        return


class RegisterView(generics.CreateAPIView):
    """
    View for patient self-registration.
    This endpoint allows new patients to register an account.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    """
    View for user login.
    Returns JWT tokens for authentication.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = [CsrfExemptSessionAuthentication]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    View for retrieving and updating the authenticated user's profile.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """
    View for changing user password.
    Accepts POST requests for password changes.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check old password
        if not user.check_password(serializer.validated_data.get('old_password')):
            return Response(
                {'old_password': ['Wrong password.']},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Set new password
        user.set_password(serializer.validated_data.get('new_password'))
        user.save()
        
        # Update session with new password to prevent logout
        login(request, user)
        
        # Generate new JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Return success response with new tokens
        return Response({
            'detail': 'Password changed successfully.',
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }, status=status.HTTP_200_OK)
        
    # Keep PUT/PATCH support for backward compatibility
    def put(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
        
    def patch(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class DoctorRegistrationView(generics.CreateAPIView):
    """
    View for doctor registration (admin only).
    """
    queryset = User.objects.all()
    permission_classes = [IsAdmin]
    serializer_class = DoctorRegistrationSerializer


class PatientProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving patient profiles.
    Permissions:
    - Admins can see all patient profiles
    - Doctors can see profiles of their patients
    - Patients can only see their own profile
    """
    serializer_class = PatientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Admin can see all
        if user.role == 'admin' or user.is_superuser:
            return PatientProfile.objects.all()
            
        # Patient can only see their own profile
        if user.role == 'patient':
            return PatientProfile.objects.filter(user=user)
            
        # Doctors can see patients they have appointments with
        if user.role == 'doctor':
            return PatientProfile.objects.filter(
                user__patient_appointments__doctor=user
            ).distinct()
            
        return PatientProfile.objects.none()
    
    @action(detail=True, methods=['put', 'patch'], permission_classes=[IsSelfOrAdmin], serializer_class=PatientProfileUpdateSerializer)
    def update_profile(self, request, pk=None):
        patient_profile = self.get_object()
        
        if request.method == 'PUT':
            serializer = PatientProfileUpdateSerializer(patient_profile, data=request.data)
        else:
            serializer = PatientProfileUpdateSerializer(patient_profile, data=request.data, partial=True)
            
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)


class DoctorProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving doctor profiles.
    - Everyone can see doctor profiles
    - Only admins and the doctor themselves can update profiles
    """
    queryset = DoctorProfile.objects.all()
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['put', 'patch'], permission_classes=[IsSelfOrAdmin], serializer_class=DoctorProfileUpdateSerializer)
    def update_profile(self, request, pk=None):
        doctor_profile = self.get_object()
        
        if request.method == 'PUT':
            serializer = DoctorProfileUpdateSerializer(doctor_profile, data=request.data)
        else:
            serializer = DoctorProfileUpdateSerializer(doctor_profile, data=request.data, partial=True)
            
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_profile(self, request):
        """
        Get the authenticated doctor's own profile.
        """
        if request.user.role != 'doctor':
            return Response(
                {'detail': 'Only doctors can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        doctor_profile = DoctorProfile.objects.get(user=request.user)
        serializer = self.get_serializer(doctor_profile)
        return Response(serializer.data)
