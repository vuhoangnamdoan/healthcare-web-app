from django.db import models
from django.utils.translation import gettext_lazy as _


class Appointment(models.Model):
    """Model for medical appointments between patients and doctors."""
    
    # Status choices for appointment
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    
    STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (CONFIRMED, _('Confirmed')),
        (CANCELLED, _('Cancelled')),
        (COMPLETED, _('Completed')),
    ]
    
    # Foreign keys will be imported at runtime to avoid circular imports
    patient = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='doctor_appointments')
    
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    reason = models.TextField()
    notes = models.TextField(blank=True)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.patient} - {self.doctor} - {self.date} {self.start_time}"
    
    def is_pending(self):
        return self.status == self.PENDING
    
    def is_confirmed(self):
        return self.status == self.CONFIRMED
    
    def is_cancelled(self):
        return self.status == self.CANCELLED
    
    def is_completed(self):
        return self.status == self.COMPLETED


class AvailabilitySlot(models.Model):
    """Model to track doctor availability for appointments."""
    
    doctor = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='availability_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['date', 'start_time']
        unique_together = ['doctor', 'date', 'start_time', 'end_time']
    
    def __str__(self):
        return f"{self.doctor} - {self.date} {self.start_time}-{self.end_time}"


class MedicalRecord(models.Model):
    """Model for storing medical records associated with appointments."""
    
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='medical_record')
    diagnosis = models.TextField()
    prescription = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Medical Record for {self.appointment}"
