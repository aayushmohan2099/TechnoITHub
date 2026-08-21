from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Task, DailyTaskUpdate
from .serializers import TaskSerializer, TaskStatusUpdateSerializer, DailyTaskUpdateSerializer
from accounts.permissions import IsAdmin
from audit.utils import log_action  # Audit utility import ki gayi

# ==========================================
# ADMIN VIEWS
# ==========================================

class AdminTaskViewSet(viewsets.ModelViewSet):
    """ Admin creates, assigns and views all tasks. """
    permission_classes = [IsAuthenticated, IsAdmin] # Explicit IsAdmin permission[cite: 2]
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer

    def perform_create(self, serializer):
        # Admin jo task bana raha hai, uska record rakhna
        task = serializer.save(created_by=self.request.user)
        
        # Audit Log for Task Creation[cite: 2]
        log_action(
            actor=self.request.user,
            action="CREATE_TASK",
            entity_type="Task",
            entity_id=task.id,
            metadata={"title": task.title, "assigned_to": task.assigned_to.employee_id}
        )

class AdminTaskStatusUpdateView(views.APIView):
    """ Moderate task status[cite: 2]. """
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        old_status = task.status
        serializer = TaskStatusUpdateSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # Audit Log for Task Status Change[cite: 2]
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
    """ Admin views global daily work updates[cite: 2]. """
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = DailyTaskUpdate.objects.all().order_by('-created_at')
    serializer_class = DailyTaskUpdateSerializer


# ==========================================
# EMPLOYEE VIEWS
# ==========================================

class EmployeeTaskViewSet(viewsets.ReadOnlyModelViewSet):
    """ Employee views own tasks (Strict Data Isolation)[cite: 2]. """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        # Query Task objects using the authenticated employee relationship[cite: 2]
        return Task.objects.filter(assigned_to=self.request.user).order_by('-deadline')

class EmployeeSubmitUpdateView(views.APIView):
    """ Employee submits progress notes against an assigned task[cite: 2]. """
    permission_classes = [IsAuthenticated]

    def post(self, request, task_id):
        # Verify both task ID and assigned employee before creating the update[cite: 2].
        task = get_object_or_404(Task, pk=task_id, assigned_to=request.user)
        
        serializer = DailyTaskUpdateSerializer(data=request.data)
        if serializer.is_valid():
            update_obj = serializer.save(task=task, employee=request.user)
            
            # Audit Log for Daily Update Submission[cite: 2]
            log_action(
                actor=request.user,
                action="SUBMIT_DAILY_UPDATE",
                entity_type="DailyTaskUpdate",
                entity_id=update_obj.id,
                metadata={"task_id": task.id, "progress": update_obj.progress_percent}
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)