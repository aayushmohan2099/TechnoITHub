from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser

class EmployeeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['name', 'email']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Token ke andar custom claims add karna
        token['role'] = user.role
        token['must_change_password'] = user.must_change_password
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user  # Logged-in user object

        # 🖼️ Profile picture ka full URL nikalna
        request = self.context.get('request')
        profile_pic_url = None
        if user.profile_picture and request:
            profile_pic_url = request.build_absolute_uri(user.profile_picture.url)
        elif user.profile_picture:
            profile_pic_url = user.profile_picture.url

        # 🏷️ EmployeeProfile se designation nikalna (agar exist karta hai)
        designation = None
        if hasattr(user, 'employeeprofile') and user.employeeprofile:
            designation = user.employeeprofile.designation

        # 🚀 Login response ke sath saari details ek sath bhejna
        data['role'] = user.role
        data['must_change_password'] = user.must_change_password
        data['employee_id'] = user.employee_id
        data['name'] = user.name
        data['designation'] = designation  # 👈 Yeh line add kar di gayi hai
        data['profile_picture'] = profile_pic_url 
        
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField() # Optional:agar profile API mein bhi chahiye

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
        if hasattr(obj, 'employeeprofile') and obj.employeeprofile:
            return obj.employeeprofile.designation
        return None