from rest_framework import views, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Attendance
from .serializers import AttendanceSerializer
from accounts.permissions import IsAdmin # Admin permission import kiya

class EmployeePunchAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        
        # Check whether an open attendance record already exists (Punch-out missing)[cite: 2]
        open_record = Attendance.objects.filter(employee=user, punch_out__isnull=True).first()

        if open_record:
            # ========================
            # PUNCH-OUT FLOW[cite: 2]
            # ========================
            open_record.punch_out = timezone.now() # Use server timestamp[cite: 2]
            
            # Calculate duration in seconds[cite: 2]
            duration = open_record.punch_out - open_record.punch_in
            open_record.total_seconds = int(duration.total_seconds())
            open_record.save()

            return Response({
                "message": "Punched out successfully",
                "punch_in_time": open_record.punch_in,
                "punch_out_time": open_record.punch_out,
                "total_seconds": open_record.total_seconds
            }, status=status.HTTP_200_OK)
        else:
            # ========================
            # PUNCH-IN FLOW[cite: 2]
            # ========================
            # Create today's attendance record with server timestamp[cite: 2]
            new_record = Attendance.objects.create(
                employee=user,
                punch_in=timezone.now()
            )
            return Response({
                "message": "Punched in successfully",
                "punch_in_time": new_record.punch_in,
                "status": "Currently Working"
            }, status=status.HTTP_201_CREATED)


class EmployeeAttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    """ Return own attendance for Employee[cite: 2] """
    permission_classes = [IsAuthenticated]
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        # Strict Data Isolation: Fetch records through the authenticated employee relationship[cite: 2]
        return Attendance.objects.filter(employee=self.request.user).order_by('-attendance_date', '-punch_in')


class AdminAttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    """ Global attendance report for Admin[cite: 2] """
    # Explicit IsAdmin permission class[cite: 2]
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = AttendanceSerializer
    queryset = Attendance.objects.all().order_by('-attendance_date', '-punch_in')