from django.core.management.base import BaseCommand
from WEB.models import Plan

class Command(BaseCommand):
    help = 'Crea planes base en la base de datos'

    def handle(self, *args, **kwargs):
        planes = [
            ("Plan Básico", 10,  50000.00),
            ("Plan Intermedio", 50,  80000.00),
            ("Plan Avanzado", 90,  100000.00),
            ("Plan Premium", 100,  150000.00)
        ]
        
        for nombre, sup, valor in planes:
            codigo = nombre.upper().replace(" ", "_")
            plan, creado = Plan.objects.get_or_create(
                nombre=nombre,
                max_usuarios=sup,
                valor=valor,
                codigo=codigo,
                activo=True
            )
            if creado:
                self.stdout.write(self.style.SUCCESS(f'Plan "{nombre}" creado exitosamente.'))
            else:
                self.stdout.write(self.style.WARNING(f'Plan "{nombre}" ya existe.'))