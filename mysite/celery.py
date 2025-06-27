import os
from celery import Celery

# Establecer la configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

# Crear la aplicación Celery
app = Celery('mysite')

# Cargar configuración desde Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodescubrir tareas en las aplicaciones instaladas
app.autodiscover_tasks()