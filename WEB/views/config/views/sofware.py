from WEB.models import *
from WEB.forms import *
from django.shortcuts import render, redirect
from WEB.decorators import permiso_requerido
from django.contrib.auth.decorators import login_required

@login_required
@permiso_requerido("crear_admin")
def crear_admin(request):
    """
    Vista para creación de nuevos usuarios administradores.
    
    :param request: HttpRequest
    :return: Renderizado de formulario o redirección tras éxito
    """
    if request.method == 'POST':
        form = AdminForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AdminForm()
    return render(request, 'side_menu/Sofware/crear_admin.html', {'form': form})

@login_required
@permiso_requerido("crear_supervisor")
def crear_supervisor(request):
    """
    Vista para la creación de supervisores.
    """
    if request.method == 'POST':
        form = SupervisorForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()  # Aquí se asigna el rol y se guardan los permisos seleccionados
            return redirect('configuracion_home')
    else:
        form = SupervisorForm(user=request.user)
    return render(request, 'side_menu/Sofware/crear_supervisor.html', {'form': form})

@login_required
@permiso_requerido("crear_trabajador")
def crear_trabajador(request):
    """
    Vista para creación de nuevos usuarios trabajadores.
    
    :param request: HttpRequest
    :return: Renderizado de formulario o redirección tras éxito
    """
    if request.method == 'POST':
        form = TrabajadorForm(request.POST, user=request.user)
        if form.is_valid():
            trabajador = form.save(commit=False)
            trabajador.role = 'trabajador'
            if request.user.role != 'admin':
                trabajador.empresa = request.user.empresa
            trabajador.save()
            form.save_m2m()
            if request.user.role == 'admin':
                return redirect('listar_empresas')
            else:
                return redirect('detalles_empresa', empresa_id=trabajador.empresa.id)
    else:
        form = TrabajadorForm(user=request.user)
    return render(request, 'side_menu/Sofware/crear_trabajador.html', {'form': form})
