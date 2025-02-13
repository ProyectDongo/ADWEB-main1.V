import re
from django.core.exceptions import ValidationError

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
