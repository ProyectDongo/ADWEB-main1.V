import os
import django
from django.conf import settings
from django.core.management.base import BaseCommand

# Configuración del entorno Django si no está configurado
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tu_proyecto.settings')
django.setup()

from WEB.models import RegistroPermisos, Usuario

def crear_admin_unico():
    admin, creado = Usuario.objects.get_or_create(
        email="admin@empresa.com",
        defaults={
            'username': "admin",
            'first_name': "Administrador",
            'last_name': "Principal",
            'role': "admin"
        }
    )
    if creado:
        admin.set_password('admin123')  # Contraseña por defecto
        admin.save()
        # Asignar todos los permisos al administrador
        permisos = RegistroPermisos.objects.all()
        admin.permisos.set(permisos)
        admin.save()
        print("Administrador creado exitosamente y permisos asignados.")
    else:
        print("El administrador ya existe.")

class Command(BaseCommand):
    help = 'Crea un administrador único'

    def handle(self, *args, **kwargs):
        crear_admin_unico()
        self.stdout.write(self.style.SUCCESS('Administrador único creado o ya existente.'))