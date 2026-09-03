from django.db import models

class AppBuild(models.Model):
    version_code = models.CharField(max_length=50, unique=True) # e.g., "1.0.0", "1.0.1"
    download_url = models.CharField(max_length=500) # Yahan .exe file upload hogi
    changelog = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Version {self.version_code}"