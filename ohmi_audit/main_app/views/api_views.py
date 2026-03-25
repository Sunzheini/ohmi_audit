"""
API endpoint views.
Contains REST API views for CRUD operations on models and custom data endpoints.
"""
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.serializers import AuditSerializer, CustomDataSerializer
from ohmi_audit.main_app.models import Audit


class ModelEndPointView(APIView):
    """
    Full CRUD API endpoint for Audit model.
    """
    # permission_classes = [AllowAny]  # Or IsAuthenticated

    def get(self, request, *args, **kwargs):
        audits = Audit.objects.all()
        serializer = AuditSerializer(audits, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to create a new Audit object.
        """
        serializer = AuditSerializer(data=request.data)
        if serializer.is_valid():
            # serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PUT (Update full object)
    def put(self, request, pk, *args, **kwargs):
        audit = get_object_or_404(Audit, pk=pk)
        serializer = AuditSerializer(audit, data=request.data)
        if serializer.is_valid():
            # serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PATCH (Partial update)
    def patch(self, request, pk, *args, **kwargs):
        audit = get_object_or_404(Audit, pk=pk)
        serializer = AuditSerializer(audit, data=request.data, partial=True)
        if serializer.is_valid():
            # serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        audit = get_object_or_404(Audit, pk=pk)
        # audit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomDataEndPointView(APIView):
    """
    A simple API view that returns a JSON response with a message.
    This can be for the frontend / Postman to send a get request to.
    """
    permission_classes = [AllowAny]  # Or IsAuthenticated

    def get(self, request, *args, **kwargs):
        data = [
            {
                'custom_field': '1234567'
            }
        ]
        serializer = CustomDataSerializer(data, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to create a new custom data object.
        """
        serializer = CustomDataSerializer(data=request.data)
        if serializer.is_valid():
            # Here you can handle the creation logic if needed
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

