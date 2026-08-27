from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter  # 👈 1. Yeh import add karein
from django.shortcuts import get_object_or_404
from .models import Task, DailyTaskUpdate
from .serializers import TaskSerializer, TaskStatusUpdateSerializer, DailyTaskUpdateSerializer
from accounts.permissions import IsAdmin
from audit.utils import log_action 

# ==========================================
# ADMIN VIEWS
# ==========================================

class AdminTaskViewSet(viewsets.ModelViewSet):
    """ Admin creates, assigns and views all tasks. """
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer

    # 👇 2. Admin Task search ke liye yahan filter add kiya gaya hai
    filter_backends = [SearchFilter]
    search_fields = ['title', 'assigned_to__name', 'assigned_to__employee_id'] 
    # (Agar aap chahte hain ki sirf employee ke naam/ID se search ho, toh 'title' hata sakte hain)

    def perform_create(self, serializer):
        task = serializer.save(created_by=self.request.user)
        
        log_action(
            actor=self.request.user,
            action="CREATE_TASK",
            entity_type="Task",
            entity_id=task.id,
            metadata={"title": task.title, "assigned_to": task.assigned_to.employee_id}
        )

class AdminTaskStatusUpdateView(views.APIView):
    """ Moderate task status. """
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        old_status = task.status
        serializer = TaskStatusUpdateSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            log_action(
                actor=request.user,
                action="UPDATE_TASK_STATUS",
                entity_type="Task",
                entity_id=task.id,
                metadata={"old_status": old_status, "new_status": task.status}
            )
            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminWorkLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ Admin views global daily work updates. """
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = DailyTaskUpdate.objects.all().order_by('-created_at')
    serializer_class = DailyTaskUpdateSerializer

    # 👇 3. Work logs (updates) par bhi search lagane ke liye
    filter_backends = [SearchFilter]
    search_fields = ['update_text', 'employee__name', 'task__title']


# ==========================================
# EMPLOYEE VIEWS
# ==========================================

class EmployeeTaskViewSet(viewsets.ReadOnlyModelViewSet):
    """ Employee views own tasks (Strict Data Isolation). """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    # 👇 4. Employee apne tasks me search kar sake (jaise task title se)
    filter_backends = [SearchFilter]
    search_fields = ['title', 'description', 'status']

    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user).order_by('-deadline')

class EmployeeSubmitUpdateView(views.APIView):
    """ Employee submits progress notes against an assigned task. """
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        task = get_object_or_404(Task, pk=task_id, assigned_to=request.user)
        
        serializer = DailyTaskUpdateSerializer(data=request.data)
        if serializer.is_valid():
            update_obj = serializer.save(task=task, employee=request.user)
            
            log_action(
                actor=request.user,
                action="SUBMIT_DAILY_UPDATE",
                entity_type="DailyTaskUpdate",
                entity_id=update_obj.id,
                metadata={"task_id": task.id, "progress": update_obj.progress_percent}
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)