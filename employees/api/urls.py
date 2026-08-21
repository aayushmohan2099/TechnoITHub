from django.urls import path, include
from rest_framework.routers import DefaultRouter
from employees.views import EmployeeProfileViewSet

router = DefaultRouter()
router.register(r'profiles', EmployeeProfileViewSet, basename='employee-profiles')

urlpatterns = [
    path('', include(router.urls)),
]