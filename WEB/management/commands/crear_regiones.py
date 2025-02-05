# migrations/load_chile_data.py
from django.core.management.base import BaseCommand
from WEB.models import Region, Provincia, Comuna

class Command(BaseCommand):
    help = 'Carga datos de regiones, provincias y comunas de Chile'

    def handle(self, *args, **kwargs):
        # Ejemplo de datos (debes completar con todos los datos reales)
        regions = [
            {
                'nombre': 'Arica y Parinacota',
                'provincias': [
                    {
                        'nombre': 'Arica',
                        'comunas': ['Arica', 'Camarones']
                    },
                    {
                        'nombre': 'Parinacota',
                        'comunas': ['Putre', 'General Lagos']
                    }
                ]
            },
            {
                'nombre': 'Tarapacá',
                'provincias': [
                    {
                        'nombre': 'Iquique',
                        'comunas': ['Iquique', 'Alto Hospicio']
                    },
                    {
                        'nombre': 'Tamarugal',
                        'comunas': ['Pozo Almonte', 'Pica']
                    }
                ]
            },
            # Agregar todas las regiones con sus provincias y comunas
        ]

        for region_data in regions:
            region, _ = Region.objects.get_or_create(nombre=region_data['nombre'])
            for provincia_data in region_data['provincias']:
                provincia, _ = Provincia.objects.get_or_create(
                    nombre=provincia_data['nombre'],
                    region=region
                )
                for comuna_nombre in provincia_data['comunas']:
                    Comuna.objects.get_or_create(
                        nombre=comuna_nombre,
                        provincia=provincia
                    )

        self.stdout.write(self.style.SUCCESS('Datos de Chile cargados exitosamente'))