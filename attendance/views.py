from rest_framework import views, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Attendance
from .serializers import AttendanceSerializer
from accounts.permissions import IsAdmin

class EmployeePunchAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        open_record = Attendance.objects.filter(employee=user, punch_out__isnull=True).first()

        if open_record:
            open_record.punch_out = timezone.now()
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
    """ Return own attendance for Employee with Date Filter """
    permission_classes = [IsAuthenticated]
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        queryset = Attendance.objects.filter(employee=self.request.user)
        
        # 📅 Date Filter Query Parameter: ?date=2026-08-27
        date_param = self.request.query_params.get('date')
        if date_param:
            queryset = queryset.filter(attendance_date=date_param)
            
        return queryset.order_by('-attendance_date', '-punch_in')


class AdminAttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    """ Global attendance report for Admin with Date Filter """
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        queryset = Attendance.objects.all()
        
        # 📅 Date Filter Query Parameter: ?date=2026-08-27
        date_param = self.request.query_params.get('date')
        if date_param:
            queryset = queryset.filter(attendance_date=date_param)
            
        return queryset.order_by('-attendance_date', '-punch_in')