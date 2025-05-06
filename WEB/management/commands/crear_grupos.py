from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Crea grupos de usuarios y asigna permisos específicos'

    def handle(self, *args, **kwargs):
        # Permisos para Admin (todos los listados)
        admin_permissions = [
            'crear_plan',
            'lista_permisos',
            'crear_permiso',
            'vista_planes',
            'crear_empresa',
            'eliminar_empresa',
            'detalles_empresa',
            'lista_empresas',
            'vista_empresas',
            'generar_boleta',
            'vista_servicios',
            'vista_estadisticas',
            'Registrar_pago',
            'eliminar_trabajador',
            'eliminar_supervisor',
            'eliminar_admin',

            'crear_admin',
            'crear_supervisor',
            'crear_trabajador',
            
            'editar_supervisor',
            'editar_trabajador',
        ]

        # Grupo Admin
        admin_group, created = Group.objects.get_or_create(name='Admin')
        permissions = Permission.objects.filter(codename__in=admin_permissions)
        admin_group.permissions.set(permissions)
        self.stdout.write(self.style.SUCCESS('Permisos asignados a Admin'))

        # Permisos para Supervisor
        supervisor_permissions = [
            'crear_trabajador',
            'editar_trabajador'
        ]

        # Grupo Supervisor
        supervisor_group, created = Group.objects.get_or_create(name='Supervisor')
        permissions = Permission.objects.filter(codename__in=supervisor_permissions)
        supervisor_group.permissions.set(permissions)
        self.stdout.write(self.style.SUCCESS('Permisos asignados a Supervisor'))

        # Grupo Trabajador (sin permisos)
        trabajador_group, created = Group.objects.get_or_create(name='Trabajador')
        trabajador_group.permissions.clear()
        self.stdout.write(self.style.SUCCESS('Grupo Trabajador creado'))

        self.stdout.write(self.style.SUCCESS('Configuración de grupos completada'))