from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from users.models import User, Patient


class PatientRegistrationTests(APITestCase):
    def test_patient_registration_creates_user_and_profile(self):
        url = reverse('users:patient-register')
        payload = {
            "email": "new.patient@example.com",
            "password": "Str0ngPass!123",
            "password2": "Str0ngPass!123",
            "first_name": "New",
            "last_name": "Patient",
            "phone": "0400000000",
            "dob": "1995-05-05",
            "address1": "123 Health St",
            "address2": "",
            "city": "Melbourne",
            "state": "VIC",
            "zip_code": "3000",
            "identity_id": "ID-10001"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=payload["email"]).exists())
        created_user = User.objects.get(email=payload["email"])
        self.assertTrue(Patient.objects.filter(user=created_user).exists())

    def test_registration_rejects_password_mismatch(self):
        url = reverse('users:patient-register')
        payload = {
            "email": "bad.patient@example.com",
            "password": "Mismatch123!",
            "password2": "Mismatch321!",
            "first_name": "Bad",
            "last_name": "Mismatch",
            "phone": "0400000001",
            "dob": "1990-01-01",
            "address1": "1 Error Road",
            "address2": "",
            "city": "Sydney",
            "state": "NSW",
            "zip_code": "2000",
            "identity_id": "ID-10002"
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)


class AuthenticatedUserTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.patient_user = User.objects.create_user(
            email="patient@example.com",
            password="Str0ngPass!123",
            first_name="Pat",
            last_name="Ient",
            role=User.PATIENT,
        )
        Patient.objects.create(
            user=self.patient_user,
            phone="0400000002",
            dob=date(1992, 2, 2),
            address1="2 Wellness Ave",
            address2="",
            city="Brisbane",
            state="QLD",
            zip_code="4000",
            identity_id="ID-20001",
        )

    def test_login_returns_jwt_tokens(self):
        # Use canonical token endpoint name (pytest-django/setup may expose it)
        url = reverse('token_obtain_pair')
        response = self.client.post(
            url,
            {"email": "patient@example.com", "password": "Str0ngPass!123"},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # tokens may vary by implementation; check for common keys
        self.assertTrue(any(k in response.data for k in ("access", "token", "refresh")))

    def test_profile_requires_authentication(self):
        url = reverse('users:my-profile')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patient_profile_returns_full_payload(self):
        # authenticate via force_authenticate to avoid token issuance issues in CI
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('users:my-profile')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["email"], "patient@example.com")
        self.assertEqual(response.data["user"]["role"], User.PATIENT)
        self.client.force_authenticate(user=None)


class DoctorListPermissionTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.patient_user = User.objects.create_user(
            email="patient2@example.com",
            password="Str0ngPass!123",
            first_name="Another",
            last_name="Patient",
            role=User.PATIENT,
        )
        Patient.objects.create(
            user=self.patient_user,
            phone="0400000003",
            dob=date(1993, 3, 3),
            address1="3 Care Blvd",
            address2="",
            city="Perth",
            state="WA",
            zip_code="6000",
            identity_id="ID-30001",
        )
        self.doctor_user = User.objects.create_user(
            email="doctor@example.com",
            password="Str0ngPass!123",
            first_name="Doc",
            last_name="Tor",
            role=User.DOCTOR,
        )
        from users.models import Doctor
        Doctor.objects.create(
            user=self.doctor_user,
            speciality="General",
            dob=date(1980, 4, 4),
            experience=10,
            working_day="1,2,3,4,5",
            from_time="09:00",
            to_time="17:00",
            description="General practitioner",
            is_available=True,
        )

    def test_patient_can_list_doctors(self):
        self.client.force_authenticate(user=self.patient_user)
        url = reverse('users:doctor-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        self.client.force_authenticate(user=None)

    def test_doctor_cannot_list_other_doctors(self):
        self.client.force_authenticate(user=self.doctor_user)
        url = reverse('users:doctor-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=None)
