from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.crypto import get_random_string
from .models import CustomUser
from .serializers import EmployeeCreateSerializer
from .permissions import IsAdmin
from audit.utils import log_action  # Audit utility import ki gayi
from employees.models import EmployeeProfile  # Employee profile model import


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
                # 409 Conflict: duplicate employee/email
                return Response({"error": "Email already exists"}, status=status.HTTP_409_CONFLICT)

            # Generate a strong temporary password using a cryptographically secure random generator
            temporary_password = get_random_string(length=12)

            # 1. Create employee using the CustomUserManager
            user = CustomUser.objects.create_user(
                email=email,
                name=name,
                password=temporary_password
            )

            # Optional fields request se lena
            phone_number = request.data.get('phone_number', None)
            designation = request.data.get('designation', None)

            # 2. AUTOMATICALLY CREATE EMPLOYEE PROFILE
            EmployeeProfile.objects.create(
                user=user,
                employee_id=user.employee_id,
                name=user.name,
                email=user.email,
                phone_number=phone_number,
                designation=designation
            )

            # ==========================================
            # AUDIT LOGGING
            # ==========================================
            log_action(
                actor=request.user,
                action="CREATE_EMPLOYEE",
                entity_type="CustomUser",
                entity_id=user.id,
                metadata={"employee_id": user.employee_id, "email": user.email}
            )

            # Return credentials
            return Response({
                "message": "Employee created successfully",
                "employee_id": user.employee_id,
                "temporary_password": temporary_password
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminResetPasswordView(views.APIView):
    # Sirf authenticated admin hi password reset kar sakta hai
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        employee_id = request.data.get('employee_id')
        
        if not employee_id:
            return Response({"error": "employee_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(employee_id=employee_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

        # Naya temporary password generate karna
        new_temporary_password = get_random_string(length=12)
        
        # Django ka built-in method use karke password hash karke save karna
        user.set_password(new_temporary_password)
        user.save()

        # Audit Log record karna
        log_action(
            actor=request.user,
            action="RESET_PASSWORD",
            entity_type="CustomUser",
            entity_id=user.id,
            metadata={"employee_id": user.employee_id}
        )

        return Response({
            "message": "Password reset successfully by admin",
            "employee_id": user.employee_id,
            "new_temporary_password": new_temporary_password
        }, status=status.HTTP_200_OK)