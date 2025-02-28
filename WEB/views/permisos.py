from WEB.models import *
from WEB.forms import *
from django.shortcuts import render, redirect
from WEB.decorators import permiso_requerido
from django.contrib.auth.decorators import login_required


@login_required
@permiso_requerido("crear_permiso")
def crear_permiso(request):
    """
    Vista para creación de nuevos permisos de usuario.
    
    :param request: HttpRequest
    :return: Renderizado de formulario o redirección tras éxito
    """
    if request.method == 'POST':
        form = PermisoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_permisos')
    else:
        form = PermisoForm()
    return render(request, 'side_menu/permisos/crear/crear_permiso.html', {'form': form})

@login_required
@permiso_requerido("lista_permisos")
def lista_permisos(request):
    """
    Lista todos los permisos registrados.
    
    :param request: HttpRequest
    :return: Renderizado de template con lista de permisos
    """
    permisos = RegistroPermisos.objects.all()
    return render(request, 'side_menu/permisos/lista/listas_permisos.html', {'permisos': permisos})
