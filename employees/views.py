from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter
from accounts.permissions import IsAdmin
from .models import EmployeeProfile, Designation
from .serializers import EmployeeProfileSerializer, DesignationSerializer

class DesignationViewSet(viewsets.ModelViewSet):
    """ Pure database-backed designations API (Frontend dropdown ke liye) """
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = Designation.objects.all().order_by('id')
    serializer_class = DesignationSerializer


class EmployeeProfileViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = EmployeeProfile.objects.all().order_by('-created_at')
    serializer_class = EmployeeProfileSerializer
    lookup_field = 'user'  
    filter_backends = [SearchFilter]
    search_fields = ['name', 'employee_id', 'designation__title']

    def perform_update(self, serializer):
        profile = serializer.save()
        user = profile.user
        if profile.name:
            user.name = profile.name
        if profile.email:
            user.email = profile.email
        user.save()

    def perform_destroy(self, instance):
        user = instance.user  
        user.delete()