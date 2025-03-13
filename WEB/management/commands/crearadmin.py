import os
import django
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from WEB.models import Usuario

def crear_admin_unico():
    # Crear o obtener el usuario admin
    admin, creado = Usuario.objects.get_or_create(
        email="admin@empresa.com",
        defaults={
            'username': "admin",
            'first_name': "Administrador",
            'last_name': "Principal",
            'role': "admin",
            'is_staff': False  # Aseguramos que no sea staff
        }
    )
    
    if creado:
        admin.set_password('admin123')
        admin.save()
        print("Administrador creado exitosamente.")
    else:
        print("El administrador ya existe.")
    
    # Obtener o crear el grupo admin
    grupo_admin, grupo_creado = Group.objects.get_or_create(name='admin')
    
    # Asignar todos los permisos al grupo admin
    if grupo_creado:
        # Incluir todos los permisos del sistema
        todos_permisos = Permission.objects.all()
        grupo_admin.permissions.set(todos_permisos)
        print("Todos los permisos asignados al grupo admin.")
    
    # Añadir usuario al grupo admin si no está ya asignado
    if not admin.groups.filter(name='admin').exists():
        admin.groups.add(grupo_admin)
        print("Usuario admin añadido al grupo admin.")
    
    # Actualizar permisos directos (por si hay algún permiso especial)
    admin.user_permissions.set(grupo_admin.permissions.all())
    admin.save()

class Command(BaseCommand):
    help = 'Crea un administrador único y asigna todos los permisos mediante grupo'
    
    def handle(self, *args, **kwargs):
        crear_admin_unico()
        self.stdout.write(
            self.style.SUCCESS('Proceso completado: '
                               'Usuario admin creado/verificado y permisos asignados via grupo admin')
        )