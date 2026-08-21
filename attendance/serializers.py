from rest_framework import serializers
from .models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.name')
    employee_id = serializers.ReadOnlyField(source='employee.employee_id')

    class Meta:
        model = Attendance
        fields = ['id', 'employee_id', 'employee_name', 'attendance_date', 'punch_in', 'punch_out', 'total_seconds']
        read_only_fields = ['attendance_date', 'punch_in', 'punch_out', 'total_seconds']