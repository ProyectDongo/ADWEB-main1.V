from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.utils.crypto import get_random_string
from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from WEB.models import *
from django.db import models

# Decorador para verificar si el usuario tiene un rol específico------------#
def permiso_requerido(permiso):                                             #
    def decorator(view_func):                                               #
        @wraps(view_func)                                                   #  
        def _wrapped_view(request, *args, **kwargs):                        #
            if request.user.has_perm(permiso):                              #
                return view_func(request, *args, **kwargs)                  #
            else:                                                           #                                  
                return render(request, 'error/error.html', status=403)      #
        return _wrapped_view                                                #
    return decorator                                                        #
                                                                            #           
#----------------------------------------------------------------------------
# implementar a futuro
# Crear un usuario supervisor al registrar una empresa
#@receiver(post_save, sender=RegistroEmpresas)

def crear_supervisor(sender, instance, created, **kwargs):

    if created:

        temp_password = get_random_string(10)
        supervisor = Usuario.objects.create(

            username=f"sup_{instance.rut}",

            role='supervisor',

            empresa=instance,

            nombre=f"Supervisor {instance.nombre}",

            email=instance.mail_contacto,

            is_active=True
        )
        supervisor.set_password(temp_password)
        supervisor.save()
        # Enviar correo con temp_password (implementar según necesidad)

#---------------------------------------------------------------------------
# implementar a futuro
# Actualizar el límite de usuarios de una empresa al crear o eliminar una vigencia

#@receiver([post_save, post_delete], sender=VigenciaPlan)

def actualizar_limite_usuarios(sender, instance, **kwargs):

    empresa = instance.empresa

    total = empresa.vigencias.aggregate(

        total=models.Sum('plan__max_usuarios')

    )['total'] or 0

    empresa.limite_usuarios = total

    empresa.save(update_fields=['limite_usuarios'])
    

#---------------------------------------------------------------------------