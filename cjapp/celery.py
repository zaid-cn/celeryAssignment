import os
from celery import Celery
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cjapp.settings')

celery_app = Celery('tasks')

celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks(settings.INSTALLED_APPS)

# CREATE USER 'zaidraza'@'%' IDENTIFIED WITH mysql_native_password BY 'algorithm';
# GRANT ALL ON tu2k20_zaid.* TO 'zaidraza'@'%';
# FLUSH PRIVILEGES;