from django.contrib import admin
from .models import Appointment, AvailabilitySlot, MedicalRecord


class MedicalRecordInline(admin.StackedInline):
    model = MedicalRecord
    can_delete = False
    verbose_name_plural = 'Medical Record'
    fk_name = 'appointment'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'date', 'doctor')
    search_fields = ('patient__email', 'doctor__email', 'patient__first_name', 'doctor__first_name', 
                     'patient__last_name', 'doctor__last_name', 'reason', 'notes')
    date_hierarchy = 'date'
    inlines = [MedicalRecordInline]


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'start_time', 'end_time', 'is_available')
    list_filter = ('is_available', 'date', 'doctor')
    search_fields = ('doctor__email', 'doctor__first_name', 'doctor__last_name')
    date_hierarchy = 'date'


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'diagnosis', 'follow_up_required', 'follow_up_date')
    list_filter = ('follow_up_required', 'follow_up_date')
    search_fields = ('appointment__patient__email', 'appointment__doctor__email', 'diagnosis', 
                     'prescription', 'treatment_plan')
