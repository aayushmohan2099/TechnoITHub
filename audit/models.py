from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    # Columns directly from PDF Recommended Database Design
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=100) # e.g., 'Employee', 'Task'
    entity_id = models.CharField(max_length=50)
    metadata = models.JSONField(null=True, blank=True) # JSON store karne ke liye
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.actor} - {self.action} on {self.entity_type} ({self.entity_id})"