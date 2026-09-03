from django.urls import path
from ..views import CheckAndUpdateView, UploadBuildAPIView

urlpatterns = [
    path('check/', CheckAndUpdateView.as_view(), name='check-update'),
    path('upload-build/', UploadBuildAPIView.as_view(), name='upload-build'),
]