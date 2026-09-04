from django.contrib import admin
from django.urls import path, include
from django.conf import settings  
from django.conf.urls.static import static  
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import JsonResponse

def health(request):
    return JsonResponse({"status": "healthy", "project": "Employee Tracker"})

schema_view = get_schema_view(
   openapi.Info(
      title="Employee Tracker API",
      default_version='v1',
      description="API Directory for Employee Tracker",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('health/', health),
    
    # API Routes
    path("api/v1/accounts/", include("accounts.api.urls")),
    path("api/v1/attendance/", include("attendance.api.urls")),
    path("api/v1/tasks/", include("tasks.api.urls")),
    path("api/v1/employees/", include("employees.api.urls")),
]

urlpatterns += [
    path("swagger.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger.yaml", schema_view.without_ui(cache_timeout=0), name="schema-yaml"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)