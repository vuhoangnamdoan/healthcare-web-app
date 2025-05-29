from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Appointment, Booking
from users.serializers import UserSerializer, DoctorProfileSerializer, PatientProfileSerializer
from users.models import Doctor, Patient


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for appointment slots created by doctors."""
    doctor_info = DoctorProfileSerializer(source='doctor', read_only=True)
    week_day_display = serializers.CharField(source='get_week_day_display', read_only=True)
    end_time = serializers.SerializerMethodField()
    slot_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'appointment_id', 'doctor', 'doctor_info', 'week_day', 'week_day_display',
            'start_time', 'end_time', 'duration', 'is_available', 'slot_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['appointment_id', 'created_at', 'updated_at']
    
    def get_end_time(self, obj):
        return obj.get_end_time()
    
    def get_slot_status(self, obj):
        return "Available" if obj.is_slot_available() else "Booked"
    
    def validate(self, data):
        appointment = Appointment(**data)
        try:
            appointment.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return data


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating appointment slots (doctors only)."""
    class Meta:
        model = Appointment
        fields = [
            'doctor', 'week_day', 'start_time', 'duration', 'is_available'
        ]
    
    def validate(self, data):
        """Validate appointment creation data."""
        appointment = Appointment(**data)
        try:
            appointment.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return data


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for patient bookings of appointment slots."""
    appointment_info = AppointmentSerializer(source='appointment', read_only=True)
    patient_info = PatientProfileSerializer(source='patient', read_only=True)
    doctor_info = serializers.SerializerMethodField()
    booking_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = [
            'booking_id', 'appointment', 'appointment_info', 'patient', 'patient_info',
            'doctor_info', 'reason', 'booking_status', 'is_canceled', 'canceled_at',
            'cancellation_reason', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'booking_id', 'canceled_at', 'created_at', 'updated_at'
        ]
    
    def get_doctor_info(self, obj):
        return DoctorProfileSerializer(obj.appointment.doctor).data
    
    def get_booking_status(self, obj):
        if obj.is_canceled:
            return f"Canceled on {obj.canceled_at.strftime('%Y-%m-%d %H:%M')}" if obj.canceled_at else "Canceled"
        return "Active"
    
    def validate(self, data):
        booking = Booking(**data)
        try:
            booking.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return data


class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new bookings (patients only)."""
    class Meta:
        model = Booking
        fields = ['appointment', 'patient', 'reason']
    
    def validate_appointment(self, value):
        if not value.is_slot_available():
            raise serializers.ValidationError(
                "This appointment slot is no longer available."
            )
        return value
    
    def validate_patient(self, value):
        if not value:
            raise serializers.ValidationError("Patient is required.")
        return value

    def validate(self, data):
        booking = Booking(**data)
        try:
            booking.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return data


class BookingCancelSerializer(serializers.Serializer):
    """Serializer for canceling bookings."""
    cancellation_reason = serializers.CharField(max_length=500, required=False, 
        help_text="Optional reason for cancellation"
    )
    
    def update(self, instance, validated_data):
        reason = validated_data.get('cancellation_reason')
        instance.cancel_booking(reason=reason)
        return instance


class AvailableAppointmentSerializer(serializers.ModelSerializer):
    """Serializer for listing available appointment slots for booking."""
    doctor_info = serializers.SerializerMethodField()
    week_day_display = serializers.CharField(source='get_week_day_display', read_only=True)
    end_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'appointment_id', 'doctor_info', 'week_day', 'week_day_display',
            'start_time', 'end_time', 'duration'
        ]
    
    def get_doctor_info(self, obj):
        return {
            'doctor_id': obj.doctor.user.user_id,
            'name': f"Dr. {obj.doctor.user.get_full_name()}",
            'speciality': obj.doctor.speciality,
            'experience': obj.doctor.experience
        }
    
    def get_end_time(self, obj):
        return obj.get_end_time()


class DoctorAvailabilitySerializer(serializers.Serializer):
    """Serializer for managing doctor availability."""
    week_day = serializers.IntegerField(min_value=1, max_value=7)
    start_time = serializers.TimeField()
    duration = serializers.IntegerField(min_value=15, max_value=120)
    
    def validate(self, data):
        if data['duration'] % 15 != 0:
            raise serializers.ValidationError(
                "Duration must be in 15-minute intervals."
            )
        return data