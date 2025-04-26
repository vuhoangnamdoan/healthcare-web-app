from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class Notification(models.Model):
    """Model for storing user notifications"""
    
    # Notification status choices
    UNREAD = 'unread'
    READ = 'read'
    ARCHIVED = 'archived'
    
    STATUS_CHOICES = [
        (UNREAD, _('Unread')),
        (READ, _('Read')),
        (ARCHIVED, _('Archived')),
    ]
    
    # Notification type choices
    APPOINTMENT_REMINDER = 'appointment_reminder'
    APPOINTMENT_CONFIRMED = 'appointment_confirmed'
    APPOINTMENT_CANCELLED = 'appointment_cancelled'
    APPOINTMENT_RESCHEDULED = 'appointment_rescheduled'
    SYSTEM_NOTIFICATION = 'system_notification'
    
    TYPE_CHOICES = [
        (APPOINTMENT_REMINDER, _('Appointment Reminder')),
        (APPOINTMENT_CONFIRMED, _('Appointment Confirmed')),
        (APPOINTMENT_CANCELLED, _('Appointment Cancelled')),
        (APPOINTMENT_RESCHEDULED, _('Appointment Rescheduled')),
        (SYSTEM_NOTIFICATION, _('System Notification')),
    ]
    
    recipient = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    appointment_id = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=UNREAD)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient']),
            models.Index(fields=['status']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['appointment_id']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} for {self.recipient} - {self.title}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if self.status == self.UNREAD:
            self.status = self.READ
            self.read_at = timezone.now()
            self.save()
    
    def archive(self):
        """Archive notification"""
        self.status = self.ARCHIVED
        self.save()


class NotificationTemplate(models.Model):
    """Model for notification templates"""
    
    # Template type choices
    APPOINTMENT_REMINDER = 'appointment_reminder'
    APPOINTMENT_CONFIRMATION = 'appointment_confirmation'
    APPOINTMENT_CANCELLATION = 'appointment_cancellation'
    
    TEMPLATE_TYPE_CHOICES = [
        (APPOINTMENT_REMINDER, _('Appointment Reminder')),
        (APPOINTMENT_CONFIRMATION, _('Appointment Confirmation')),
        (APPOINTMENT_CANCELLATION, _('Appointment Cancellation')),
    ]
    
    name = models.CharField(max_length=100, default="Default Template")
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPE_CHOICES, default=APPOINTMENT_REMINDER)
    content = models.TextField(help_text=_("Use {patient_name}, {doctor_name}, {date}, {time}, etc. as placeholders"), default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['template_type', 'is_active']
        indexes = [
            models.Index(fields=['template_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"


class AppointmentReminder(models.Model):
    """Model for appointment reminders"""
    
    # Reminder status choices
    PENDING = 'pending'
    SENT = 'sent'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (SENT, _('Sent')),
        (FAILED, _('Failed')),
        (CANCELLED, _('Cancelled')),
    ]
    
    appointment_id = models.CharField(max_length=50)
    recipient = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='appointment_reminders')
    message = models.TextField()
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=PENDING)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-scheduled_time']
        indexes = [
            models.Index(fields=['appointment_id']),
            models.Index(fields=['recipient']),
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_time']),
        ]
    
    def __str__(self):
        return f"Reminder for {self.appointment_id} to {self.recipient}"
    
    def mark_as_sent(self):
        """Mark reminder as sent"""
        self.status = self.SENT
        self.sent_at = timezone.now()
        self.save()
    
    def mark_as_failed(self):
        """Mark reminder as failed"""
        self.status = self.FAILED
        self.save()
    
    def cancel(self):
        """Cancel reminder"""
        self.status = self.CANCELLED
        self.save()
