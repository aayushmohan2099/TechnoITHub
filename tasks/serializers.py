from rest_framework import serializers
from .models import Task, DailyTaskUpdate
from accounts.models import CustomUser

class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.ReadOnlyField(source='assigned_to.name')
    assigned_to_emp_id = serializers.ReadOnlyField(source='assigned_to.employee_id')
    created_by_name = serializers.ReadOnlyField(source='created_by.name')

    # 👇 Yeh default PrimaryKeyRelatedField hai jo seedha numeric ID (jaise 19) accept karega
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all()
    )

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_by', 'status', 'created_at', 'updated_at']

    def validate(self, data):
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
        read_only_fields = ['task', 'employee', 'created_at', 'updated_at']