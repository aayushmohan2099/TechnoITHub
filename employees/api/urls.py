from django.urls import path, include
from rest_framework.routers import DefaultRouter
from employees.views import EmployeeProfileViewSet, DesignationViewSet

router = DefaultRouter()
router.register(r'profiles', EmployeeProfileViewSet, basename='employee-profiles')
router.register(r'designations', DesignationViewSet, basename='designations')

urlpatterns = [
    path('', include(router.urls)),
]