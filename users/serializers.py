from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, DoctorProfile, PatientProfile


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model, used for general user information"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'phone_number', 
                  'date_of_birth', 'city', 'state', 'country', 'is_active']
        read_only_fields = ['role', 'is_active']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'first_name', 'last_name', 
                  'phone_number', 'date_of_birth']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        # Default role is patient for self-registration
        user = User.objects.create_user(role='patient', **validated_data)
        # Create associated patient profile
        PatientProfile.objects.create(user=user)
        return user


class PatientProfileSerializer(serializers.ModelSerializer):
    """Serializer for patient profile information"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = PatientProfile
        fields = ['user', 'patient_id', 'identity_id', 'blood_type', 'conditions', 
                  'weight', 'emergency_contact_name', 'emergency_contact_phone', 
                  'emergency_contact_relationship']
        read_only_fields = ['patient_id']


class DoctorProfileSerializer(serializers.ModelSerializer):
    """Serializer for doctor profile information"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = DoctorProfile
        fields = ['user', 'doctor_id', 'specialization', 'years_of_experience', 
                  'available_from', 'available_to', 'working_days']
        read_only_fields = ['doctor_id']


class DoctorRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for doctor registration (admin only)"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    specialization = serializers.CharField(required=True, write_only=True)
    years_of_experience = serializers.IntegerField(required=True, write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone_number', 
                  'date_of_birth', 'specialization', 'years_of_experience']
    
    def create(self, validated_data):
        # Extract doctor profile specific fields
        specialization = validated_data.pop('specialization')
        years_of_experience = validated_data.pop('years_of_experience')
        
        # Create the user with doctor role
        user = User.objects.create_user(role='doctor', **validated_data)
        
        # Create the doctor profile
        DoctorProfile.objects.create(
            user=user,
            specialization=specialization,
            years_of_experience=years_of_experience
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        user = authenticate(
            username=attrs.get('email'),
            password=attrs.get('password')
        )
        
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled.')
            
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs


class PatientProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating patient profile"""
    
    class Meta:
        model = PatientProfile
        fields = ['identity_id', 'blood_type', 'conditions', 'weight', 
                  'emergency_contact_name', 'emergency_contact_phone', 
                  'emergency_contact_relationship']


class DoctorProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating doctor profile"""
    
    class Meta:
        model = DoctorProfile
        fields = ['specialization', 'years_of_experience', 
                  'available_from', 'available_to', 'working_days']