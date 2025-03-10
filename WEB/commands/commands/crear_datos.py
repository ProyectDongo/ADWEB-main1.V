from django.core.management.base import BaseCommand
from WEB.models import RegistroEmpresas, Usuario

class Command(BaseCommand):
    help = 'Crea 10 empresas, 1 supervisor por empresa y 10 trabajadores por empresa'

    def handle(self, *args, **kwargs):
        # Crear 10 empresas
        empresas = []
        for i in range(1, 11):
            rut = f"12345678-{i}"
            # Verificar si la empresa ya existe
            if not RegistroEmpresas.objects.filter(rut=rut).exists():
                empresa = RegistroEmpresas(
                    rut=rut,
                    nombre=f"Empresa {i}",
                    direccion=f"Dirección {i}",
                    telefono=f"+5691234567{i}"
                )
                empresa.save()
                empresas.append(empresa)
                self.stdout.write(self.style.SUCCESS(f'Empresa {i} creada'))
            else:
                self.stdout.write(self.style.WARNING(f'Empresa con RUT {rut} ya existe'))

        # Crear 1 supervisor y 10 trabajadores por empresa
        for empresa in empresas:
            # Crear supervisor
            username_supervisor = f"supervisor_{empresa.nombre.lower().replace(' ', '_')}"
            if not Usuario.objects.filter(username=username_supervisor).exists():
                supervisor = Usuario(
                    username=username_supervisor,
                    role='supervisor',
                    empresa=empresa
                )
                supervisor.set_password('password123')  # Contraseña por defecto
                supervisor.save()
                self.stdout.write(self.style.SUCCESS(f'Supervisor para {empresa.nombre} creado'))
            else:
                self.stdout.write(self.style.WARNING(f'Supervisor {username_supervisor} ya existe'))

            # Crear 10 trabajadores
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