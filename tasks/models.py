from django.db import models
from django.conf import settings

class Task(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('In-Progress', 'In-Progress'),
        ('Completed', 'Completed'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Relation: Assigned to an employee, Created by an admin[cite: 2]
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assigned_tasks')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    
    start_date = models.DateField()
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    priority = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class DailyTaskUpdate(models.Model):
    # Daily updates should be linked to the task and employee[cite: 2]
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='daily_updates')
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    update_text = models.TextField()
    progress_percent = models.PositiveIntegerField(default=0, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Update on {self.task.title} by {self.employee.employee_id}"