from datetime import date

from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User, Patient


def r(name):
    """
    Robust reverse helper: try 'users:name' first, then 'name'.
    Raises NoReverseMatch if neither is found.
    """
    for candidate in (f"users:{name}", name):
        try:
            return reverse(candidate)
        except NoReverseMatch:
            continue
    raise NoReverseMatch(f"No URL found for {name}")


class PatientRegistrationTests(APITestCase):
    def test_patient_registration_creates_user_and_profile(self):
        url = r('patient-register')
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
        url = r('patient-register')
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
        # try canonical token endpoint first, else fallback to 'login'
        try:
            url = reverse('token_obtain_pair')
        except NoReverseMatch:
            url = r('login')
        response = self.client.post(
            url,
            {"email": "patient@example.com", "password": "Str0ngPass!123"},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Accept common token key names to be robust across setups
        self.assertTrue(any(k in response.data for k in ("access", "token", "refresh")))

    def test_profile_requires_authentication(self):
        url = r('my-profile')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patient_profile_returns_full_payload(self):
        access_token = RefreshToken.for_user(self.patient_user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = r('my-profile')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["email"], "patient@example.com")
        self.assertEqual(response.data["user"]["role"], User.PATIENT)


class DoctorListPermissionTests(APITestCase):
    def setUp(self):
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
        access_token = RefreshToken.for_user(self.patient_user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = r('doctor-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_doctor_cannot_list_other_doctors(self):
        access_token = RefreshToken.for_user(self.doctor_user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = r('doctor-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
```# filepath: /home/vuhoangnamdoan/Code/health-appointment-system/users/tests/test_auth_api.py
from datetime import date

from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User, Patient


def r(name):
    """
    Robust reverse helper: try 'users:name' first, then 'name'.
    Raises NoReverseMatch if neither is found.
    """
    for candidate in (f"users:{name}", name):
        try:
            return reverse(candidate)
        except NoReverseMatch:
            continue
    raise NoReverseMatch(f"No URL found for {name}")


class PatientRegistrationTests(APITestCase):
    def test_patient_registration_creates_user_and_profile(self):
        url = r('patient-register')
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
        url = r('patient-register')
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
        # try canonical token endpoint first, else fallback to 'login'
        try:
            url = reverse('token_obtain_pair')
        except NoReverseMatch:
            url = r('login')
        response = self.client.post(
            url,
            {"email": "patient@example.com", "password": "Str0ngPass!123"},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Accept common token key names to be robust across setups
        self.assertTrue(any(k in response.data for k in ("access", "token", "refresh")))

    def test_profile_requires_authentication(self):
        url = r('my-profile')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patient_profile_returns_full_payload(self):
        access_token = RefreshToken.for_user(self.patient_user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = r('my-profile')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["email"], "patient@example.com")
        self.assertEqual(response.data["user"]["role"], User.PATIENT)


class DoctorListPermissionTests(APITestCase):
    def setUp(self):
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
        access_token = RefreshToken.for_user(self.patient_user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = r('doctor-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_doctor_cannot_list_other_doctors(self):
        access_token = RefreshToken.for_user(self.doctor_user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        url = r('doctor-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
