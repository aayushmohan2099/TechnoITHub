from django.urls import path
from ..views import CheckAndUpdateView, DownloadBuildView, UploadBuildAPIView

urlpatterns = [
    path('check/', CheckAndUpdateView.as_view(), name='check-update'),
    path('download/', DownloadBuildView.as_view(), name='download-build'),
    path('upload-build/', UploadBuildAPIView.as_view(), name='upload-build'),
]