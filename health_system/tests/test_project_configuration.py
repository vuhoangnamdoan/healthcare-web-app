from django.conf import settings
from django.test import SimpleTestCase
from django.urls import reverse, resolve

from rest_framework_simplejwt.authentication import JWTAuthentication


class ProjectConfigurationTests(SimpleTestCase):
    def test_custom_user_model_is_configured(self):
        self.assertEqual(settings.AUTH_USER_MODEL, 'users.User')

    def test_rest_framework_authentication_includes_jwt(self):
        configured_classes = settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']
        self.assertIn('rest_framework_simplejwt.authentication.JWTAuthentication', configured_classes)

    def test_jwt_token_endpoint_is_registered(self):
        url = reverse('token_obtain_pair')
        self.assertEqual(url, '/api/auth/token/')
        resolver = resolve(url)
        self.assertIsNotNone(resolver.func)

    def test_cors_configuration_allows_localhost(self):
        allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        normalized = [origin.lower() for origin in allowed_origins]
        self.assertIn('http://localhost', normalized)
        self.assertIn('http://127.0.0.1', normalized)

    def test_installed_apps_include_required_components(self):
        installed = set(settings.INSTALLED_APPS)
        self.assertIn('rest_framework', installed)
        self.assertIn('users', installed)
        self.assertIn('appointments', installed)