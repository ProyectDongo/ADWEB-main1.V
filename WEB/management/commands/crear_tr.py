from django.core.management.base import BaseCommand
from WEB.models import RegistroEmpresas, Usuario
# este comando esta desactualizado no usar
class Command(BaseCommand):
    help = 'Asocia 10 trabajadores y 2 supervisores a cada empresa existente'

    def handle(self, *args, **kwargs):
        # Obtener todas las empresas
        empresas = RegistroEmpresas.objects.all()

        # Verificar si hay empresas
        if not empresas:
            self.stdout.write(self.style.ERROR('No hay empresas en la base de datos.'))
            return

        # Recorrer cada empresa
        for empresa in empresas:
            self.stdout.write(self.style.SUCCESS(f'Procesando empresa: {empresa.nombre}'))

            # Crear 2 supervisores para la empresa
            for i in range(1, 3):
                username_supervisor = f"supervisor_{empresa.nombre.lower().replace(' ', '_')}_{i}"
                if not Usuario.objects.filter(username=username_supervisor).exists():
                    supervisor = Usuario(
                        username=username_supervisor,
                        role='supervisor',
                        empresa=empresa
                    )
                    supervisor.set_password('password123')  # Contraseña por defecto
                    supervisor.save()
                    self.stdout.write(self.style.SUCCESS(f'Supervisor {i} para {empresa.nombre} creado'))
                else:
                    self.stdout.write(self.style.WARNING(f'Supervisor {username_supervisor} ya existe'))

            # Crear 10 trabajadores para la empresa
            for j in range(1, 11):
                username_trabajador = f"trabajador_{empresa.nombre.lower().replace(' ', '_')}_{j}"
                if not Usuario.objects.filter(username=username_trabajador).exists():
                    trabajador = Usuario(
                        username=username_trabajador,
                        role='trabajador',
                        empresa=empresa
                    )
                    trabajador.set_password('password123')  # Contraseña por defecto
                    trabajador.save()
                    self.stdout.write(self.style.SUCCESS(f'Trabajador {j} para {empresa.nombre} creado'))
                else:
                    self.stdout.write(self.style.WARNING(f'Trabajador {username_trabajador} ya existe'))

        self.stdout.write(self.style.SUCCESS('Proceso completado exitosamente'))