from rest_framework import serializers
from .models import Task, DailyTaskUpdate

class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.ReadOnlyField(source='assigned_to.name')
    assigned_to_emp_id = serializers.ReadOnlyField(source='assigned_to.employee_id')
    created_by_name = serializers.ReadOnlyField(source='created_by.name')

    class Meta:
        model = Task
        fields = '__all__'
        # Status aur created_by Admin APIs handle karengi, isliye inhe read_only rakha hai
        read_only_fields = ['created_by', 'status', 'created_at', 'updated_at']

    def validate(self, data):
        # Deadline validation should prevent invalid dates such as a deadline before the start date[cite: 2].
        if data.get('start_date') and data.get('deadline'):
            if data['deadline'] < data['start_date']:
                raise serializers.ValidationError({"deadline": "Deadline cannot be before the start date."})
        return data

class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['status']

class DailyTaskUpdateSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.name')
    task_title = serializers.ReadOnlyField(source='task.title')

    class Meta:
        model = DailyTaskUpdate
        fields = '__all__'
        # Task aur employee automatically view logic se set honge
        read_only_fields = ['task', 'employee', 'created_at', 'updated_at']