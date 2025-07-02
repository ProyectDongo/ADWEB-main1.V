
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator




def validar_rut(value):
    rut = value.upper().replace(".", "").replace("-", "")
    rut_body = rut[:-1]
    rut_verifier = rut[-1]

    try:
        rut_body = int(rut_body)
    except ValueError:
        raise ValidationError("El RUT debe contener solo números en la parte del cuerpo.")

    suma = 0
    multiplo = 2

    for digit in reversed(str(rut_body)):
        suma += int(digit) * multiplo
        multiplo = 2 if multiplo == 7 else multiplo + 1

    mod = 11 - (suma % 11)
    if mod == 11:
        mod = '0'
    elif mod == 10:
        mod = 'K'
    else:
        mod = str(mod)

    if mod != rut_verifier:
        raise ValidationError("El RUT ingresado no es válido.")

phone_validator = RegexValidator(
    regex=r'^(\+56\s*)?[29]\d{8}$',  # Expresión regular corregida
    message="Formato válido: 2XXXXXXXX, +562XXXXXXXX, 9XXXXXXXX o +569XXXXXXXX"
)


mobile_validator = RegexValidator(
    regex=r'^(\+56)?\s*9\d{8}$',  # Permite espacios después de +56
    message="Formato válido: 9XXXXXXXX o +569XXXXXXXX"
)
def format_rut(rut):
    """
    Recibe un RUT sin formatear (ej: '107091637') y lo transforma en el formato con puntos y guion (ej: '10.709.163-7').
    """
    # Elimina cualquier punto o guion existente
    rut = rut.replace('.', '').replace('-', '')
    if not rut or len(rut) < 2:
        return rut
    # Se asume que el último dígito es el dígito verificador (DV)
    numeros, dv = rut[:-1], rut[-1]
    numeros_formateado = ""
    # Agrupa de derecha a izquierda en bloques de tres dígitos
    while len(numeros) > 3:
        numeros_formateado = "" + numeros[-3:] + numeros_formateado
        numeros = numeros[:-3]
    numeros_formateado = numeros + numeros_formateado
    return f"{numeros_formateado}-{dv}"