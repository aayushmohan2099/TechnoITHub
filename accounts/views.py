from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.crypto import get_random_string
from .models import CustomUser
from .serializers import EmployeeCreateSerializer
from .permissions import IsAdmin
from audit.utils import log_action  # Audit utility import ki gayi

class AdminCreateEmployeeView(views.APIView):
    # Admin endpoints should use an explicit IsAdmin permission class
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = EmployeeCreateSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            name = serializer.validated_data['name']

            # Duplicate email validation
            if CustomUser.objects.filter(email=email).exists():
                # 409 Conflict: duplicate employee/email[cite: 2]
                return Response({"error": "Email already exists"}, status=status.HTTP_409_CONFLICT)

            # Generate a strong temporary password using a cryptographically secure random generator[cite: 2]
            temporary_password = get_random_string(length=12)

            # Create employee using the CustomUserManager
            user = CustomUser.objects.create_user(
                email=email,
                name=name,
                password=temporary_password
            )

            # ==========================================
            # AUDIT LOGGING YAHAN ADD HOGI
            # ==========================================
            log_action(
                actor=request.user,
                action="CREATE_EMPLOYEE",
                entity_type="CustomUser",
                entity_id=user.id,
                metadata={"employee_id": user.employee_id, "email": user.email}
            )

            # Return credentials (Ideally over HTTPS)[cite: 2]
            return Response({
                "message": "Employee created successfully",
                "employee_id": user.employee_id,
                "temporary_password": temporary_password
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)