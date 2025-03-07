from django.db import models
from django.utils import timezone
from .empresa import RegistroEmpresas


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
