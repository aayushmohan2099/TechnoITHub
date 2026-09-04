import os
from celery import Celery

# Yahan 'ETTM.settings' ki jagah 'config.settings' karein
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')  # Yahan bhi 'config' kar dein

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()