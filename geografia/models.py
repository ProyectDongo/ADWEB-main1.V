from django.db import models

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


#
