from rest_framework import serializers
from .models import Appointment, AvailabilitySlot
from users.serializers import UserSerializer
from users.models import User, DoctorProfile


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Serializer for appointment creation and updates.
    """
    patient = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='patient'),
        required=False  # Not required as it may be set from the current user
    )
    doctor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='doctor'),
        required=False  # We'll make this optional when doctor_id is provided
    )
    doctor_id = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Appointment
        fields = [
            'appointment_id', 'patient', 'doctor', 'doctor_id',
            'date', 'start_time', 'end_time', 'duration_minutes',
            'reason', 'notes', 'status', 'created_at',
            'updated_at', 'cancellation_reason', 'confirmation_timestamp'
        ]
        read_only_fields = ['appointment_id', 'created_at', 'updated_at']
    
    def validate(self, data):
        # If doctor_id is provided, find the doctor user
        if 'doctor_id' in data and not 'doctor' in data:
            try:
                doctor_profile = DoctorProfile.objects.get(doctor_id=data['doctor_id'])
                data['doctor'] = doctor_profile.user
                # Remove doctor_id from data as it's not a model field
                data.pop('doctor_id')
            except DoctorProfile.DoesNotExist:
                raise serializers.ValidationError(
                    {"doctor_id": f"Doctor with ID {data['doctor_id']} does not exist."}
                )
        
        # Check if either doctor or doctor_id is provided
        if 'doctor' not in data:
            raise serializers.ValidationError(
                {"doctor": "Either doctor (User ID) or doctor_id (e.g., DOC-XXXXXXXX) must be provided."}
            )
            
        # Check if doctor is available at the specified time
        if 'date' in data and 'start_time' in data and 'end_time' in data and 'doctor' in data:
            try:
                doctor_profile = DoctorProfile.objects.get(user=data['doctor'])
                doctor_id = doctor_profile.doctor_id
                
                if not AvailabilitySlot.objects.filter(
                    doctor_id=doctor_id,
                    date=data['date'],
                    start_time__lte=data['start_time'],
                    end_time__gte=data['end_time'],
                    is_available=True
                ).exists():
                    raise serializers.ValidationError(
                        {"doctor": "Doctor is not available during this time slot."}
                    )
            except DoctorProfile.DoesNotExist:
                raise serializers.ValidationError(
                    {"doctor": "The selected user does not have a doctor profile."}
                )
        
        # Check if start time is before end time
        if 'start_time' in data and 'end_time' in data:
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError(
                    {"end_time": "End time must be after start time."}
                )
        
        return data


class AppointmentDetailSerializer(AppointmentSerializer):
    """
    Serializer for detailed appointment view.
    Includes user details instead of just IDs.
    """
    patient = UserSerializer(read_only=True)
    doctor = UserSerializer(read_only=True)


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    """
    Serializer for doctor availability slots
    """
    class Meta:
        model = AvailabilitySlot
        fields = [
            'doctor_id', 'date', 'start_time', 'end_time', 
            'is_available', 'week_day'
        ]
    
    def validate(self, data):
        # Check if start time is before end time
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError(
                {"end_time": "End time must be after start time."}
            )
        
        return data