from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter  
from rest_framework.decorators import action  
from django.utils import timezone  
from django.shortcuts import get_object_or_404
from .models import Task, DailyTaskUpdate
from .serializers import TaskSerializer, TaskStatusUpdateSerializer, DailyTaskUpdateSerializer
from accounts.permissions import IsAdmin
from audit.utils import log_action 

# ==========================================
# ADMIN VIEWS
# ==========================================

class AdminTaskViewSet(viewsets.ModelViewSet):
    """ Admin creates, assigns, views, updates and deletes tasks with filters, ordering & overdue check. """
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = TaskSerializer
    
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'assigned_to__name', 'assigned_to__employee_id', 'priority'] 
    
    # Sorting fields (e.g., ?ordering=created_at or ?ordering=-created_at or ?ordering=deadline)
    ordering_fields = ['created_at', 'deadline', 'priority']
    ordering = ['-created_at'] # Default: Newest first

    def get_queryset(self):
        queryset = Task.objects.all()
        
        # Date Filter
        date_param = self.request.query_params.get('date')
        if date_param:
            queryset = queryset.filter(created_at__date=date_param)
            
        # Status Filter
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Priority Filter
        priority_param = self.request.query_params.get('priority')
        if priority_param:
            queryset = queryset.filter(priority=priority_param)
            
        return queryset

    @action(detail=False, methods=['get'], url_path='overdue-tasks')
    def overdue_tasks(self, request):
        """ 
        Yeh endpoint un tasks ko dhoondhega jinki deadline nikal chuki hai 
        aur status abhi bhi 'Completed' nahi hua hai (Admin Dashboard ke liye).
        """
        today = timezone.now().date()
        
        # Deadline aaj se pehle ki ho aur status Completed na ho
        overdue_qs = self.get_queryset().exclude(status='Completed').filter(deadline__lt=today)
        
        serializer = self.get_serializer(overdue_qs, many=True)
        return Response({
            "count": overdue_qs.count(),
            "overdue_tasks": serializer.data
        }, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        task = serializer.save(created_by=self.request.user)
        log_action(
            actor=self.request.user,
            action="CREATE_TASK",
            entity_type="Task",
            entity_id=task.id,
            metadata={"title": task.title, "assigned_to": task.assigned_to.employee_id}
        )

    def perform_update(self, serializer):
        task = serializer.save()
        log_action(
            actor=self.request.user,
            action="UPDATE_TASK",
            entity_type="Task",
            entity_id=task.id,
            metadata={"title": task.title, "status": task.status}
        )

    def perform_destroy(self, instance):
        task_id = instance.id
        task_title = instance.title
        instance.delete()
        log_action(
            actor=self.request.user,
            action="DELETE_TASK",
            entity_type="Task",
            entity_id=task_id,
            metadata={"title": task_title}
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
    """ Admin views global daily work updates with Search & Date Filter. """
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = DailyTaskUpdateSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['update_text', 'employee__name', 'task__title']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = DailyTaskUpdate.objects.all()
        date_param = self.request.query_params.get('date')
        if date_param:
            queryset = queryset.filter(created_at__date=date_param)
        return queryset


# ==========================================
# EMPLOYEE VIEWS
# ==========================================

class EmployeeTaskViewSet(viewsets.ReadOnlyModelViewSet):
    """ Employee views own tasks with Search, Date, Status, Priority & Ordering Filter. """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'description', 'status', 'priority']
    ordering_fields = ['deadline', 'created_at', 'priority']
    ordering = ['-deadline']

    def get_queryset(self):
        queryset = Task.objects.filter(assigned_to=self.request.user)
        
        date_param = self.request.query_params.get('date')
        if date_param:
            queryset = queryset.filter(created_at__date=date_param)
            
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        priority_param = self.request.query_params.get('priority')
        if priority_param:
            queryset = queryset.filter(priority=priority_param)
            
        return queryset

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