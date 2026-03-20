import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from ohmi_audit.main_app.models import Audit


@pytest.mark.django_db
class TestAuditApi:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.list_url = reverse('api-endpoint-example-model')

    def test_get_list_returns_items(self):
        Audit.objects.create(
            name='Audit 1', description='d', date=timezone.now().date(), is_active=True
        )
        resp = self.client.get(self.list_url)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert len(resp.json()) >= 1

    def test_post_valid_payload_returns_201_but_does_not_persist(self):
        payload = {
            'name': 'Api Audit',
            'description': 'via api',
            'date': str(timezone.now().date()),
            'is_active': True,
            'category': 'other',
        }
        resp = self.client.post(self.list_url, payload, format='json')
        assert resp.status_code == 201
        # Serializer.save() is commented; ensure not persisted
        assert not Audit.objects.filter(name='Api Audit').exists()


@pytest.mark.django_db
class TestCustomDataApi:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()
        self.url = reverse('api-endpoint-example-custom-data')

    def test_get_returns_list(self):
        resp = self.client.get(self.url)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        assert 'custom_field' in resp.json()[0]

    def test_post_invalid_returns_400(self):
        resp = self.client.post(self.url, {'custom_field': 'not valid!'}, format='json')
        assert resp.status_code == 400
