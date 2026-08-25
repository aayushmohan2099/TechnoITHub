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
        # Login response ke sath extra fields bhejna
        data['role'] = self.user.role
        data['must_change_password'] = self.user.must_change_password
        data['employee_id'] = self.user.employee_id
        data['name'] = self.user.name
        return data