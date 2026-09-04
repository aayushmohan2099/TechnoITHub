from rest_framework import serializers
from .models import EmployeeProfile, Designation

class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ['id', 'title']


class EmployeeProfileSerializer(serializers.ModelSerializer):
    designation_title = serializers.CharField(source='designation.title', read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = [
            'employee_id', 
            'name', 
            'email', 
            'phone_number', 
            'designation', 
            'designation_title', 
            'created_at', 
            'user_id'
        ]
        read_only_fields = ['employee_id', 'created_at']