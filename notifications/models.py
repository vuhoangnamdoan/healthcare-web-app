from django.db import models
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    """Model for storing notifications sent to users."""
    
    # Notification types
    APPOINTMENT_REMINDER = 'appointment_reminder'
    APPOINTMENT_CONFIRMATION = 'appointment_confirmation'
    APPOINTMENT_CANCELLATION = 'appointment_cancellation'
    APPOINTMENT_RESCHEDULED = 'appointment_rescheduled'
    GENERAL = 'general'
    
    TYPE_CHOICES = [
        (APPOINTMENT_REMINDER, _('Appointment Reminder')),
        (APPOINTMENT_CONFIRMATION, _('Appointment Confirmation')),
        (APPOINTMENT_CANCELLATION, _('Appointment Cancellation')),
        (APPOINTMENT_RESCHEDULED, _('Appointment Rescheduled')),
        (GENERAL, _('General')),
    ]
    
    # Status of the notification
    PENDING = 'pending'
    SENT = 'sent'
    FAILED = 'failed'
    
    STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (SENT, _('Sent')),
        (FAILED, _('Failed')),
    ]
    
    recipient = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='notifications')
    appointment = models.ForeignKey('appointments.Appointment', on_delete=models.SET_NULL, 
                                   null=True, blank=True, related_name='notifications')
    
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    delivery_method = models.CharField(max_length=10, choices=[('email', _('Email')), ('sms', _('SMS'))], default='email')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scheduled_time = models.DateTimeField()
    sent_time = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-scheduled_time']
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.recipient} - {self.subject}"
    
    def is_pending(self):
        return self.status == self.PENDING
    
    def is_sent(self):
        return self.status == self.SENT
    
    def is_failed(self):
        return self.status == self.FAILED


class NotificationTemplate(models.Model):
    """Model for storing templates for different types of notifications."""
    
    notification_type = models.CharField(max_length=30, choices=Notification.TYPE_CHOICES, unique=True)
    subject_template = models.CharField(max_length=255)
    message_template = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Template for {self.get_notification_type_display()}"
