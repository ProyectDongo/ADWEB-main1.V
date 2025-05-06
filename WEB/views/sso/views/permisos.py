from WEB.models import *
from WEB.forms.secure.forms import *
from django.shortcuts import render, redirect
from WEB.views.scripts import *
from django.contrib.auth.decorators import login_required


@login_required
@permiso_requerido("web.crear_permiso")
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
    return render(request, 'admin/permisos/crear/crear_permiso.html', {'form': form})


@login_required
@permiso_requerido("WEB.lista_permisos")
def lista_permisos(request):
    """
    Lista todos los permisos registrados.
    
    :param request: HttpRequest
    :return: Renderizado de template con lista de permisos
    """
    permisos =request.user.user_permissions.all()
    return render(request, 'admin/permisos/lista/listas_permisos.html', {'permisos': permisos})
