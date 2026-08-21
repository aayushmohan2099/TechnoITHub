from django.db import models
from django.conf import settings

class Attendance(models.Model):
    # Relation: One employee can have many attendance records[cite: 2]
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendances')
    
    attendance_date = models.DateField(auto_now_add=True)
    punch_in = models.DateTimeField(auto_now_add=True) # Uses server timestamp[cite: 2]
    punch_out = models.DateTimeField(null=True, blank=True)
    
    # Store duration in seconds/minutes[cite: 2]
    total_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.employee_id} - {self.attendance_date}"