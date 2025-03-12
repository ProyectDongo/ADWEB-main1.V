from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # Grupo Admin: Todos los permisos
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        admin_group.permissions.set(Permission.objects.all())

        # Grupo Supervisor: Permisos específicos
        supervisor_group, _ = Group.objects.get_or_create(name='Supervisor')
        permisos_supervisor = Permission.objects.filter(
            codename__in=['crear_trabajador', 'editar_trabajador']
        )
        supervisor_group.permissions.set(permisos_supervisor)

        # Grupo Trabajador: Sin permisos
        trabajador_group, _ = Group.objects.get_or_create(name='Trabajador')