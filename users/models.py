import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    """Custom user manager for User model with no username field."""
    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Base user model for authentication - supports patients, doctors, and admins"""
    # User roles
    PATIENT = 'patient'
    DOCTOR = 'doctor'
    
    USER_ROLE_CHOICES = [
        (PATIENT, _('Patient')),
        (DOCTOR, _('Doctor')),
    ]
    
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=USER_ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']
    
    objects = UserManager()
    
    def has_role(self, role):
        return self.role == role
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.first_name
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.get_role_display()})"
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]


class Patient(models.Model):
    """Patient profile extending User"""
    BLOOD_TYPES = [
        ('A', 'A'),
        ('B', 'B'),
        ('AB', 'AB'),
        ('O', 'O'),
        ('R', 'R'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    dob = models.DateField(verbose_name=_('Date of Birth'))
    address1 = models.CharField(max_length=255, verbose_name=_('Primary Address'))
    address2 = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Secondary Address'))
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    identity_id = models.CharField(max_length=50, unique=True, verbose_name=_('Identity ID'))
    
    # Medical information
    blood_type = models.CharField(max_length=2, choices=BLOOD_TYPES, blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name=_('Weight (kg)'))
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name=_('Height (cm)'))
    
    # Emergency contact
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Patient: {self.user.first_name} {self.user.last_name}"
    
    def get_age(self):
        from datetime import date
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
    
    class Meta:
        verbose_name = _('Patient')
        verbose_name_plural = _('Patients')
        indexes = [
            models.Index(fields=['identity_id']),
            models.Index(fields=['dob']),
        ]


class Doctor(models.Model):
    """Doctor profile extending User"""
    SPECIALITIES = [
        ('Mental', _('Mental Health')),
        ('General', _('General Medicine')),
        ('Density', _('Dentistry')),
        ('Physiotherapy', _('Physiotherapy')),
        ('Chiropractic', _('Chiropractic')),
        ('Audiology', _('Audiology')),
        ('Optometry', _('Optometry')),
    ]
    
    DAYS_OF_WEEK = [
        (1, _('Monday')),
        (2, _('Tuesday')),
        (3, _('Wednesday')),
        (4, _('Thursday')),
        (5, _('Friday')),
        (6, _('Saturday')),
        (7, _('Sunday')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    speciality = models.CharField(max_length=50, choices=SPECIALITIES)
    dob = models.DateField(verbose_name=_('Date of Birth'))
    experience = models.PositiveIntegerField(verbose_name=_('Years of Experience'))
    
    # Working schedule
    working_day = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Enter working days as numbers (1-7): 1=Monday, 2=Tuesday, etc. Example: 1,2,4,6"),
        verbose_name=_('Working Days')
    )
    from_time = models.TimeField(verbose_name=_('Working hours from'))
    to_time = models.TimeField(verbose_name=_('Working hours to'))
    
    description = models.TextField(verbose_name=_('Professional Description'))
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name} - {self.get_speciality_display()}"
    
    def get_working_days_display(self):
        if not self.working_day or not self.working_day.strip():
            return str(_('No working days set'))
        
        day_names = dict(self.DAYS_OF_WEEK)
        
        try:
            working_days = [int(day.strip()) for day in self.working_day.split(',') if day.strip().isdigit()]
            
            if not working_days:
                return str(_('No working days set'))
            
            # Convert translation proxies to strings and join
            day_strings = []
            for day in sorted(working_days):  # Sort for consistent display
                if day in day_names:
                    day_strings.append(str(day_names[day]))
            
            return ', '.join(day_strings) if day_strings else str(_('No working days set'))
            
        except (ValueError, TypeError):
            return str(_('Invalid working day format'))
    
    def is_working_today(self):
        if not self.working_day:
            return False
        try:
            today = datetime.now().isoweekday()
            working_days = [int(day.strip()) for day in self.working_day.split(',') if day.strip().isdigit()]
            return today in working_days
        except (ValueError, TypeError):
            return False
        
    def get_working_days_list(self):
        if not self.working_day:
            return []
        
        try:
            return [int(day.strip()) for day in self.working_day.split(',') if day.strip().isdigit()]
        except (ValueError, TypeError):
            return []
    
    def clean(self):
        """Validate working_day format"""
        if self.working_day:
            try:
                days = [int(day.strip()) for day in self.working_day.split(',') if day.strip()]
                # Check if all days are valid (1-7)
                invalid_days = [day for day in days if day < 1 or day > 7]
                if invalid_days:
                    raise ValidationError({
                        'working_day': _('Invalid day numbers: {}. Use 1-7 only.').format(', '.join(map(str, invalid_days)))
                    })
            except ValueError:
                raise ValidationError({
                    'working_day': _('Invalid format. Use comma-separated numbers like: 1,2,4,6')
                })

    class Meta:
        verbose_name = _('Doctor')
        verbose_name_plural = _('Doctors')
        ordering = ['user__first_name', 'user__last_name']
        indexes = [
            models.Index(fields=['speciality']),
            models.Index(fields=['is_available']),
        ]
