from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser
from employees.models import EmployeeProfile

class EmployeeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['name', 'email']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['must_change_password'] = user.must_change_password
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user  # Logged-in CustomUser object

        # 🖼️ Profile picture ka full URL nikalna
        request = self.context.get('request')
        profile_pic_url = None
        if user.profile_picture and request:
            profile_pic_url = request.build_absolute_uri(user.profile_picture.url)
        elif user.profile_picture:
            profile_pic_url = user.profile_picture.url

        # 🏷️ EmployeeProfile table se safe tarike se designation nikalna
        designation = "Employee"  # Default fallback agar profile na mile
        try:
            profile = EmployeeProfile.objects.filter(user=user).first()
            if profile and profile.designation:
                designation = profile.designation
        except Exception:
            pass

        # 🚀 Login response ke sath saari details bhejna
        data['role'] = user.role
        data['must_change_password'] = user.must_change_password
        data['employee_id'] = user.employee_id
        data['name'] = user.name
        data['designation'] = designation  # 👈 Ab yahan sahi designation aayega
        data['profile_picture'] = profile_pic_url 
        
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'employee_id', 'name', 'email', 'role', 'profile_picture', 'must_change_password', 'designation']

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture and request:
            return request.build_absolute_uri(obj.profile_picture.url)
        elif obj.profile_picture:
            return obj.profile_picture.url
        return None

    def get_designation(self, obj):
        try:
            profile = EmployeeProfile.objects.filter(user=obj).first()
            if profile:
                return profile.designation
        except Exception:
            pass
        return None