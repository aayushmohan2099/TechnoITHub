from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ObjectDoesNotExist
from .models import CustomUser
from employees.models import EmployeeProfile, Designation

class EmployeeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['name', 'email']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = getattr(user, 'role', None)
        token['must_change_password'] = getattr(user, 'must_change_password', None)
        try:
            if hasattr(user, 'employee_profile') and user.employee_profile and user.employee_profile.designation:
                token['designation'] = user.employee_profile.designation.title
        except (ObjectDoesNotExist, AttributeError):
            pass
        return token

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            user = self.user  

            data['role'] = getattr(user, 'role', None)
            data['must_change_password'] = getattr(user, 'must_change_password', None)
            data['employee_id'] = getattr(user, 'employee_id', None)
            data['name'] = getattr(user, 'name', None)
            
            profile_pic_url = None
            try:
                if getattr(user, 'profile_picture', None):
                    profile_pic_url = user.profile_picture.url
            except (ValueError, AttributeError):
                profile_pic_url = None
                
            data['profile_picture'] = profile_pic_url
            
            # Default null-safe values
            data['designation_id'] = None
            data['designation_title'] = None
            
            try:
                profile = getattr(user, 'employee_profile', None)
                if profile and profile.designation:
                    data['designation_id'] = profile.designation.id
                    data['designation_title'] = profile.designation.title
            except (ObjectDoesNotExist, AttributeError):
                pass
            
            return data

        except Exception as e:
            import traceback
            traceback.print_exc()
            raise e