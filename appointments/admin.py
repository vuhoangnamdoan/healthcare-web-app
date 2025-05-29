from django.contrib import admin
from .models import Appointment, Booking
from django.db.models import Q


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'appointment_id', 'get_doctor_name', 'get_week_day_display', 
        'start_time', 'get_end_time', 'duration', 'is_available', 'created_at'
    )
    list_filter = ('week_day', 'is_available', 'doctor__speciality', 'created_at')
    search_fields = (
        'appointment_id', 'doctor__user__first_name', 'doctor__user__last_name',
        'doctor__user__email', 'doctor__speciality'
    )
    readonly_fields = ('appointment_id', 'created_at', 'updated_at', 'get_end_time')
    fieldsets = (
        ('Appointment Information', {
            'fields': ('appointment_id', 'doctor')
        }),
        ('Schedule', {
            'fields': ('week_day', 'start_time', 'duration', 'get_end_time')
        }),
        ('Availability', {
            'fields': ('is_available',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.get_full_name()}"
    get_doctor_name.short_description = 'Doctor'
    
    def get_week_day_display(self, obj):
        return obj.get_week_day_display()
    get_week_day_display.short_description = 'Day'
    
    def get_end_time(self, obj):
        end_time = obj.get_end_time()
        return end_time.strftime('%H:%M') if end_time else 'Not calculated'
    get_end_time.short_description = 'End Time'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_id', 'get_patient_name', 'get_doctor_name', 
        'get_appointment_time', 'booking_status', 'created_at'
    )
    list_filter = (
        'is_canceled', 'created_at', 'updated_at',
        'appointment__week_day', 'appointment__doctor__speciality'
    )
    search_fields = (
        'booking_id', 'patient__user__first_name', 'patient__user__last_name',
        'patient__user__email', 'appointment__doctor__user__first_name',
        'appointment__doctor__user__last_name', 'reason'
    )
    readonly_fields = ('booking_id', 'created_at', 'updated_at', 'canceled_at')
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_id', 'appointment', 'patient')
        }),
        ('Details', {
            'fields': ('reason',)
        }),
        ('Status', {
            'fields': ('is_canceled', 'canceled_at', 'cancellation_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "appointment":
            # Only show appointments that don't have active bookings
            kwargs["queryset"] = Appointment.objects.filter(
                Q(bookings__isnull=True) | Q(bookings__is_canceled=True)
            ).distinct()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name()
    get_patient_name.short_description = 'Patient'
    get_patient_name.admin_order_field = 'patient__user__first_name'
    
    def get_doctor_name(self, obj):
        return f"Dr. {obj.appointment.doctor.user.get_full_name()}"
    get_doctor_name.short_description = 'Doctor'
    get_doctor_name.admin_order_field = 'appointment__doctor__user__first_name'
    
    def get_appointment_time(self, obj):
        return f"{obj.appointment.get_week_day_display()} at {obj.appointment.start_time}"
    get_appointment_time.short_description = 'Appointment Time'
    
    def booking_status(self, obj):
        if obj.is_canceled:
            if obj.canceled_at:
                return f"Canceled ({obj.canceled_at.strftime('%Y-%m-%d %H:%M')})"
            else:
                return "Canceled"
        else:
            return "Active"
    booking_status.short_description = 'Status'
    
    def cancel_booking_action(self, request, queryset):
        canceled_count = 0
        for booking in queryset.filter(is_canceled=False):
            booking.cancel_booking(reason="Canceled by admin")
            canceled_count += 1
        
        self.message_user(
            request, 
            f"{canceled_count} booking(s) canceled successfully."
        )
    cancel_booking_action.short_description = "Cancel selected bookings"
    
    actions = [cancel_booking_action]

    def save_model(self, request, obj, form, change):
        is_new = not change
        was_canceled = False
        
        if change:
            try:
                old_booking = Booking.objects.get(pk=obj.pk)
                was_canceled = not old_booking.is_canceled and obj.is_canceled
            except Booking.DoesNotExist:
                is_new = True
        
        super().save_model(request, obj, form, change)
        
        try:
            if is_new and not obj.is_canceled:
                obj._create_booking_notification()
            elif was_canceled and obj.is_canceled:
                obj._create_cancellation_notification()
        except Exception as e:
            print(f"❌ Error in admin notification creation: {e}")