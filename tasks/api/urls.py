from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tasks.views import (
    AdminTaskViewSet, AdminTaskStatusUpdateView, AdminWorkLogViewSet,
    EmployeeTaskViewSet, EmployeeSubmitUpdateView
)

router = DefaultRouter()
# Admin Routes
router.register(r'admin/manage', AdminTaskViewSet, basename='admin-tasks')
router.register(r'admin/work-logs', AdminWorkLogViewSet, basename='admin-work-logs')
# Employee Routes
router.register(r'employee/my-tasks', EmployeeTaskViewSet, basename='employee-tasks')

urlpatterns = [
    # Router ko include karein
    path('', include(router.urls)),
    
    # Task Status Update API (Admin)
    path('admin/manage/<int:pk>/status/', AdminTaskStatusUpdateView.as_view(), name='admin-task-status'),
    
    # Daily Update Submit API (Employee)
    path('employee/my-tasks/<int:task_id>/update/', EmployeeSubmitUpdateView.as_view(), name='employee-task-update'),
]