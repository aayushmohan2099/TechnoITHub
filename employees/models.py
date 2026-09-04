from django.db import models
from django.conf import settings

class Designation(models.Model):
    title = models.CharField(max_length=100, unique=True) # Duplicate names allowed nahi hain
    
    def __str__(self):
        return self.title


class EmployeeProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # ForeignKey relation taaki ek designation multiple employees ko assign ho sake
    designation = models.ForeignKey(
        Designation, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='employees'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.employee_id})"