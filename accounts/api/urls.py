from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.views import (
    AdminCreateEmployeeView, 
    AdminResetPasswordView,
    CurrentUserProfileView, 
    CustomTokenObtainPairView,
    ChangePasswordView,
    UpdateProfilePictureView
)

router = DefaultRouter()

urlpatterns = [
    # Router include
    path("", include(router.urls)),

    # Auth APIs
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Password Change API (Employee ke liye)
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),

    # Admin APIs
    path(
        "admin/create-employee/",
        AdminCreateEmployeeView.as_view(),
        name="admin-create-employee",
    ),
    path(
        'admin/reset-password/', 
        AdminResetPasswordView.as_view(), 
        name='admin-reset-password'
    ),
    
    path('me/', CurrentUserProfileView.as_view(), 
         name='current-user-profile'),
    path('update-dp/', UpdateProfilePictureView.as_view(),
     name='update-profile-picture'),
]