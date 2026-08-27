from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.parsers import MultiPartParser, FormParser  # 👈 Image upload ke liye zaroori hai
from django.utils.crypto import get_random_string
from .models import CustomUser
from .serializers import EmployeeCreateSerializer, CustomTokenObtainPairSerializer, UserProfileSerializer  # 👈 UserProfileSerializer import karein
from .permissions import IsAdmin
from audit.utils import log_action  
from employees.models import EmployeeProfile  


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ChangePasswordView(views.APIView):
    permission_classes = [IsAuthenticated]  

    def post(self, request):
        user = request.user
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not new_password or not confirm_password:
            return Response({"error": "Both new_password and confirm_password are required"}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
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

            if CustomUser.objects.filter(email=email).exists():
                return Response({"error": "Email already exists"}, status=status.HTTP_409_CONFLICT)

            temporary_password = get_random_string(length=12)

            user = CustomUser.objects.create_user(
                email=email,
                name=name,
                password=temporary_password
            )

            user.must_change_password = True
            user.save()

            phone_number = request.data.get('phone_number', None)
            designation = request.data.get('designation', None)

            EmployeeProfile.objects.create(
                user=user,
                employee_id=user.employee_id,
                name=user.name,
                email=user.email,
                phone_number=phone_number,
                designation=designation
            )

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

        new_temporary_password = get_random_string(length=12)
        
        user.set_password(new_temporary_password)
        user.must_change_password = True  
        user.save()

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


# ==========================================
# 🆕 EMPLOYEE PROFILE & DP (PHOTO) VIEWS
# ==========================================

class CurrentUserProfileView(views.APIView):
    """ Logged-in employee apne dashboard ke liye apna naam aur photo yahan se dekhega """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateProfilePictureView(views.APIView):
    """ Employee apni DP (Profile Picture) yahan upload ya change karega """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # 👈 File/Image accept karne ke liye zaroori hai

    def patch(self, request):
        user = request.user
        profile_pic = request.FILES.get('profile_picture')

        if not profile_pic:
            return Response({"error": "No image file provided."}, status=status.HTTP_400_BAD_REQUEST)

        user.profile_picture = profile_pic
        user.save()

        serializer = UserProfileSerializer(user, context={'request': request})
        return Response({
            "message": "Profile picture updated successfully!",
            "data": serializer.data
        }, status=status.HTTP_200_OK)