from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Patient, Doctor


class DoctorInline(admin.StackedInline):
    """Inline admin for Doctor profile when editing User"""
    model = Doctor
    can_delete = False
    verbose_name_plural = 'Doctor Profile'
    fk_name = 'user'
    fields = (
        ('speciality', 'experience'),
        'dob',
        ('working_day', 'from_time', 'to_time'),
        'description',
        'is_available'
    )
    extra = 0


class PatientInline(admin.StackedInline):
    """Inline admin for Patient profile when editing User"""
    model = Patient
    can_delete = False
    verbose_name_plural = 'Patient Profile'
    fk_name = 'user'
    fields = (
        ('phone', 'dob'), 'identity_id',
        'address1', 'address2', ('city', 'state', 'zip_code'),
        ('blood_type', 'weight', 'height'),
        'emergency_contact_name', ('emergency_contact_phone', 'emergency_contact_relationship')
    )
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin with role-based profile management"""
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Information'), {
            'fields': (('first_name', 'last_name'), 'role')
        }),
        (_('Permissions'), {
            'fields': (
                ('is_active', 'is_staff', 'is_superuser'),
                'groups',
                'user_permissions',
            ),
        }),
        (_('Important Dates'), {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2',
                ('first_name', 'last_name'),
                'role'
            ),
        }),
    )
    
    list_display = (
        'email', 'get_full_name', 'role', 'is_active',
        'is_staff', 'created_at'
    )
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    
    def get_full_name(self, obj):
        """Display full name"""
        return obj.get_full_name()
    get_full_name.short_description = _('Full Name')
    get_full_name.admin_order_field = 'first_name'
    
    def get_inlines(self, request, obj=None):
        if obj:
            if obj.role == User.DOCTOR:
                return [DoctorInline]
            elif obj.role == User.PATIENT:
                return [PatientInline]
        return []
    
    def get_readonly_fields(self, request, obj=None):
        """Make user_id readonly when editing"""
        readonly = list(self.readonly_fields)
        if obj:
            readonly.append('email')  # Email should not be changed
        return readonly


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """Admin interface for Doctor profiles"""
    list_display = (
        'get_doctor_name', 'speciality', 'experience_years',
        'is_available', 'working_schedule'
    )
    list_filter = ('speciality', 'is_available', 'experience', 'created_at')
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'speciality', 'description'
    )
    ordering = ('-created_at',)
    
    fieldsets = (
        (_('User Information'), {
            'fields': ('user',)
        }),
        (_('Professional Information'), {
            'fields': (('speciality', 'experience'), 'description')
        }),
        (_('Personal Information'), {
            'fields': ('dob',)
        }),
        (_('Working Schedule'), {
            'fields': (
                'working_day',
                ('from_time', 'to_time'),
                'is_available'
            )
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            # Only show users with doctor role who don't already have a doctor profile
            kwargs["queryset"] = User.objects.filter(
                role=User.DOCTOR 
            ).exclude(
                doctor__isnull=False
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_doctor_name(self, obj):
        """Display doctor's full name with title"""
        return f"Dr. {obj.user.get_full_name()}"
    get_doctor_name.short_description = _('Doctor Name')
    get_doctor_name.admin_order_field = 'user__first_name'
    
    def experience_years(self, obj):
        return f"{obj.experience} years"
    experience_years.short_description = _('Experience')
    experience_years.admin_order_field = 'experience'
    
    def working_schedule(self, obj):
        """Display working schedule"""
        try:
            working_days = obj.get_working_days_display()
            from_time = obj.from_time.strftime('%H:%M') if obj.from_time else 'Not set'
            to_time = obj.to_time.strftime('%H:%M') if obj.to_time else 'Not set'
            return f"{working_days}, {from_time} - {to_time}"
        except Exception as e:
            return f"Schedule error: {str(e)}"
    working_schedule.short_description = _('Schedule')
    
    def user_display(self, obj):
        if obj.user:
            return f"{obj.user.get_full_name()} ({obj.user.email})"
        return '-'
    user_display.short_description = _('User Account')


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """Admin interface for Patient profiles"""
    list_display = (
        'get_patient_name', 'age_display', 'identity_id',
        'blood_type', 'emergency_contact_name'
    )
    list_filter = ('blood_type', 'city', 'state', 'created_at')
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'identity_id', 'phone', 'emergency_contact_name'
    )
    ordering = ('-created_at',)
    
    fieldsets = (
        (_('User Information'), {
            'fields': ('user',)
        }),
        (_('Personal Information'), {
            'fields': (('phone', 'dob'), 'identity_id')
        }),
        (_('Address Information'), {
            'fields': (
                'address1', 'address2',
                ('city', 'state', 'zip_code')
            )
        }),
        (_('Medical Information'), {
            'fields': (('blood_type', 'weight', 'height'),)
        }),
        (_('Emergency Contact'), {
            'fields': (
                'emergency_contact_name',
                ('emergency_contact_phone', 'emergency_contact_relationship')
            )
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter User dropdown to only show patient role users without existing patient profiles."""
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(
                role=User.PATIENT
            ).exclude(
                patient__isnull=False
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_patient_name(self, obj):
        """Display patient's full name"""
        return obj.user.get_full_name()
    get_patient_name.short_description = _('Patient Name')
    get_patient_name.admin_order_field = 'user__first_name'
    
    def age_display(self, obj):
        return f"{obj.get_age()} years"
    age_display.short_description = _('Age')
    age_display.admin_order_field = 'dob'
    
    def user_display(self, obj):
        if obj.user:
            return f"{obj.user.get_full_name()} ({obj.user.email})"
        return '-'
    user_display.short_description = _('User Account')


# # Customize admin site headers
# admin.site.site_header = _('Healthcare Appointment System Administration')
# admin.site.site_title = _('Healthcare Admin')
# admin.site.index_title = _('Welcome to Healthcare Administration Portal')
