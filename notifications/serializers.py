from rest_framework import serializers
from .models import Notification, NotificationTemplate, AppointmentReminder
from users.serializers import UserBasicSerializer


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for user notifications"""
    recipient_details = UserBasicSerializer(source='recipient', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'recipient_details', 'title', 'message',
            'notification_type', 'appointment_id', 'status', 
            'created_at', 'updated_at', 'read_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'read_at']
        
    def update(self, instance, validated_data):
        # Handle marking notifications as read
        if 'status' in validated_data and validated_data['status'] == 'read':
            if instance.status == 'unread':
                import timezone
                instance.read_at = timezone.now()
        return super().update(instance, validated_data)


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for notification templates"""
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'template_type', 'content', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class AppointmentReminderSerializer(serializers.ModelSerializer):
    """Serializer for appointment reminders"""
    recipient_details = UserBasicSerializer(source='recipient', read_only=True)
    
    class Meta:
        model = AppointmentReminder
        fields = [
            'id', 'appointment_id', 'recipient', 'recipient_details',
            'message', 'scheduled_time', 'status', 'sent_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'sent_at']