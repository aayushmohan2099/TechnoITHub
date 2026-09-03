from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import AppBuild

class CheckAndUpdateView(views.APIView):
    """ Client ka version check karne ke liye API """
    permission_classes = [AllowAny]

    def get(self, request):
        client_version = request.query_params.get('version')
        if not client_version:
            return Response({"error": "Version parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Database se sabse naya build nikalna
        latest_build = AppBuild.objects.order_by('-uploaded_at').first()
        
        if not latest_build:
            return Response({"message": "No builds found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Version comparison
        update_available = client_version != latest_build.version_code
        download_url = request.build_absolute_uri(latest_build.build_file.url) if update_available else None

        return Response({
            "update_available": update_available,
            "current_version": client_version,
            "latest_version": latest_build.version_code,
            "download_url": download_url,
            "changelog": latest_build.changelog
        }, status=status.HTTP_200_OK)


class UploadBuildAPIView(views.APIView):
    """ Script (publish.js) ke zariye direct .exe aur version upload karne ke liye (No Admin Panel needed) """
    permission_classes = [AllowAny]

    def post(self, request):
        version_code = request.data.get('version_code')
        build_file = request.FILES.get('build_file')
        changelog = request.data.get('changelog', '')

        if not version_code or not build_file:
            return Response({"error": "Version code and build file are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Agar version pehle se hai toh update karega, nahi toh naya create karega
        build, created = AppBuild.objects.update_or_create(
            version_code=version_code,
            defaults={'build_file': build_file, 'changelog': changelog}
        )

        return Response({
            "success": True,
            "message": f"Build version {version_code} uploaded successfully!"
        }, status=status.HTTP_201_CREATED)