from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils.crypto import get_random_string
from .models import CustomUser
from .serializers import EmployeeCreateSerializer, CustomTokenObtainPairSerializer
from .permissions import IsAdmin
from audit.utils import log_action  # Audit utility import ki gayi
from employees.models import EmployeeProfile  # Employee profile model import


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ChangePasswordView(views.APIView):
    permission_classes = [IsAuthenticated]  # Login hona zaroori hai

    def post(self, request):
        user = request.user
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not new_password or not confirm_password:
            return Response({"error": "Both new_password and confirm_password are required"}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Naya password set karein
        user.set_password(new_password)
        
        # 2. Flag ko False kar dein taaki dobara password change na mangey
        user.must_change_password = False
        user.save()

        return Response({"message": "Password changed successfully. You can now use your new password."}, status=status.HTTP_200_OK)


class AdminCreateEmployeeView(views.APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = EmployeeCreateSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            name = serializer.validated_data['name']

            # Duplicate email validation
            if CustomUser.objects.filter(email=email).exists():
                return Response({"error": "Email already exists"}, status=status.HTTP_409_CONFLICT)

            # Generate a strong temporary password
            temporary_password = get_random_string(length=12)

            # 1. Create employee
            user = CustomUser.objects.create_user(
                email=email,
                name=name,
                password=temporary_password
            )

            # must_change_password ko True set karna
            user.must_change_password = True
            user.save()

            # Optional fields request se lena
            phone_number = request.data.get('phone_number', None)
            designation = request.data.get('designation', None)

            # 2. Automatically create Employee Profile
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

            return Response({
                "message": "Employee created successfully",
                "employee_id": user.employee_id,
                "temporary_password": temporary_password
            }, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminResetPasswordView(views.APIView):
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
        
        user.set_password(new_temporary_password)
        user.must_change_password = True  # Reset ke baad bhi password change mandatory karna
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