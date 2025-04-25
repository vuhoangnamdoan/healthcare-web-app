from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django_cryptography.fields import encrypt
import uuid


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

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
        extra_fields.setdefault('role', User.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with email as username and role-based authentication."""
    
    # Define user roles
    PATIENT = 'patient'
    DOCTOR = 'doctor'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (PATIENT, _('Patient')),
        (DOCTOR, _('Doctor')),
        (ADMIN, _('Admin')),
    ]
    
    username = None
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=PATIENT)
    
    # Additional fields with encryption for sensitive data
    phone_number = encrypt(models.CharField(max_length=15, blank=True, null=True))
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Address fields
    address_line1 = encrypt(models.CharField(max_length=255, blank=True, null=True))
    address_line2 = encrypt(models.CharField(max_length=255, blank=True, null=True))
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zipcode = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    def __str__(self):
        return self.email

    def is_patient(self):
        return self.role == self.PATIENT
        
    def is_doctor(self):
        return self.role == self.DOCTOR
        
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser


class DoctorProfile(models.Model):
    """Extended profile for doctors with medical specialization information."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    doctor_id = models.CharField(max_length=50, unique=True, editable=False)
    specialization = models.CharField(max_length=100)
    years_of_experience = models.PositiveIntegerField(default=0)
    
    # Available hours
    available_from = models.TimeField(null=True, blank=True)
    available_to = models.TimeField(null=True, blank=True)
    
    # Working days (comma-separated list of weekdays: 1-7)
    working_days = models.CharField(max_length=20, blank=True, default="1,2,3,4,5")
    
    def save(self, *args, **kwargs):
        if not self.doctor_id:
            self.doctor_id = f"DOC-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.specialization}"


class PatientProfile(models.Model):
    """Extended profile for patients with medical information."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    patient_id = models.CharField(max_length=50, unique=True, editable=False)
    identity_id = models.CharField(max_length=50, blank=True, null=True)
    blood_type = encrypt(models.CharField(max_length=10, blank=True, null=True))
    conditions = encrypt(models.TextField(blank=True))
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Emergency contact information
    emergency_contact_name = encrypt(models.CharField(max_length=100, blank=True))
    emergency_contact_phone = encrypt(models.CharField(max_length=15, blank=True))
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.patient_id:
            self.patient_id = f"PAT-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.email
