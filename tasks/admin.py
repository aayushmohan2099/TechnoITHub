from django.contrib import admin
from .models import Task, DailyTaskUpdate

admin.site.register(Task)
admin.site.register(DailyTaskUpdate)