from django.core.management.base import BaseCommand
from WEB.models import Region, Provincia, Comuna

class Command(BaseCommand):
    help = 'Carga datos de regiones, provincias y comunas de Chile'

    def handle(self, *args, **kwargs):
        regions = [
            {
                'nombre': 'Arica y Parinacota',
                'provincias': [
                    {'nombre': 'Arica', 'comunas': ['Arica', 'Camarones']},
                    {'nombre': 'Parinacota', 'comunas': ['Putre', 'General Lagos']},
                ]
            },
            {
                'nombre': 'Tarapacá',
                'provincias': [
                    {'nombre': 'Iquique', 'comunas': ['Iquique', 'Alto Hospicio']},
                    {'nombre': 'Tamarugal', 'comunas': ['Pozo Almonte', 'Camiña', 'Colchane', 'Huara', 'Pica']},
                ]
            },
            {
                'nombre': 'Antofagasta',
                'provincias': [
                    {'nombre': 'Antofagasta', 'comunas': ['Antofagasta', 'Mejillones', 'Sierra Gorda', 'Taltal']},
                    {'nombre': 'El Loa', 'comunas': ['Calama', 'Ollagüe', 'San Pedro de Atacama']},
                    {'nombre': 'Tocopilla', 'comunas': ['Tocopilla', 'María Elena']},
                ]
            },
            {
                'nombre': 'Atacama',
                'provincias': [
                    {'nombre': 'Chañaral', 'comunas': ['Chañaral', 'Diego de Almagro']},
                    {'nombre': 'Copiapó', 'comunas': ['Copiapó', 'Caldera', 'Tierra Amarilla']},
                    {'nombre': 'Huasco', 'comunas': ['Vallenar', 'Alto del Carmen', 'Freirina', 'Huasco']},
                ]
            },
            {
                'nombre': 'Coquimbo',
                'provincias': [
                    {'nombre': 'Elqui', 'comunas': ['La Serena', 'Coquimbo', 'Andacollo', 'La Higuera', 'Paihuano', 'Vicuña']},
                    {'nombre': 'Choapa', 'comunas': ['Illapel', 'Canela', 'Los Vilos', 'Salamanca']},
                    {'nombre': 'Limarí', 'comunas': ['Ovalle', 'Combarbalá', 'Monte Patria', 'Punitaqui', 'Río Hurtado']},
                ]
            },
            {
                'nombre': 'Valparaíso',
                'provincias': [
                    {'nombre': 'Valparaíso', 'comunas': ['Valparaíso', 'Viña del Mar', 'Concón', 'Quintero', 'Puchuncaví', 'Casablanca', 'Juan Fernández']},
                    {'nombre': 'Isla de Pascua', 'comunas': ['Isla de Pascua']},
                    {'nombre': 'Los Andes', 'comunas': ['Los Andes', 'San Esteban', 'Calle Larga', 'Rinconada']},
                    {'nombre': 'Petorca', 'comunas': ['La Ligua', 'Petorca', 'Cabildo', 'Papudo', 'Zapallar']},
                    {'nombre': 'Quillota', 'comunas': ['Quillota', 'La Calera', 'Hijuelas', 'La Cruz', 'Nogales']},
                    {'nombre': 'San Antonio', 'comunas': ['San Antonio', 'Cartagena', 'El Tabo', 'El Quisco', 'Algarrobo', 'Santo Domingo']},
                    {'nombre': 'San Felipe de Aconcagua', 'comunas': ['San Felipe', 'Llay Llay', 'Catemu', 'Panquehue', 'Putaendo', 'Santa María']},
                ]
            },
            {
                'nombre': 'Metropolitana de Santiago',
                'provincias': [
                    {'nombre': 'Santiago', 'comunas': ['Santiago', 'Cerrillos', 'Cerro Navia', 'Conchalí', 'El Bosque', 'Estación Central', 'Huechuraba', 'Independencia', 
                     'La Cisterna', 'La Florida', 'La Granja', 'La Pintana', 'La Reina', 'Las Condes', 'Lo Barnechea', 'Lo Espejo', 'Lo Prado', 'Macul', 'Maipú', 'Ñuñoa', 
                     'Pedro Aguirre Cerda', 'Peñalolén', 'Providencia', 'Pudahuel', 'Quilicura', 'Quinta Normal', 'Recoleta', 'Renca', 'San Joaquín', 'San Miguel', 
                     'San Ramón', 'Vitacura']},
                    {'nombre': 'Chacabuco', 'comunas': ['Colina', 'Lampa', 'Tiltil']},
                    {'nombre': 'Cordillera', 'comunas': ['Puente Alto', 'Pirque', 'San José de Maipo']},
                    {'nombre': 'Maipo', 'comunas': ['San Bernardo', 'Buin', 'Calera de Tango', 'Paine']},
                    {'nombre': 'Melipilla', 'comunas': ['Melipilla', 'Alhué', 'Curacaví', 'María Pinto', 'San Pedro']},
                    {'nombre': 'Talagante', 'comunas': ['Talagante', 'El Monte', 'Isla de Maipo', 'Padre Hurtado', 'Peñaflor']},
                ]
            },
            {
                'nombre': 'Libertador General Bernardo O\'Higgins',
                'provincias': [
                    {'nombre': 'Cachapoal', 'comunas': ['Rancagua', 'Codegua', 'Coinco', 'Coltauco', 'Doñihue', 'Graneros', 'Las Cabras', 'Machalí', 'Malloa', 
                     'Mostazal', 'Olivar', 'Peumo', 'Pichidegua', 'Quinta de Tilcoco', 'Rengo', 'Requínoa', 'San Vicente de Tagua Tagua']},
                    {'nombre': 'Colchagua', 'comunas': ['San Fernando', 'Chépica', 'Chimbarongo', 'Lolol', 'Nancagua', 'Palmilla', 'Peralillo', 'Placilla', 
                     'Pumanque', 'Santa Cruz']},
                    {'nombre': 'Cardenal Caro', 'comunas': ['Pichilemu', 'La Estrella', 'Litueche', 'Marchihue', 'Navidad', 'Paredones']},
                ]
            },
            {
                'nombre': 'Maule',
                'provincias': [
                    {'nombre': 'Talca', 'comunas': ['Talca', 'Constitución', 'Curepto', 'Empedrado', 'Maule', 'Pelarco', 'Pencahue', 'Río Claro', 
                     'San Clemente', 'San Rafael']},
                    {'nombre': 'Cauquenes', 'comunas': ['Cauquenes', 'Chanco', 'Pelluhue']},
                    {'nombre': 'Curicó', 'comunas': ['Curicó', 'Hualañé', 'Licantén', 'Molina', 'Rauco', 'Romeral', 'Sagrada Familia', 'Teno', 'Vichuquén']},
                    {'nombre': 'Linares', 'comunas': ['Linares', 'Colbún', 'Longaví', 'Parral', 'Retiro', 'San Javier', 'Villa Alegre', 'Yerbas Buenas']},
                ]
            },
            {
                'nombre': 'Ñuble',
                'provincias': [
                    {'nombre': 'Diguillín', 'comunas': ['Chillán', 'Bulnes', 'Chillán Viejo', 'El Carmen', 'Pemuco', 'Pinto', 'Quillón', 'San Ignacio', 'Yungay']},
                    {'nombre': 'Punilla', 'comunas': ['San Carlos', 'Coihueco', 'Ñiquén', 'San Fabián', 'San Nicolás']},
                    {'nombre': 'Itata', 'comunas': ['Quirihue', 'Cobquecura', 'Coelemu', 'Ninhue', 'Portezuelo', 'Ránquil', 'Treguaco']},
                ]
            },
            {
                'nombre': 'Biobío',
                'provincias': [
                    {'nombre': 'Arauco', 'comunas': ['Lebu', 'Arauco', 'Cañete', 'Contulmo', 'Curanilahue', 'Los Álamos', 'Tirúa']},
                    {'nombre': 'Biobío', 'comunas': ['Los Ángeles', 'Antuco', 'Cabrero', 'Laja', 'Mulchén', 'Nacimiento', 'Negrete', 'Quilaco', 'Quilleco', 
                     'San Rosendo', 'Santa Bárbara', 'Tucapel', 'Yumbel', 'Alto Biobío']},
                    {'nombre': 'Concepción', 'comunas': ['Concepción', 'Coronel', 'Chiguayante', 'Florida', 'Hualpén', 'Hualqui', 'Lota', 'Penco', 
                     'San Pedro de la Paz', 'Santa Juana', 'Talcahuano', 'Tomé']},
                ]
            },
            {
                'nombre': 'La Araucanía',
                'provincias': [
                    {'nombre': 'Cautín', 'comunas': ['Temuco', 'Carahue', 'Cunco', 'Curarrehue', 'Freire', 'Galvarino', 'Gorbea', 'Lautaro', 'Loncoche', 
                     'Melipeuco', 'Nueva Imperial', 'Padre Las Casas', 'Perquenco', 'Pitrufquén', 'Pucón', 'Saavedra', 'Teodoro Schmidt', 'Toltén', 
                     'Vilcún', 'Villarrica', 'Cholchol']},
                    {'nombre': 'Malleco', 'comunas': ['Angol', 'Collipulli', 'Curacautín', 'Ercilla', 'Lonquimay', 'Los Sauces', 'Lumaco', 
                     'Purén', 'Renaico', 'Traiguén', 'Victoria']},
                ]
            },
            {
                'nombre': 'Los Ríos',
                'provincias': [
                    {'nombre': 'Valdivia', 'comunas': ['Valdivia', 'Corral', 'Lanco', 'Los Lagos', 'Máfil', 'Mariquina', 'Paillaco', 'Panguipulli']},
                    {'nombre': 'Ranco', 'comunas': ['La Unión', 'Futrono', 'Lago Ranco', 'Río Bueno']},
                ]
            },
            {
                'nombre': 'Los Lagos',
                'provincias': [
                    {'nombre': 'Llanquihue', 'comunas': ['Puerto Montt', 'Calbuco', 'Cochamó', 'Fresia', 'Frutillar', 'Los Muermos', 'Llanquihue', 
                     'Maullín', 'Puerto Varas']},
                    {'nombre': 'Chiloé', 'comunas': ['Castro', 'Ancud', 'Chonchi', 'Curaco de Vélez', 'Dalcahue', 'Puqueldón', 'Queilén', 
                     'Quellón', 'Quemchi', 'Quinchao']},
                    {'nombre': 'Osorno', 'comunas': ['Osorno', 'San Juan de la Costa', 'San Pablo', 'Puyehue', 'Río Negro', 'Purranque', 'Puerto Octay']},
                    {'nombre': 'Palena', 'comunas': ['Chaitén', 'Futaleufú', 'Hualaihué', 'Palena']},
                ]
            },
            {
                'nombre': 'Aysén del General Carlos Ibáñez del Campo',
                'provincias': [
                    {'nombre': 'Coyhaique', 'comunas': ['Coyhaique', 'Lago Verde']},
                    {'nombre': 'Aysén', 'comunas': ['Puerto Aysén', 'Cisnes', 'Guaitecas']},
                    {'nombre': 'Capitán Prat', 'comunas': ['Cochrane', 'O\'Higgins', 'Tortel']},
                    {'nombre': 'General Carrera', 'comunas': ['Chile Chico', 'Río Ibáñez']},
                ]
            },
            {
                'nombre': 'Magallanes y de la Antártica Chilena',
                'provincias': [
                    {'nombre': 'Magallanes', 'comunas': ['Punta Arenas', 'Laguna Blanca', 'Río Verde', 'San Gregorio']},
                    {'nombre': 'Antártica Chilena', 'comunas': ['Cabo de Hornos', 'Antártica']},
                    {'nombre': 'Tierra del Fuego', 'comunas': ['Porvenir', 'Primavera', 'Timaukel']},
                    {'nombre': 'Última Esperanza', 'comunas': ['Puerto Natales', 'Torres del Paine']},
                ]
            },
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