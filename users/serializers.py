from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, Patient, Doctor


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model, used for general user information"""
    class Meta:
        model = User
        fields = ['user_id', 'email', 'first_name', 'last_name', 'role', 'is_active']
        read_only_fields = ['role', 'is_active']


class PatientRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for patient self-registration - creates User + Patient profile"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    # Patient profile fields
    phone = serializers.CharField(max_length=20, required=False, write_only=True)
    dob = serializers.DateField(required=True, write_only=True)
    address1 = serializers.CharField(max_length=255, required=True, write_only=True)
    address2 = serializers.CharField(max_length=255, required=False, write_only=True)
    city = serializers.CharField(max_length=100, required=True, write_only=True)
    state = serializers.CharField(max_length=100, required=True, write_only=True)
    zip_code = serializers.CharField(max_length=20, required=True, write_only=True)
    identity_id = serializers.CharField(max_length=50, required=True, write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password2', 'first_name', 'last_name',
            'phone', 'dob', 'address1', 'address2', 'city', 'state', 'zip_code', 'identity_id'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        # Extract patient profile specific fields
        patient_fields = {
            'phone': validated_data.pop('phone', ''),
            'dob': validated_data.pop('dob'),
            'address1': validated_data.pop('address1'),
            'address2': validated_data.pop('address2', ''),
            'city': validated_data.pop('city'),
            'state': validated_data.pop('state'),
            'zip_code': validated_data.pop('zip_code'),
            'identity_id': validated_data.pop('identity_id'),
        }
        
        # Remove password2 and create user
        validated_data.pop('password2')
        user = User.objects.create_user(role='patient', **validated_data)
        
        # Create associated patient profile
        Patient.objects.create(user=user, **patient_fields)
        return user
    
    def to_representation(self, instance):
        return {
            'message': 'User created successfully',
            'user_id': str(instance.user_id),
            'email': instance.email
        }


class PatientProfileSerializer(serializers.ModelSerializer):
    """Serializer for patient profile information display"""
    user = UserSerializer(read_only=True)
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = ['user', 'phone', 'dob', 'age', 'address1', 'address2', 'city', 
                  'state', 'zip_code', 'identity_id', 'blood_type', 'weight', 'height',
                  'emergency_contact_name', 'emergency_contact_phone', 
                  'emergency_contact_relationship']
    
    def get_age(self, obj):
        return obj.get_age()


class DoctorProfileSerializer(serializers.ModelSerializer):
    """Serializer for doctor profile information display"""
    user = UserSerializer(read_only=True)
    working_days_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctor
        fields = ['user', 'speciality', 'dob', 'experience', 'working_day', 
                  'working_days_display', 'from_time', 'to_time', 'description', 
                  'is_available']
    
    def get_working_days_display(self, obj):
        return obj.get_working_days_display()


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
        model = Patient
        fields = ['phone', 'dob', 'address1', 'address2', 'city', 'state', 'zip_code',
                  'blood_type', 'weight', 'height', 'emergency_contact_name', 
                  'emergency_contact_phone', 'emergency_contact_relationship']


class DoctorProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating doctor profile"""
    class Meta:
        model = Doctor
        fields = ['speciality', 'dob', 'experience', 'working_day', 'from_time', 
                  'to_time', 'description', 'is_available']