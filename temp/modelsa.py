from wsgiref.validate import validator
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Max
from django.utils import timezone
from django.conf import settings
from ..WEB.views.scripts.validators import validar_rut
from django.forms import modelformset_factory
from django.db.models import  Sum
from django.urls import reverse



class Region(models.Model):
    """
    Modelo que representa una región geográfica.

    Atributos:
        nombre (CharField): Nombre de la región, limitado a 100 caracteres.
    """
    nombre = models.CharField(max_length=100)

    def __str__(self):
        """
        Retorna la representación en cadena de la región.

        :return: Nombre de la región.
        """
        return self.nombre


class Provincia(models.Model):
    """
    Modelo que representa una provincia, vinculada a una región específica.

    Atributos:
        nombre (CharField): Nombre de la provincia, limitado a 100 caracteres.
        region (ForeignKey): Relación a la región a la que pertenece la provincia. 
                             Si se elimina la región, se eliminarán sus provincias asociadas.
    """
    nombre = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        """
        Retorna la representación en cadena de la provincia.

        :return: Cadena con el formato "Nombre (Región)".
        """
        return f"{self.nombre} ({self.region})"


class Comuna(models.Model):
    """
    Modelo que representa una comuna, perteneciente a una provincia.

    Atributos:
        nombre (CharField): Nombre de la comuna, limitado a 100 caracteres.
        provincia (ForeignKey): Relación a la provincia a la que pertenece la comuna. 
                                Se elimina en cascada junto con la provincia.
    """
    nombre = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE)

    def __str__(self):
        """
        Retorna la representación en cadena de la comuna.

        :return: Cadena con el formato "Nombre (Provincia)".
        """
        return f"{self.nombre} ({self.provincia})"


class Plan(models.Model):
    """
    Modelo que representa un plan de suscripción o servicio.

    Atributos:
        estado (CharField): Estado del plan, con opciones 'habilitado' o 'suspendido'.
                            Por defecto es 'habilitado'.
        nombre (CharField): Nombre descriptivo del plan, limitado a 100 caracteres.
        max_usuarios (PositiveIntegerField): Número máximo de usuarios permitidos en este plan.
        valor (DecimalField): Valor monetario del plan, con hasta 10 dígitos y 2 decimales.
        codigo (CharField): Código único identificador del plan, limitado a 20 caracteres.
        activo (BooleanField): Indica si el plan se encuentra activo. Valor por defecto True.
        descripcion (TextField): Campo opcional para detallar información adicional del plan.

    Meta:
        verbose_name: "Plan"
        verbose_name_plural: "Planes"

    Método especial:
        __str__: Devuelve una representación en cadena del plan incluyendo el nombre y el máximo de usuarios.
    """
    ESTADOS_CHOICES = [
        ('habilitado', 'Habilitado'),
        ('suspendido', 'Plan Suspendido'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES, default='habilitado')
    nombre = models.CharField(max_length=100)
    max_usuarios = models.PositiveIntegerField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    codigo = models.CharField(max_length=20, unique=True)
    activo = models.BooleanField(default=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Planes"

    def __str__(self):
        """
        Retorna la representación en cadena del plan.

        :return: Cadena con el formato "Nombre (U: Máximo de usuarios)".
        """
        return f"{self.nombre} (U: {self.max_usuarios})"


class RegistroEmpresas(models.Model):
    """
    Modelo que representa el registro de una empresa en el sistema.

    Este modelo almacena información detallada sobre una empresa, incluyendo datos
    de identificación, ubicación, contacto, plan contratado y métodos de pago.

    Atributos:
        codigo_cliente (CharField): Código único asignado al cliente. Si no se
            proporciona, se genera automáticamente en el método save.
        fecha_ingreso (DateField): Fecha de ingreso de la empresa, se asigna
            automáticamente al crearse el registro.
        rut (CharField): RUT de la empresa, debe ser único y se valida mediante la
            función 'validar_rut'.
        nombre (CharField): Nombre de la empresa.
        giro (CharField): Giro o actividad principal de la empresa.
        direccion (CharField): Dirección de la empresa.
        numero (CharField): Número de la dirección.
        oficina (CharField): Oficina o departamento (opcional).
        region (ForeignKey): Región a la que pertenece la empresa. Se usa PROTECT
            para evitar borrados accidentales.
        provincia (ForeignKey): Provincia a la que pertenece la empresa.
        comuna (ForeignKey): Comuna a la que pertenece la empresa.
        telefono (CharField): Teléfono fijo de la empresa.
        celular (CharField): Teléfono celular de la empresa (opcional).
        email (EmailField): Correo electrónico de la empresa.
        web (URLField): Página web de la empresa (opcional).
        vigente (BooleanField): Indica si la empresa está activa.
        estado (CharField): Estado de la empresa, con opciones ('aldia', 'atrasado', 'suspendido'),
            por defecto 'aldia'.

        rut_representante (CharField): RUT del representante de la empresa, validado con 'validar_rut'.
        nombre_representante (CharField): Nombre del representante legal de la empresa.

        nombre_contacto (CharField): Nombre de la persona de contacto.
        celular_contacto (CharField): Teléfono celular de la persona de contacto.
        mail_contacto (EmailField): Correo electrónico de la persona de contacto.

        plan_contratado (ForeignKey): Plan contratado por la empresa, relacionado con el modelo 'Plan'.
            Se utiliza PROTECT para evitar borrados accidentales. La relación se identifica con el nombre 'empresas'.
        limite_usuarios (PositiveIntegerField): Límite de usuarios permitido según el plan contratado.
        
        eliminada (BooleanField): Indica si la empresa ha sido eliminada lógicamente.
        metodo_pago (CharField): Método de pago con opciones ('manual', 'automatico'), por defecto 'manual'.
        frecuencia_pago (CharField): Frecuencia de pago con opciones ('mensual', 'anual') (opcional).
        banco (CharField): Banco asociado al método de pago (opcional).
        tipo_cuenta (CharField): Tipo de cuenta bancaria con opciones ('ahorro', 'corriente') (opcional).
        numero_cuenta (CharField): Número de cuenta bancaria (opcional).

    Meta:
        verbose_name: "Empresa"
        verbose_name_plural: "Empresas"

    Métodos:
        __str__: Retorna el nombre de la empresa.
        save: Sobrescribe el método de guardado para generar automáticamente el 'codigo_cliente'
              y actualizar el 'limite_usuarios' en función del plan contratado.
    """
    ESTADO_CHOICES = [
        ('aldia', 'Al día'),
        ('atrasado', 'Atrasado'),
        ('suspendido', 'Suspendido'),
    ]
    
    codigo_cliente = models.CharField(max_length=20, unique=True)
    fecha_ingreso = models.DateField(auto_now_add=True)
    rut = models.CharField(max_length=13, unique=True, validators=[validar_rut])
    nombre = models.CharField(max_length=100)
    giro = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    numero = models.CharField(max_length=20)
    oficina = models.CharField(max_length=20, blank=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    provincia = models.ForeignKey(Provincia, on_delete=models.PROTECT)
    comuna = models.ForeignKey(Comuna, on_delete=models.PROTECT)
    telefono = models.CharField(max_length=20)
    celular = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    web = models.URLField(blank=True)
    vigente = models.BooleanField(default=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='aldia')
    
    rut_representante = models.CharField(max_length=12, validators=[validar_rut])
    nombre_representante = models.CharField(max_length=100)
    
    nombre_contacto = models.CharField(max_length=100)
    celular_contacto = models.CharField(max_length=20)
    mail_contacto = models.EmailField()
    
    plan_contratado = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='empresas')
    limite_usuarios = models.PositiveIntegerField(default=0)

    eliminada = models.BooleanField(default=False, verbose_name="Eliminada")  # Nuevo campo
    metodo_pago = models.CharField(
        max_length=20, 
        choices=[('manual', 'Manual'), ('automatico', 'Automático')], 
        default='manual'
    )
    frecuencia_pago = models.CharField(
        max_length=20, 
        choices=[('mensual', 'Mensual'), ('anual', 'Anual')], 
        blank=True, null=True
    )
    banco = models.CharField(max_length=100, blank=True, null=True)
    tipo_cuenta = models.CharField(
        max_length=20, 
        choices=[('ahorro', 'Ahorro'), ('corriente', 'Corriente')], 
        blank=True, null=True
    )
    numero_cuenta = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self):
        """
        Retorna la representación en cadena de la empresa.

        :return: El nombre de la empresa.
        """
        return self.nombre

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para realizar acciones adicionales antes de guardar:

        - Genera automáticamente el 'codigo_cliente' si aún no está asignado, utilizando el máximo ID
          actual y formateándolo con el prefijo 'CLI-' seguido de un número de 6 dígitos.
        - Actualiza el campo 'limite_usuarios' en función del 'max_usuarios' definido en el plan contratado.

        Luego, llama al método save del padre para almacenar el registro en la base de datos.

        :param args: Argumentos posicionales.
        :param kwargs: Argumentos con nombre.
        """
        if not self.codigo_cliente:
            ultimo_id = RegistroEmpresas.objects.aggregate(Max('id'))['id__max'] or 0
            self.codigo_cliente = f"CLI-{ultimo_id + 1:06d}"
        
        if self.plan_contratado:
            self.limite_usuarios = self.plan_contratado.max_usuarios
            
        super().save(*args, **kwargs)

class Usuario(AbstractUser):
    """
    Modelo que extiende AbstractUser para representar a un usuario en el sistema.

    Este modelo incorpora campos adicionales a los definidos en AbstractUser para
    manejar roles específicos (Administrador, Supervisor, Trabajador), la asociación
    a una empresa y permisos adicionales personalizados.

    Atributos:
        role (CharField): Rol del usuario, con opciones:
            - 'admin' para Administrador,
            - 'supervisor' para Supervisor,
            - 'trabajador' para Trabajador.
            Valor por defecto: 'trabajador'.
        empresa (ForeignKey): Relación con el modelo RegistroEmpresas, que define la empresa
            a la que pertenece el usuario. Este campo es opcional.
        permisos (ManyToManyField): Relación con el modelo RegistroPermisos para asignar
            permisos personalizados al usuario.
        rut (CharField): RUT del usuario, debe ser único y se valida mediante la función 'validar_rut'.
            Se permite que esté en blanco.
        apellidoM (CharField): Apellido materno del usuario (opcional).
        nombre (CharField): Nombre del usuario.
        celular (CharField): Número de celular del usuario (opcional).
        email (EmailField): Correo electrónico del usuario.
        groups (ManyToManyField): Grupos a los que pertenece el usuario.
        user_permissions (ManyToManyField): Permisos específicos asignados al usuario.

    Meta:
        verbose_name: "Usuario"
        verbose_name_plural: "Usuarios"

    Métodos:
        __str__: Retorna una representación en cadena del usuario, que incluye el nombre
                 de usuario y la descripción de su rol.
    """
    ROLES = (
        ('admin', 'Administrador'),
        ('supervisor', 'Supervisor'),
        ('trabajador', 'Trabajador'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='trabajador')
    empresa = models.ForeignKey(
        RegistroEmpresas, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name="usuarios"
    )
    permisos = models.ManyToManyField("RegistroPermisos", blank=True, related_name='usuarios')
    rut = models.CharField(max_length=12, unique=True, validators=[validar_rut], blank=True)
    apellidoM = models.CharField(max_length=12, blank=True)
    nombre = models.CharField(max_length=100)
    celular = models.CharField(max_length=20, blank=True)
    email = models.EmailField()

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='usuario_groups',
        help_text='Grupos a los que pertenece el usuario'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='usuario_permissions',
        help_text='Permisos específicos para este usuario'
    )

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        """
        Retorna una representación en cadena del usuario.

        :return: Cadena con el formato "username (Rol)", donde Rol es la descripción del rol.
        """
        return f"{self.username} ({self.get_role_display()})"


class RegistroPermisos(models.Model):
    """
    Modelo que representa un permiso personalizado para los usuarios.

    Este modelo se utiliza para definir permisos adicionales que pueden asignarse
    a los usuarios, complementando los permisos predeterminados del sistema.

    Atributos:
        nombre (CharField): Nombre del permiso.
        descripcion (TextField): Descripción detallada del permiso (opcional).

    Métodos:
        __str__: Retorna el nombre del permiso.
    """
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        """
        Retorna la representación en cadena del permiso.

        :return: Nombre del permiso.
        """
        return self.nombre


class RegistroEntrada(models.Model):
    """
    Modelo que representa el registro de entrada y salida de un trabajador.

    Este modelo almacena la hora en la que un trabajador inicia y finaliza su jornada,
    y permite indicar si se permite registrar otra entrada (por ejemplo, en caso de turnos múltiples).

    Atributos:
        trabajador (ForeignKey): Relación con el usuario (trabajador) que realiza el registro.
                                  Se asocia mediante settings.AUTH_USER_MODEL y se elimina en cascada.
        hora_entrada (DateTimeField): Fecha y hora en que se registra la entrada.
                                      Se asigna automáticamente al crearse el registro.
        hora_salida (DateTimeField): Fecha y hora en que se registra la salida. Es opcional.
        permitir_otra_entrada (BooleanField): Indica si se permite registrar otra entrada para el mismo trabajador.
    """
    trabajador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='entradas'
    )
    hora_entrada = models.DateTimeField(auto_now_add=True)
    hora_salida = models.DateTimeField(null=True, blank=True)
    permitir_otra_entrada = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Registro de Entrada"
        verbose_name_plural = "Registros de Entrada"
        ordering = ['-hora_entrada']

    def __str__(self):
        """
        Retorna una representación en cadena del registro de entrada.

        :return: Cadena con el formato "username - AAAA-MM-DD HH:MM", donde 'username' es el nombre
                 de usuario del trabajador y la fecha/hora corresponde a 'hora_entrada'.
        """
        return f"{self.trabajador.username} - {self.hora_entrada.strftime('%Y-%m-%d %H:%M')}"


@receiver(post_save, sender=RegistroEntrada)
def notificar_registro_entrada(sender, instance, created, **kwargs):
    """
    Función receptora para la señal post_save del modelo RegistroEntrada.

    Cuando se crea un nuevo registro de entrada, esta función notifica (mediante un print)
    que se ha registrado la entrada para el trabajador asociado, mostrando el nombre de usuario
    y la hora de entrada.

    Parámetros:
        sender: La clase del modelo que envió la señal (RegistroEntrada).
        instance: La instancia del modelo RegistroEntrada que se acaba de guardar.
        created (bool): Indica si la instancia fue creada (True) o actualizada (False).
        **kwargs: Argumentos adicionales de la señal.
    """
    if created:
        print(f"Entrada registrada para {instance.trabajador.username} a las {instance.hora_entrada}")


class VigenciaPlan(models.Model):
    """
    Modelo que representa la vigencia de un plan contratado por una empresa.

    Este modelo registra la duración y las condiciones económicas de un plan contratado,
    permitiendo calcular el monto final del plan después de aplicar un descuento.

    Atributos:
        empresa (ForeignKey): Relación con el modelo RegistroEmpresas que contrata el plan.
                                Se elimina en cascada.
        plan (ForeignKey): Relación con el modelo Plan contratado. Se utiliza PROTECT para evitar borrados accidentales.
        fecha_inicio (DateField): Fecha de inicio de la vigencia del plan. Por defecto, la fecha actual.
        fecha_fin (DateField): Fecha de término de la vigencia, opcional.
        monto_plan (DecimalField): Valor base del plan.
        descuento (DecimalField): Porcentaje de descuento a aplicar al valor del plan. Valor por defecto: 0.
        monto_final (DecimalField): Valor final del plan luego de aplicar el descuento.
        codigo_plan (CharField): Código único identificador del plan.
        estado (CharField): Estado de la vigencia, con opciones:
            - 'indefinido' para una vigencia sin fecha definida.
            - 'mensual' para una vigencia mensual.
            - 'suspendido' para una vigencia suspendida.

    Meta:
        verbose_name: "Vigencia de Plan"
        verbose_name_plural: "Vigencias de Planes"
        ordering: Ordena los registros por 'fecha_inicio' en orden descendente.

    Métodos:
        __str__: Retorna una representación en cadena de la vigencia, mostrando la empresa, el nombre del plan y la fecha de inicio.
        calcular_monto: Calcula y actualiza el 'monto_final' del plan aplicando el descuento.
                        Si el plan no tiene un valor definido, lanza un ValueError.
        save: Sobrescribe el método save para calcular el monto final antes de guardar la instancia.
    """
    TIPO_DURACION = [
        ('indefinido', 'Indefinido'),
        ('mensual', 'Mensual'),
        ('suspendido', 'Suspendido'),
    ]
    empresa = models.ForeignKey(
        RegistroEmpresas,
        on_delete=models.CASCADE,
        related_name='vigencias'
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_fin = models.DateField(null=True, blank=True)
    monto_plan = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    monto_final = models.DecimalField(max_digits=10, decimal_places=2)
    codigo_plan = models.CharField(max_length=50, unique=True)
    estado = models.CharField(max_length=20, choices=TIPO_DURACION, default='indefinido')

    class Meta:
        verbose_name = "Vigencia de Plan"
        verbose_name_plural = "Vigencias de Planes"
        ordering = ['-fecha_inicio']

    def __str__(self):
        """
        Retorna la representación en cadena de la vigencia del plan.

        :return: Cadena con el formato "Empresa - Nombre del Plan (Fecha de inicio)".
        """
        return f"{self.empresa} - {self.plan.nombre} ({self.fecha_inicio})"

    def calcular_monto(self):
        """
        Calcula y actualiza el monto final del plan aplicando el descuento.

        El cálculo se realiza de la siguiente manera:
            - Se verifica que el valor del plan esté definido.
            - Se convierte el porcentaje de descuento en decimal.
            - Se establece 'monto_plan' con el valor base del plan.
            - Se calcula 'monto_final' multiplicando 'monto_plan' por (1 - descuento_decimal).

        :return: El monto final calculado.
        :raises ValueError: Si el valor del plan (plan.valor) no está definido.
        """
        if self.plan.valor is None:
            raise ValueError("El plan no tiene un valor definido.")

        descuento_decimal = self.descuento / 100
        self.monto_plan = self.plan.valor
        self.monto_final = self.monto_plan * (1 - descuento_decimal)
        return self.monto_final

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para calcular el monto final antes de guardar la instancia.

        Llama al método 'calcular_monto' para actualizar 'monto_final' y luego procede
        a guardar la instancia utilizando el método save del padre.

        :param args: Argumentos posicionales.
        :param kwargs: Argumentos con nombre.
        """
        self.calcular_monto()
        super().save(*args, **kwargs)

class HistorialCambios(models.Model):
    """
    Modelo que representa un registro en el historial de cambios de una empresa.

    Este modelo almacena información sobre modificaciones o acciones realizadas en una
    empresa, incluyendo el usuario que realizó el cambio, la fecha en que se efectuó y una
    descripción detallada del cambio.

    Atributos:
        empresa (ForeignKey): Relación con el modelo RegistroEmpresas, representa la empresa
            a la que corresponde el cambio. Se elimina en cascada.
        usuario (ForeignKey): Relación con el modelo de usuario (settings.AUTH_USER_MODEL) que realizó
            el cambio. Si el usuario es eliminado, se asigna el valor null.
        fecha (DateTimeField): Fecha y hora en que se registra el cambio, asignada automáticamente al crear el registro.
        descripcion (TextField): Descripción detallada del cambio realizado.

    Meta:
        verbose_name: "Historial de Cambios"
        verbose_name_plural: "Historial de Cambios"
        ordering: Lista los registros en orden descendente por fecha.

    Métodos:
        __str__: Retorna una representación en cadena del historial en formato "AAAA-MM-DD HH:MM - usuario".
    """
    empresa = models.ForeignKey(RegistroEmpresas, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()

    class Meta:
        verbose_name = "Historial de Cambios"
        verbose_name_plural = "Historial de Cambios"
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.fecha.strftime('%Y-%m-%d %H:%M')} - {self.usuario}"



    
class Cobro(models.Model):
    empresa = models.ForeignKey(RegistroEmpresas, on_delete=models.CASCADE, related_name='cobros')
    vigencia_plan = models.ForeignKey(
        VigenciaPlan, 
        on_delete=models.CASCADE, 
        related_name='cobros_relacionados',  # Cambiado para evitar conflicto de nombres
        null=True, 
        blank=True
    )
    # Agregar campo ManyToMany para asociar múltiples planes
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    def planes_asociados(self):
        if self.vigencia_plan:
            return [self.vigencia_plan]
        return self.vigencias_planes.all()
    vigencias_planes = models.ManyToManyField(VigenciaPlan, related_name='cobros_planes', blank=True)
    
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(
        max_length=20,
        choices=[('pendiente', 'Pendiente'), ('pagado', 'Pagado')],
        default='pendiente'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def monto_pagado(self):
        return self.pagos.aggregate(total=Sum('monto'))['total'] or 0

    def monto_restante(self):
        return self.monto_total - self.monto_pagado()
    
    def actualizar_estado(self):
        if self.monto_restante() <= 0:
            self.estado = 'pagado'
            self.save()

    def __str__(self):
        return f"Cobro {self.id} - {self.vigencia_plan.plan.nombre if self.vigencia_plan else 'Todos'}"
    
class Pago(models.Model):
    """
    Modelo que representa un pago realizado por una empresa.
    Se registran distintos métodos de pago (incluyendo abono y cobranza) y se añaden
    campos de auditoría y observaciones para un registro detallado.
    """
    METODO_PAGO_CHOICES = [
        ('automatico', 'Automático'),
        ('cheque', 'Cheque'),
        ('tarjeta', 'Tarjeta'),
        ('credito', 'Crédito'),
        ('debito', 'Débito'),
        ('abono', 'Abono'),
        ('efectivo', 'Efectivo'),  
    
    ]
    empresa = models.ForeignKey(RegistroEmpresas, on_delete=models.CASCADE, related_name='pagos')
    vigencia_planes = models.ManyToManyField(VigenciaPlan, related_name='pagos_asociados')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField() 
    metodo = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
    comprobante = models.FileField(upload_to='comprobantes/', blank=True, null=True)
    pagado = models.BooleanField(default=False)
    cobro = models.ForeignKey(Cobro, on_delete=models.CASCADE, related_name='pagos', null=True)
    
    # CAMBIO: Campos de auditoría para tener un registro detallado
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # CAMBIO: Campo de observaciones para comentarios internos o incidencias
    observaciones = models.TextField(blank=True, null=True)
    def save(self, *args, **kwargs):
        if self.cobro and not self.pk:
            self.empresa = self.cobro.empresa
        super().save(*args, **kwargs)
    def __str__(self):
        return f"Pago {self.id} - {self.empresa.nombre} ({self.fecha_pago})"

class HistorialPagos(models.Model):
    """
    Modelo para llevar un registro detallado de las operaciones y cambios en los pagos.
    Permite rastrear cada acción (creación, actualización, cambio de estado) realizada sobre un pago.
    """
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name='historial')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField()

    def __str__(self):
        return f"Historial Pago {self.pago.id} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"

class EmailNotification(models.Model):
    subject = models.CharField(max_length=255)
    sender = models.CharField(max_length=255)
    received_date = models.DateTimeField()
    procesado = models.BooleanField(default=False)  # Para marcar si ya se revisó el comprobante

    def __str__(self):
        return f"{self.subject} - {self.sender}"
    

class HistorialNotificaciones(models.Model):
    empresa = models.ForeignKey(RegistroEmpresas, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Historial de Notificaciones"
        ordering = ['-fecha_envio']