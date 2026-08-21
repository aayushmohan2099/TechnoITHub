from django.urls import path, include
from rest_framework.routers import DefaultRouter
from attendance.views import EmployeePunchAPIView, EmployeeAttendanceViewSet, AdminAttendanceViewSet

router = DefaultRouter()
# Employee aur Admin ke Get/List views ke liye router
router.register(r'employee/history', EmployeeAttendanceViewSet, basename='employee-history')
router.register(r'admin/history', AdminAttendanceViewSet, basename='admin-history')

urlpatterns = [
    # API for Punch-in / Punch-out[cite: 2]
    path('employee/punch/', EmployeePunchAPIView.as_view(), name='employee-punch'),
    
    # Router include for lists
    path('', include(router.urls)),
]