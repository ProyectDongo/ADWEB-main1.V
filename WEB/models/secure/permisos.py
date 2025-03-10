
from django.db import models


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
