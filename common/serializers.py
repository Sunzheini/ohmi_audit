from rest_framework import serializers
from ohmi_audit.main_app.models import *


# example for a model serializer
class AuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audit
        fields = '__all__'




# example for a serializer with custom fields
class CustomDataSerializer(serializers.Serializer):
    custom_field = serializers.CharField(max_length=100, required=True)

    def validate(self, data):
        """
        Custom validation logic that can involve multiple fields.
        This method is called after individual field validations.
        """
        if 'custom_field' in data and not data['custom_field'].isalnum():
            raise serializers.ValidationError("Custom field must be alphanumeric.")
        return data

    def create(self, validated_data):
        # Custom create logic can go here
        return validated_data

    def update(self, instance, validated_data):
        # Custom update logic can go here
        instance.custom_field = validated_data.get('custom_field', instance.custom_field)
        return instance
