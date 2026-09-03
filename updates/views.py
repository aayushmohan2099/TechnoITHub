import os
from django.http import FileResponse, Http404
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import AppBuild

class CheckAndUpdateView(views.APIView):
    """
    API 1: Client ka version check karne ke liye.
    Endpoint: /api/v1/updates/check/?version=1.0.0
    """
    permission_classes = [AllowAny]

    def get(self, request):
        client_version = request.query_params.get('version')
        if not client_version:
            return Response({"error": "Version parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Database se sabse naya build nikalna
        latest_build = AppBuild.objects.order_by('-uploaded_at').first()

        if not latest_build:
            return Response({"message": "No builds found on server"}, status=status.HTTP_404_NOT_FOUND)

        # Version comparison
        update_available = client_version != latest_build.version_code

        download_url = None
        if update_available:
            # Download API ka absolute URL generate karna
            download_url = request.build_absolute_uri(f'/api/v1/updates/download/?version={latest_build.version_code}')

        return Response({
            "update_available": update_available,
            "current_version": client_version,
            "latest_version": latest_build.version_code,
            "download_url": download_url,
            "changelog": latest_build.changelog if update_available else ""
        }, status=status.HTTP_200_OK)


class DownloadBuildView(views.APIView):
    """
    API 2: Naye version ki .exe file ko automatically download (stream) karane ke liye.
    Endpoint: /api/v1/updates/download/?version=1.0.1
    """
    permission_classes = [AllowAny]

    def get(self, request):
        version_code = request.query_params.get('version')
        
        if version_code:
            build = AppBuild.objects.filter(version_code=version_code).first()
        else:
            build = AppBuild.objects.order_by('-uploaded_at').first()

        if not build or not build.build_file:
            raise Http404("Build file not found on server.")

        file_path = build.build_file.path
        if os.path.exists(file_path):
            file_name = os.path.basename(file_path)
            # FileResponse large .exe files ke liye sabse fast aur memory-efficient tareeqa hai
            return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file_name)
        
        raise Http404("File does not exist on disk.")


class UploadBuildAPIView(views.APIView):
    """
    API 3: Python Script (ETTM_Uploader.py) ke zariye direct .exe aur version upload karne ke liye.
    Endpoint: /api/v1/updates/upload-build/
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # <--- Yeh error hatane ke liye zaroori hai!

    def post(self, request):
        version_code = request.data.get('version_code')
        build_file = request.FILES.get('build_file')
        changelog = request.data.get('changelog', '')

        if not version_code or not build_file:
            return Response({"error": "Version code and build file are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Database mein record save aur file server par upload hogi
        build, created = AppBuild.objects.update_or_create(
            version_code=version_code,
            defaults={'build_file': build_file, 'changelog': changelog}
        )

        return Response({
            "success": True,
            "message": f"Build version {version_code} uploaded successfully!"
        }, status=status.HTTP_201_CREATED)