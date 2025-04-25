from django.contrib import admin
from .models import Appointment, AvailabilitySlot


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('appointment_id', 'patient', 'doctor', 'date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'date', 'doctor')
    search_fields = ('appointment_id', 'patient__email', 'doctor__email', 'reason', 'notes')
    date_hierarchy = 'date'
    readonly_fields = ('appointment_id', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('appointment_id', 'patient', 'doctor')
        }),
        ('Schedule', {
            'fields': ('date', 'start_time', 'end_time', 'duration_minutes')
        }),
        ('Details', {
            'fields': ('reason', 'notes', 'status')
        }),
        ('Metadata', {
            'fields': ('cancellation_reason', 'confirmation_timestamp', 'created_at', 'updated_at')
        }),
    )


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ('doctor_id', 'date', 'start_time', 'end_time', 'is_available')
    list_filter = ('is_available', 'date', 'week_day')
    search_fields = ('doctor_id',)
    date_hierarchy = 'date'
