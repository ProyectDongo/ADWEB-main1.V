from django.core.management.base import BaseCommand
from WEB.models import RegistroPermisos

def crear_permiso(nombre, descripcion=""):
    permiso, creado = RegistroPermisos.objects.get_or_create(nombre=nombre, defaults={'descripcion': descripcion})
    if creado:
        print(f"Permiso '{nombre}' creado exitosamente.")
    else:
        print(f"Permiso '{nombre}' ya existe.")

def crear_permisos_predeterminados():
    permisos = [
        ("crearpermisos.py", "Permiso para gestionar permisos"),
        ("crear_empresa", "Permiso para crear empresas"),
        ("crear_permiso", "Permiso para crear permisos"),
        ("crear_admin", "Permiso para crear administradores"),
        ("crear_supervisor", "Permiso para crear supervisores"),
        ("crear_trabajador", "Permiso para crear trabajadores"),
        ("listar_permisos", "Permiso para listar permisos"),
    ]
    for nombre, descripcion in permisos:
        crear_permiso(nombre, descripcion)

class Command(BaseCommand):
    help = 'Crea permisos personalizados'

    def handle(self, *args, **kwargs):
        crear_permisos_predeterminados()
        self.stdout.write(self.style.SUCCESS('Permisos predeterminados creados o ya existentes.'))