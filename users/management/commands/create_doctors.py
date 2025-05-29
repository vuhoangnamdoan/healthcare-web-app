# Create: users/management/commands/create_doctors.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Doctor
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Create initial doctors for the system'

    def handle(self, *args, **options):
        doctors_data = [
            {
                'email': 'dr.smith@hospital.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'password': os.getenv('DOCTOR_DEFAULT_PASSWORD', 'test123pass!'),
                'speciality': 'General',
                'dob': '1980-01-15',
                'experience': 10,
                'working_day': '1,2,3,4,5',
                'from_time': '09:00:00',
                'to_time': '17:00:00',
                'description': 'Experienced general practitioner'
            },
            {
                'email': 'dr.johnson@hospital.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'password': os.getenv('DOCTOR_DEFAULT_PASSWORD', 'test123pass!'),
                'speciality': 'Mental',
                'dob': '1975-05-20',
                'experience': 15,
                'working_day': '1,2,3,4,5',
                'from_time': '10:00:00',
                'to_time': '18:00:00',
                'description': 'Mental health specialist'
            }
        ]

        for doctor_data in doctors_data:
            # Create user
            user, created = User.objects.get_or_create(
                email=doctor_data['email'],
                defaults={
                    'first_name': doctor_data['first_name'],
                    'last_name': doctor_data['last_name'],
                    'role': 'doctor'
                }
            )
            
            if created:
                user.set_password(doctor_data['password'])
                user.save()
                
                # Create doctor profile
                Doctor.objects.create(
                    user=user,
                    speciality=doctor_data['speciality'],
                    dob=doctor_data['dob'],
                    experience=doctor_data['experience'],
                    working_day=doctor_data['working_day'],
                    from_time=doctor_data['from_time'],
                    to_time=doctor_data['to_time'],
                    description=doctor_data['description']
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Created doctor: {user.get_full_name()}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Doctor already exists: {user.get_full_name()}')
                )