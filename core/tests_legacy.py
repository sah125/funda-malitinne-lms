from datetime import date
from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase
from django.urls import resolve, reverse

from .views import register


class HealthEndpointTests(SimpleTestCase):
    def test_health_endpoint_is_available(self):
        self.assertEqual(reverse('health_check'), '/health/')
        self.assertEqual(resolve('/health/').view_name, 'health_check')


class RegistrationFieldsTests(SimpleTestCase):
    @patch('core.views.User')
    @patch('core.views.messages.success')
    def test_registration_persists_user_profile_fields(self, success_message, user_model):
        user = user_model.objects.create_user.return_value
        user_model.objects.filter.return_value.exists.return_value = False

        request = RequestFactory().post(reverse('register'), {
            'username': 'registration-test',
            'email': 'registration@example.com',
            'password': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
            'full_name': 'Test Learner',
            'id_number': '9001010000000',
            'date_of_birth': '1990-01-01',
            'gender': 'female',
            'nationality': 'South African',
            'contact_number': '0712345678',
            'disability': 'None',
            'preferred_language': 'English',
        })
        response = register(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('login'))
        self.assertEqual(
            user_model.objects.create_user.call_args.kwargs['username'],
            'registration-test',
        )
        self.assertEqual(user.id_number, '9001010000000')
        self.assertEqual(user.date_of_birth, date(1990, 1, 1))
        self.assertEqual(user.gender, 'female')
        self.assertEqual(user.nationality, 'South African')
        self.assertEqual(user.contact_number, '0712345678')
        self.assertEqual(user.disability, 'None')
        self.assertEqual(user.preferred_language, 'English')