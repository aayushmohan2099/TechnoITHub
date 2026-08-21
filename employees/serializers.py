from rest_framework import serializers
from .models import EmployeeProfile

class EmployeeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeProfile
        fields = ['id', 'employee_id', 'name', 'email', 'department', 'designation', 'created_at']
        read_only_fields = ['employee_id', 'created_at']
        