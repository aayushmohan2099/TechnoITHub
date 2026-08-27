from rest_framework import serializers
from .models import Task, DailyTaskUpdate
from accounts.models import CustomUser

class DailyTaskUpdateSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.name')
    task_title = serializers.ReadOnlyField(source='task.title')
    
    task_status = serializers.ReadOnlyField(source='task.status')

    class Meta:
        model = DailyTaskUpdate
        fields = '__all__'
        read_only_fields = ['task', 'employee', 'created_at', 'updated_at']

    def create(self, validated_data):
        # 1. Daily update ko database mein save karein
        daily_update = super().create(validated_data)
        
        # 2. Us task ko nikalein jiska update ho raha hai
        task = daily_update.task
        progress = validated_data.get('progress_percent', 0)
        
        # 3. Progress percentage ke hisab se Task ka status automatic update karein
        if progress == 100:
            task.status = "Completed"
        elif 1 <= progress < 100:
            task.status = "In-Progress"  # Model choices ke hisab se hyphen ("In-Progress") rakhein
        else:
            task.status = "Pending"
            
        task.save()
        return daily_update


class TaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.ReadOnlyField(source='assigned_to.name')
    assigned_to_emp_id = serializers.ReadOnlyField(source='assigned_to.employee_id')
    created_by_name = serializers.ReadOnlyField(source='created_by.name')

    # 👇 Yeh naya field add kiya hai taaki task ke sath uske saare updates dikhein
    daily_updates = DailyTaskUpdateSerializer(many=True, read_only=True)

    # Yeh default PrimaryKeyRelatedField hai jo seedha numeric ID accept karega
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