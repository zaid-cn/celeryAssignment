
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cjapp.settings')

celery_app = Celery('restapi')

celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# CREATE USER 'zaidraza'@'%' IDENTIFIED WITH mysql_native_password BY 'algorithm';
# GRANT ALL ON tu2k20_zaid.* TO 'zaidraza'@'%';
# FLUSH PRIVILEGES;