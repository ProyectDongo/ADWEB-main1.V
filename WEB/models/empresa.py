from django.db import models
from .region import Region, Provincia, Comuna
from WEB.validators import validar_rut
from django.utils import timezone

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
            ultimo_id = RegistroEmpresas.objects.aggregate(max('id'))['id__max'] or 0
            self.codigo_cliente = f"CLI-{ultimo_id + 1:06d}"
        
        if self.plan_contratado:
            self.limite_usuarios = self.plan_contratado.max_usuarios
            
        super().save(*args, **kwargs)

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