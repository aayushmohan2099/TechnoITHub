import os
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.parsers import MultiPartParser, FormParser 
from django.utils.crypto import get_random_string

from .models import CustomUser
from .serializers import EmployeeCreateSerializer, CustomTokenObtainPairSerializer
from .permissions import IsAdmin
from audit.utils import log_action  
from employees.models import EmployeeProfile, Designation  


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

            # 🛑 Strict Check: Designation dena ab compulsory hai!
            designation_id = request.data.get('designation')
            if not designation_id:
                return Response({"error": "Designation is required. Please select a designation ID."}, status=status.HTTP_400_BAD_REQUEST)

            # Database se designation fetch karna
            try:
                designation_obj = Designation.objects.get(id=designation_id)
            except (Designation.DoesNotExist, ValueError, TypeError):
                return Response({"error": "Invalid designation ID provided."}, status=status.HTTP_400_BAD_REQUEST)

            temporary_password = get_random_string(length=12)

            user = CustomUser.objects.create_user(
                email=email,
                name=name,
                password=temporary_password
            )

            user.must_change_password = True
            user.save()

            phone_number = request.data.get('phone_number', None)

            EmployeeProfile.objects.create(
                user=user,
                employee_id=user.employee_id,
                name=user.name,
                email=user.email,
                phone_number=phone_number,
                designation=designation_obj  # Ab yahan hamesha valid designation jayegi, kabhi null nahi hogi!
            )

            log_action(
                actor=request.user,
                action="CREATE_EMPLOYEE",
                entity_type="CustomUser",
                entity_id=user.id,
                metadata={"employee_id": user.employee_id, "email": user.email, "designation": designation_obj.title}
            )

            return Response({
                "message": "Employee created successfully",
                "employee_id": user.employee_id,
                "temporary_password": temporary_password,
                "designation_title": designation_obj.title
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
# 🖼️ UPDATE & DELETE PROFILE PICTURE (DP) API
# ==========================================

class UpdateProfilePictureView(views.APIView):
    """ Employee apni DP (Profile Picture) update ya delete karega ek hi endpoint se """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    # 1. DP Update / Upload karne ke liye (PATCH request)
    def patch(self, request):
        user = request.user
        profile_pic = request.FILES.get('profile_picture')

        if not profile_pic:
            return Response({"error": "No image file provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Purani photo delete karna taaki storage clean rahe
        if user.profile_picture:
            user.profile_picture.delete(save=False)

        # File name ko unique banana taaki overwrite na ho
        ext = os.path.splitext(profile_pic.name)[1]
        profile_pic.name = f"{user.employee_id}_{get_random_string(8)}{ext}"

        user.profile_picture = profile_pic
        user.save()

        profile_pic_url = request.build_absolute_uri(user.profile_picture.url) if user.profile_picture else None

        return Response({
            "message": "Profile picture updated successfully!",
            "employee_id": user.employee_id,
            "name": user.name,
            "profile_picture": profile_pic_url
        }, status=status.HTTP_200_OK)

    # 2. DP Delete karne ke liye (DELETE request)
    def delete(self, request):
        user = request.user

        if not user.profile_picture:
            return Response({"error": "No profile picture found to delete."}, status=status.HTTP_404_NOT_FOUND)

        user.profile_picture.delete(save=False)
        user.profile_picture = None
        user.save()

        return Response({
            "message": "Profile picture deleted successfully!",
            "employee_id": user.employee_id,
            "name": user.name,
            "profile_picture": None
        }, status=status.HTTP_200_OK)