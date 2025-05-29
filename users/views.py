from django.contrib.auth import login
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.authentication import SessionAuthentication

from .models import User, Patient, Doctor
from .serializers import (
    UserSerializer, PatientRegistrationSerializer, LoginSerializer,
    ChangePasswordSerializer, PatientProfileSerializer, DoctorProfileSerializer,
    PatientProfileUpdateSerializer, DoctorProfileUpdateSerializer
)
from .permissions import IsPatient, IsDoctor, IsSelf

# Custom session authentication class that doesn't enforce CSRF
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class PatientRegisterView(generics.CreateAPIView):
    """
    View for patient self-registration.
    This endpoint allows new patients to register an account.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = PatientRegistrationSerializer

    def post(self, request, *args, **kwargs):
        print("🔍 DEBUG: Received registration data:", request.data)  # Add this line
        return super().post(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    """
    View for user login.
    Returns JWT tokens for authentication.
    Both patients and doctors login via frontend
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
        })


# PROFILE MANAGEMENT (Role-based)
class MyProfileView(APIView):
    """
    View for retrieving the authenticated user's profile.
    Handle both Patient and Doctor profiles
    Get profile based on user role
    """
    permission_classes = [permissions.IsAuthenticated, IsSelf]
    
    def get(self, request):
        user = request.user

        if user.role == 'patient':
            try:
                patient = Patient.objects.get(user=user)
                serializer = PatientProfileSerializer(patient)
                return Response(serializer.data)
            except Patient.DoesNotExist:
                return Response({"detail": "Patient profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        elif user.role == 'doctor':
            try:
                doctor = Doctor.objects.get(user=user)
                serializer = DoctorProfileSerializer(doctor)
                return Response(serializer.data)
            except Doctor.DoesNotExist:
                return Response({"detail": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            # Admin user - return basic user info
            serializer = UserSerializer(user)
            return Response(serializer.data)


class UpdateProfileView(APIView):
    """Update current user's profile based on role"""
    permission_classes = [permissions.IsAuthenticated, IsSelf]
    
    def put(self, request):
        user = request.user
        
        if user.role == 'patient':
            try:
                patient = Patient.objects.get(user=user)
                serializer = PatientProfileUpdateSerializer(patient, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Patient.DoesNotExist:
                return Response({"detail": "Patient profile not found."}, status=status.HTTP_404_NOT_FOUND)
                
        elif user.role == 'doctor':
            try:
                doctor = Doctor.objects.get(user=user)
                serializer = DoctorProfileUpdateSerializer(doctor, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except Doctor.DoesNotExist:
                return Response({"detail": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND)
                
        return Response({"detail": "Profile update not allowed for this user type."}, status=status.HTTP_403_FORBIDDEN)

class ChangePasswordView(APIView):
    """Change password for authenticated users"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
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
        
        # Generate new JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'detail': 'Password changed successfully.',
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Logout for authenticated users"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


# 7. DOCTOR LIST (For Patient Booking)
class DoctorListView(generics.ListAPIView):
    """List available doctors for patient booking"""
    queryset = Doctor.objects.filter(is_available=True)
    serializer_class = DoctorProfileSerializer
    permission_classes = [IsPatient]
    
    def get_queryset(self):
        queryset = Doctor.objects.filter(is_available=True).select_related('user').order_by('user__first_name', 'user__last_name')
        speciality = self.request.query_params.get('speciality')
        if speciality:
            queryset = queryset.filter(speciality=speciality)
        return queryset
