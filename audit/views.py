from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdmin
from .models import AuditLog
from rest_framework import serializers

class AuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.ReadOnlyField(source='actor.name')
    class Meta:
        model = AuditLog
        fields = '__all__'

class AdminAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ View global audit logs[cite: 2] """
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = AuditLog.objects.all().order_by('-created_at')
    serializer_class = AuditLogSerializer