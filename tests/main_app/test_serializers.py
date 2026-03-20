import pytest
from django.utils import timezone

from common.serializers import AuditSerializer, CustomDataSerializer


class TestCustomDataSerializer:
    def test_alphanumeric_validation_passes(self):
        serializer = CustomDataSerializer(data={"custom_field": "Abc123"})
        assert serializer.is_valid(), serializer.errors

    def test_alphanumeric_validation_fails(self):
        serializer = CustomDataSerializer(data={"custom_field": "not valid!"})
        assert not serializer.is_valid()
        assert 'custom_field' in serializer.errors


class TestAuditSerializer:
    def test_requires_fields(self):
        serializer = AuditSerializer(data={})
        assert not serializer.is_valid()
        # At least name/date required by model
        assert 'name' in serializer.errors or 'date' in serializer.errors
