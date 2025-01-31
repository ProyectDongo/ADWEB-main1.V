from django.shortcuts import render,redirect
from django.contrib.auth import logout
# Create your views here.
from django.contrib.auth.decorators import login_required
from .forms import EmpresaForm, PermisoForm, AdminForm, SupervisorForm, TrabajadorForm, SupervisorEditForm, TrabajadorEditForm
from .models import RegistroEmpresas,Usuario,RegistroPermisos
from django.shortcuts import get_object_or_404
from django.contrib import messages
#redirige a la pagina por defecto
@login_required
def redirect_after_login(request):
    print("Redirigiendo después del login...")
    if not hasattr(request.user, 'role'):
        print("Error: Usuario no tiene un rol definido")
        return redirect('pagina_por_defecto')  # Página genérica si el rol no existe
    
    role = request.user.role
    print(f"Usuario autenticado: {request.user.username}, Rol: {role}")

    if role == 'admin':
        print("Redirigiendo a admin_home")
        return redirect('admin_home')
    elif role == 'supervisor':
        print("Redirigiendo a supervisor_home")
        return redirect('supervisor_home')
    elif role == 'trabajador':
        print("Redirigiendo a trabajador_home")
        return redirect('trabajador_home')

    print("Redirigiendo a página por defecto")
    return redirect('pagina_por_defecto')

#requiere estar logueado
#luego redirige a la pagina de inicio correspondiente al rol del usuario
@login_required
def admin_home(request):
    return render(request, 'home/admin_home.html')

@login_required
def supervisor_home(request):
    return render(request, 'home/supervisor_home.html')

@login_required
def trabajador_home(request):
    return render(request, 'home/trabajador.home.html')

#redigire al login
def login(request):
    return render(request, 'login/login.html')


#redirige al logout cierra sesion
def logout_view(request):
    logout(request)
    return redirect('login')

# redirige a la apgin para crear empresas
@login_required
def crear_empresa(request):
    if request.method == 'POST':
        form = EmpresaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_empresas')
    else:
        form = EmpresaForm()
    return render(request, 'formularios/crear/crear_empresa.html', {'form': form})

#redirige a la pagina para crear permisos
@login_required
def crear_permiso(request):
    if request.method == 'POST':
        form = PermisoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_permisos')
    else:
        form = PermisoForm()
    return render(request, 'formularios/crear/crear_permiso.html', {'form': form})

#redirige a la pagina para crear admins
@login_required
def crear_admin(request):
    if request.method == 'POST':
        form = AdminForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_empresas')
    else:
        form = AdminForm()
    return render(request, 'formularios/crear/crear_admin.html', {'form': form})

#redirige a la pagina para crear supervisores
@login_required
def crear_supervisor(request):
    if request.method == 'POST':
        form = SupervisorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_empresas')
    else:
        form = TrabajadorForm()
    return render(request, 'formularios/crear/crear_supervisor.html', {'form': form})

#redirige a la pagina para crear trabajadores
@login_required
def crear_trabajador(request):
    if request.method == 'POST':
        form = TrabajadorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_empresas')
    else:
        form = TrabajadorForm()
    return render(request, 'formularios/crear/crear_trabajador.html', {'form': form})

#redirige a la pagina de lista de usuarios  
@login_required
def lista_empresas(request):
    empresas = RegistroEmpresas.objects.all()
    context = {
        'empresas': empresas,
    }
    return render(request, 'listas/lista_empresas.html', context)

#redirige a la pagina de detalles de la empresa
@login_required
def detalles_empresa(request, empresa_id):
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    supervisores = empresa.usuarios.filter(role='supervisor')
    trabajadores = empresa.usuarios.filter(role='trabajador')
    context = {
        'empresa': empresa,
        'supervisores': supervisores,
        'trabajadores': trabajadores,
    }
    return render(request, 'listas/detalles_empresa.html', context)

#redirige a la pagina para editar supervisores
@login_required
def editar_supervisor(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id, role='supervisor')
    empresa_id = usuario.empresa.id
    if request.method == 'POST':
        form = SupervisorEditForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('detalles_empresa', empresa_id=usuario.empresa.id)
    else:
        form = SupervisorEditForm(instance=usuario)
    return render(request, 'formularios/edit/editar_supervisor.html', {'form': form, 'empresa_id': empresa_id})

#redirige a la pagina para editar trabajadores
@login_required
def editar_trabajador(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id, role='trabajador')
    empresa_id = usuario.empresa.id
    if request.method == 'POST':
        form = TrabajadorEditForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('detalles_empresa', empresa_id=usuario.empresa.id)
    else:
        form = TrabajadorEditForm(instance=usuario)
    return render(request, 'formularios/edit/editar_trabajador.html', {'form': form, 'empresa_id': empresa_id})


#redirige a la pagina para editar supervisores
@login_required
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    empresa_id = usuario.empresa.id
    usuario.delete()
    return redirect('detalles_empresa', empresa_id=empresa_id)

#eliminas empresas
@login_required
def eliminar_empresa(request, empresa_id):
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    if request.method == 'POST':
        empresa.delete()
        messages.success(request, 'La empresa y todo su contenido han sido eliminados.')
        return redirect('lista_empresas')
    return render(request, 'eliminar/eliminar_empresa.html', {'empresa': empresa})

#lista los permisos
@login_required
def lista_permisos(request):
    permisos = RegistroPermisos.objects.all()
    return render(request, 'listas/listas_permisos.html', {'permisos': permisos})

#edita empresas
@login_required
def editar_empresa(request, empresa_id):
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    if request.method == 'POST':
        form = EmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, 'La empresa ha sido actualizada.')
            return redirect('detalles_empresa', empresa_id=empresa.id)
    else:
        form = EmpresaForm(instance=empresa)
    return render(request, 'formularios/edit/editar_empresa.html', {'form': form, 'empresa': empresa})