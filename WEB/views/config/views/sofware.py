from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from WEB.views.scripts import *
from WEB.forms import AdminForm, SupervisorForm, TrabajadorForm

@login_required
@permiso_requerido("WEB.crear_admin")
def crear_admin(request):
    if request.method == 'POST':
        form = AdminForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('configuracion_home')
        else:
            print(form.errors)  # Depuración de errores
    else:
        form = AdminForm()
    return render(request, 'admin/Sofware/admin/crear_admin.html', {'form': form})

@login_required
@permiso_requerido("WEB.crear_supervisor")
def crear_supervisor(request):
    if request.method == 'POST':
        form = SupervisorForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('configuracion_home')
        else:
            print(form.errors)  # Depuración de errores
    else:
        form = SupervisorForm(user=request.user)
    return render(request, 'admin/Sofware/supervisor/crear_supervisor.html', {'form': form})

@login_required
@permiso_requerido("WEB.crear_trabajador")
def crear_trabajador(request):
    if request.method == 'POST':
        form = TrabajadorForm(request.POST, user=request.user)
        if form.is_valid():
            trabajador = form.save(commit=False)
            if request.user.role != 'admin':
                trabajador.empresa = request.user.empresa
            trabajador.save()
            form.save_m2m()
            if request.user.role == 'admin':
                return redirect('listar_empresas')
            else:
                return redirect('detalles_empresa', empresa_id=trabajador.empresa.id)
        else:
            print(form.errors)  # Depuración de errores
    else:
        form = TrabajadorForm(user=request.user)
    return render(request, 'admin/Sofware/user/crear_trabajador.html', {'form': form})