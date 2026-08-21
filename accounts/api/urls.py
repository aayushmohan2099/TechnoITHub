from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import AdminCreateEmployeeView

router = DefaultRouter()

# Agar future me ViewSets aate hain toh yahan register honge
# router.register(r"employees", EmployeeViewSet, basename="employee")

urlpatterns = [
    # Router include
    path("", include(router.urls)),

    # Auth APIs (Login aur Token Refresh yahan merge kar diye)
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Specific APIs
    path(
        "admin/create-employee/",
        AdminCreateEmployeeView.as_view(),
        name="admin-create-employee",
    ),
]