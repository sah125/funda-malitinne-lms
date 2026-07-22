from django.test import SimpleTestCase
from django.urls import resolve, reverse


class HealthEndpointTests(SimpleTestCase):
    def test_health_endpoint_is_available(self):
        self.assertEqual(reverse('health_check'), '/health/')
        self.assertEqual(resolve('/health/').view_name, 'health_check')
