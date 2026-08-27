from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter  
from accounts.permissions import IsAdmin
from .models import EmployeeProfile
from .serializers import EmployeeProfileSerializer

class EmployeeProfileViewSet(viewsets.ModelViewSet):
    """ Admin can view and manage employee profiles """
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = EmployeeProfile.objects.all().order_by('-created_at')
    serializer_class = EmployeeProfileSerializer
    
    
    filter_backends = [SearchFilter]
    search_fields = ['name', 'employee_id', 'designation']