from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from ohmi_audit.main_app.models import Audit


class AuditApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse('api-endpoint-example-model')

    def test_get_list_returns_items(self):
        Audit.objects.create(
            name='Audit 1', description='d', date=timezone.now().date(), is_active=True
        )
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)
        self.assertGreaterEqual(len(resp.json()), 1)

    def test_post_valid_payload_returns_201_but_does_not_persist(self):
        payload = {
            'name': 'Api Audit',
            'description': 'via api',
            'date': str(timezone.now().date()),
            'is_active': True,
            'category': 'other',
        }
        resp = self.client.post(self.list_url, payload, format='json')
        self.assertEqual(resp.status_code, 201)
        # Serializer.save() is commented; ensure not persisted
        self.assertFalse(Audit.objects.filter(name='Api Audit').exists())


class CustomDataApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('api-endpoint-example-custom-data')

    def test_get_returns_list(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)
        self.assertIn('custom_field', resp.json()[0])

    def test_post_invalid_returns_400(self):
        resp = self.client.post(self.url, {'custom_field': 'not valid!'}, format='json')
        self.assertEqual(resp.status_code, 400)
