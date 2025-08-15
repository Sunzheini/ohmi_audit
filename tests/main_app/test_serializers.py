from django.test import SimpleTestCase
from django.utils import timezone

from common.serializers import AuditSerializer, CustomDataSerializer


class CustomDataSerializerTests(SimpleTestCase):
    def test_alphanumeric_validation_passes(self):
        serializer = CustomDataSerializer(data={"custom_field": "Abc123"})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_alphanumeric_validation_fails(self):
        serializer = CustomDataSerializer(data={"custom_field": "not valid!"})
        self.assertFalse(serializer.is_valid())
        self.assertIn('custom_field', serializer.errors)


class AuditSerializerTests(SimpleTestCase):
    def test_requires_fields(self):
        serializer = AuditSerializer(data={})
        self.assertFalse(serializer.is_valid())
        # At least name/date required by model
        self.assertTrue('name' in serializer.errors or 'date' in serializer.errors)
