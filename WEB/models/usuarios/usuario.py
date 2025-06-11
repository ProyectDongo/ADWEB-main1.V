from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
from WEB.models.gestion_administrativa.geografia import Region, Provincia, Comuna
from WEB.views.scripts import validar_rut
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
from django.core.validators import MinValueValidator, MaxValueValidator




class Horario(models.Model):
    TIPO_HORARIO = [
        ('diurno', 'Diurno'),
        ('nocturno', 'Nocturno'),
        ('mixto', 'Mixto'),
    ]
    nombre = models.CharField(max_length=100)
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField()
    tolerancia_retraso = models.IntegerField(default=20, validators=[MinValueValidator(0), MaxValueValidator(60)])  # in minutes
    tolerancia_horas_extra = models.IntegerField(default=20, validators=[MinValueValidator(0), MaxValueValidator(60)])
    tipo_horario = models.CharField(max_length=20, choices=TIPO_HORARIO, default='diurno') 
    empresa = models.ForeignKey('RegistroEmpresas', on_delete=models.CASCADE, related_name='horarios')

    def __str__(self):
        return f"{self.nombre} ({self.hora_entrada} - {self.hora_salida}) - {self.get_tipo_horario_display()}"





class Turno(models.Model):
    nombre = models.CharField(max_length=100)
    dias_trabajo = models.IntegerField()
    dias_descanso = models.IntegerField()
    inicio_turno = models.DateField(null=True, blank=True) 
    empresa = models.ForeignKey('RegistroEmpresas', on_delete=models.CASCADE, related_name='turnos')

    def __str__(self):
        return f"{self.nombre} ({self.dias_trabajo}x{self.dias_descanso})"






class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('supervisor', 'Supervisor'),
        ('trabajador', 'Trabajador'),
    )
    METODOS_REGISTRO = [
        ('firma', 'Firma Digital'),
        ('huella', 'Huella Digital'),
        ('geo', 'Geolocalización'),
    ]
    rut = models.CharField(max_length=12, unique=True, validators=[validar_rut])
    role = models.CharField(max_length=20, choices=ROLES, default='admin')
    empresa = models.ForeignKey(
        'RegistroEmpresas', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name="usuarios"
    )
    celular = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    vigencia_plan = models.ForeignKey(
        'VigenciaPlan', 
        on_delete=models.CASCADE, 
        related_name='usuarios', 
        null=True, 
        blank=True
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='usuarios',
        help_text='Grupos a los que pertenece el usuario'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='usuarios',
        help_text='Permisos específicos para este usuario'
    )
    is_locked = models.BooleanField(
        default=False,
        verbose_name="Cuenta bloqueada",
        help_text="Indica si la cuenta está bloqueada por seguridad"
    )
    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        verbose_name="Intentos fallidos"
    )
    last_failed_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Último intento fallido"
    )
    horario = models.ForeignKey('Horario', on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')
    turno = models.ForeignKey('Turno', on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios')
    metodo_registro_permitido = models.CharField(
        max_length=20,
        choices=METODOS_REGISTRO,
        default='firma'
    )

    def puede_trabajar(self, fecha):
        dia_habilitado = self.dias_habilitados.filter(fecha=fecha).first()
        if dia_habilitado is not None:
            return dia_habilitado.habilitado
        return self.debe_trabajar(fecha)

    @property
    def has_huella(self):
        return hasattr(self, 'huellas')

    def debe_trabajar(self, fecha):
        if not self.turno or not self.turno.inicio_turno:
            return True 
        ciclo_total = self.turno.dias_trabajo + self.turno.dias_descanso
        dias_desde_inicio = (fecha - self.turno.inicio_turno).days % ciclo_total
        return dias_desde_inicio < self.turno.dias_trabajo

    def save(self, *args, **kwargs):
        if self.vigencia_plan and not self.pk:
            current_users = self.vigencia_plan.usuarios.count()
            max_users = self.vigencia_plan.get_max_usuarios()
            if current_users >= max_users:
                raise ValidationError(
                    f"No se pueden añadir más usuarios. El límite del plan "
                    f"{self.vigencia_plan.plan.nombre} ({max_users}) ha sido alcanzado."
                )
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        permissions = [
            ("eliminar_trabajador", "Permiso para eliminar trabajadores"),
            ("eliminar_supervisor", "Permiso para eliminar supervisores"),
            ("eliminar_admin", "Permiso para eliminar administradores"),
            ("crear_admin", "Permiso para crear administradores"),
            ("crear_supervisor", "Permiso para crear supervisores"),
            ("crear_trabajador", "Permiso para crear trabajadores"),
            ("editar_supervisor", "permiso para editar supervisores"),
            ("editar_trabajador", "permiso para editar trabajadores"),
        ]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"








# Modelos adicionales

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    apellido_paterno = models.CharField(max_length=100, blank=True, null=True)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)
    nombres = models.CharField(max_length=100, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    edad = models.IntegerField(blank=True, null=True)
    nacionalidad = models.CharField(max_length=100, blank=True, null=True)
    sexo = models.CharField(max_length=10, blank=True, null=True)
    fecha_contrato = models.DateField(blank=True, null=True)
    fecha_termino = models.DateField(blank=True, null=True)  # Indefinido si es null
    cargo = models.CharField(max_length=100, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    sindicato = models.CharField(max_length=100, blank=True, null=True)
    fecha_ingreso_sindicato = models.DateField(blank=True, null=True)
    tipo_jornada = models.CharField(max_length=100, blank=True, null=True)

class ContactoUsuario(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    dpto = models.CharField(max_length=10, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    comuna = models.CharField(max_length=100, blank=True, null=True)

class InformacionBancaria(models.Model):
    BANCOS_CHILE = [
        ('banco_estado', 'Banco Estado'),
        ('banco_chile', 'Banco de Chile'),
        ('santander', 'Santander'),
        ('bci', 'BCI'),
        ('itau', 'Itaú'),
        ('scotiabank', 'Scotiabank'),
        ('falabella', 'Banco Falabella'),
    ]
    TIPOS_CUENTA = [
        ('vista', 'Cuenta Vista'),
        ('corriente', 'Cuenta Corriente'),
        ('ahorro', 'Cuenta de Ahorro'),
    ]
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    banco = models.CharField(max_length=50, choices=BANCOS_CHILE, blank=True, null=True)
    tipo_cuenta = models.CharField(max_length=50, choices=TIPOS_CUENTA, blank=True, null=True)
    numero_cuenta = models.CharField(max_length=50, blank=True, null=True)

class InformacionAdicional(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    fecha_primera_cotizacion = models.DateField(blank=True, null=True)
    anos_anteriores = models.IntegerField(blank=True, null=True)
    meses_anteriores = models.IntegerField(blank=True, null=True)
    dias_vacaciones_usados = models.IntegerField(blank=True, null=True)
    fecha_reconocimiento_vacaciones = models.DateField(blank=True, null=True)
    dias_vacaciones_anuales = models.IntegerField(blank=True, null=True)
    ajustes_vacaciones_progresivas = models.TextField(blank=True, null=True)

class SeguroCesantia(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    acogido_seguro = models.BooleanField(default=False)
    afp_recaudadora = models.CharField(max_length=100, blank=True, null=True)
    sueldo_patronal = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    acogido_seguro_accidentes = models.BooleanField(default=False)

class Prevision(models.Model):
    SALUD_OPCIONES = [
        ('fonasa', 'Fonasa'),
        ('isapre', 'Isapre'),
    ]
    REGIMEN_OPCIONES = [
        ('actual', 'Régimen Actual'),
        ('antiguo', 'Régimen Antiguo (IPS)'),
    ]
    AFP_OPCIONES = [
        ('capital', 'Capital'),
        ('cuprum', 'Cuprum'),
        ('habitat', 'Habitat'),
        ('modelo', 'Modelo'),
        ('planvital', 'Planvital'),
        ('provida', 'Provida'),
        ('uno', 'Uno'),
    ]
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    salud = models.CharField(max_length=100, choices=SALUD_OPCIONES, blank=True, null=True)
    regimen = models.CharField(max_length=50, choices=REGIMEN_OPCIONES, blank=True, null=True)
    tasa = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    afp = models.CharField(max_length=100, choices=AFP_OPCIONES, blank=True, null=True)
    pensionado = models.BooleanField(default=False)

class Otros(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    tipo_discapacidad = models.CharField(max_length=100, blank=True, null=True)
    tasa_indemnizacion = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

class AntecedentesConducir(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='antecedentes_conducir')
    tipo_licencia = models.CharField(max_length=50, blank=True, null=True)
    municipalidad = models.CharField(max_length=100, blank=True, null=True)
    fecha_ultimo_control = models.DateField(blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    hoja_vida_conducir = models.TextField(blank=True, null=True)

class ExamenesMutual(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='examenes_mutual')
    tipo_examen = models.CharField(max_length=100, blank=True, null=True)
    fecha_examen = models.DateField(blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)

class GrupoFamiliar(models.Model):
    SEXO_OPCIONES = [
        ('MASCULINO', 'masculino'),
        ('FEMENINO', 'femenino'),
    ]
      
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='grupo_familiar')
    rut_carga = models.CharField(max_length=12, validators=[validar_rut], blank=True, null=True)
    nombre_carga = models.CharField(max_length=100, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    edad = models.IntegerField(blank=True, null=True)
    sexo = models.CharField(max_length=10, blank=True ,choices=SEXO_OPCIONES, null=True)
  

class Capacitacion(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='capacitaciones')
    descripcion = models.TextField(blank=True, null=True)
    horas = models.IntegerField(blank=True, null=True)
    institucion = models.CharField(max_length=100, blank=True, null=True)

class LicenciasMedicas(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='licencias_medicas')
    tipo_accidente = models.CharField(max_length=100, blank=True, null=True)
    clasificacion_accidente = models.CharField(max_length=100, blank=True, null=True)
    fecha_inicio_reposo = models.DateField(blank=True, null=True)
    fecha_termino = models.DateField(blank=True, null=True)
    fecha_alta = models.DateField(blank=True, null=True)
    dias_reposo = models.IntegerField(blank=True, null=True)

class NivelEstudios(models.Model):
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='niveles_estudios')
    nivel_estudios = models.CharField(max_length=100, blank=True, null=True)
    completo = models.BooleanField(default=False)
    ultimo_curso = models.CharField(max_length=100, blank=True, null=True)
    carrera = models.CharField(max_length=100, blank=True, null=True)

class InformacionComplementaria(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    pais_origen = models.CharField(max_length=100, blank=True, null=True)
    pasaporte = models.CharField(max_length=50, blank=True, null=True)
    estado_civil = models.CharField(max_length=50, blank=True, null=True)
    tipo_visa = models.CharField(max_length=50, blank=True, null=True)
    numero_calzado = models.CharField(max_length=10, blank=True, null=True)
    talla_ropa = models.CharField(max_length=10, blank=True, null=True)
    grupo_sanguineo = models.CharField(max_length=10, blank=True, null=True)
    alergico = models.TextField(blank=True, null=True)
    personal_destacado = models.BooleanField(default=False)







    


class DiaHabilitado(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='dias_habilitados')
    fecha = models.DateField()
    habilitado = models.BooleanField(default=True)  # True si el día está habilitado, False si está bloqueado

    class Meta:
        unique_together = ('usuario', 'fecha')  # Evita duplicados por usuario y fecha

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha} - {'Habilitado' if self.habilitado else 'Bloqueado'}"








class AuditoriaAcceso(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    exito = models.BooleanField(default=False)
    motivo = models.TextField(blank=True)