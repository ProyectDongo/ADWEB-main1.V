from django.shortcuts import render,redirect
from django.contrib.auth import logout
from .decorators import permiso_requerido
from django.contrib.auth.decorators import login_required
from .forms import LimiteEmpresaForm,RegistroSalidaForm,RegistroEntradaForm,EmpresaForm, PermisoForm, AdminForm, SupervisorForm, TrabajadorForm, SupervisorEditForm, TrabajadorEditForm
from .models import RegistroEmpresas,Usuario,RegistroPermisos,RegistroEntrada
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone




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
    query = request.GET.get('q')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    empresa_id = request.GET.get('empresa_id')
    
    empresas = RegistroEmpresas.objects.all()
    entradas = RegistroEntrada.objects.all()
    
    if empresa_id:
        entradas = entradas.filter(trabajador__empresa_id=empresa_id)
    
    if query:
        entradas = entradas.filter(Q(trabajador__username__icontains=query) | Q(trabajador__empresa__nombre__icontains(query)))
    
    if fecha_inicio and fecha_fin:
        entradas = entradas.filter(hora_entrada__range=[fecha_inicio, fecha_fin])
    
    # Agrupar entradas por empresa
    entradas_por_empresa = {empresa.nombre: entradas.filter(trabajador__empresa=empresa) for empresa in empresas}
    
    return render(request, 'home/admin_home.html', {
        'entradas_por_empresa': entradas_por_empresa,
        'empresas': empresas,
        'selected_empresa_id': empresa_id,
    })

#redirige a la pagina de inicio del supervisor
@login_required
def supervisor_home(request):
    if request.user.role == 'supervisor':
        empresa_id = request.user.empresa.id if request.user.empresa else None
        if empresa_id:
            return redirect('detalles_empresa', empresa_id=empresa_id)
        else:
            return redirect('lista_empresas')

    query = request.GET.get('q')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    # Filtrar registros por la empresa del supervisor
    entradas = RegistroEntrada.objects.filter(trabajador__empresa=request.user.empresa)
    
    if query:
        entradas = entradas.filter(Q(trabajador__username__icontains=query))
    
    if fecha_inicio and fecha_fin:
        entradas = entradas.filter(hora_entrada__range=[fecha_inicio, fecha_fin])
    
    return render(request, 'home/supervisor_home.html', {'entradas': entradas})

# redirige a la pagina de inicio del trabajador
@login_required
def trabajador_home(request):
    if request.method == 'POST':
        if 'entrada' in request.POST:
            hace_seis_horas = timezone.now() - timezone.timedelta(hours=6)
            ultima_entrada = RegistroEntrada.objects.filter(trabajador=request.user, hora_entrada__gte=hace_seis_horas, permitir_otra_entrada=False).exists()
            
            if ultima_entrada:
                messages.warning(request, 'Usted ya ha registrado su entrada. Vuelva en 6 horas o comuníquese con su supervisor.')
                return redirect('trabajador_home')
            
            form_entrada = RegistroEntradaForm(request.POST)
            if form_entrada.is_valid():
                entrada = form_entrada.save(commit=False)
                entrada.trabajador = request.user
                entrada.save()
                messages.success(request, 'Entrada registrada exitosamente.')
                return redirect('trabajador_home')
        elif 'salida' in request.POST:
            entrada_sin_salida = RegistroEntrada.objects.filter(trabajador=request.user, hora_salida__isnull=True).last()
            
            if entrada_sin_salida:
                entrada_sin_salida.hora_salida = timezone.now()
                entrada_sin_salida.save()
                messages.success(request, 'Salida registrada exitosamente.')
                return redirect('trabajador_home')
            else:
                messages.warning(request, 'No hay una entrada sin salida registrada.')
                return redirect('trabajador_home')
    else:
        form_entrada = RegistroEntradaForm()
        form_salida = RegistroSalidaForm()
    return render(request, 'home/trabajador_home.html', {'form_entrada': form_entrada, 'form_salida': form_salida})

# habilita otra entrada antes de las 6 horas
@login_required
def habilitar_otra_entrada(request, entrada_id):
    entrada = get_object_or_404(RegistroEntrada, id=entrada_id)
    if request.user.role == 'admin' or (request.user.role == 'supervisor' and entrada.trabajador.empresa == request.user.empresa):
        entrada.permitir_otra_entrada = True
        entrada.save()
        messages.success(request, 'Se ha habilitado el registro de otra entrada antes de las 6 horas.')
    else:
        messages.error(request, 'No tienes permiso para realizar esta acción.')
    return redirect('supervisor_home')

#redirige al logout cierra sesion
def logout_view(request):
    logout(request)
    return redirect('login')

# redirige a la apgin para crear empresas
@login_required
@permiso_requerido("crear_empresa")
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
@permiso_requerido("crear_permiso")
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
@permiso_requerido("crear_admin")
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
@permiso_requerido("crear_supervisor")
def crear_supervisor(request):
    if request.method == 'POST':
        form = SupervisorForm(request.POST, user=request.user)
        if form.is_valid():
            supervisor = form.save(commit=False)
            supervisor.role = 'supervisor'  # Asegúrate de establecer el rol correctamente
            if request.user.role != 'admin':
                supervisor.empresa = request.user.empresa
            supervisor.set_password(form.cleaned_data['password1'])
            supervisor.save()
            form.save_m2m()
            return redirect('lista_empresas')
    else:
        form = SupervisorForm(user=request.user)
    return render(request, 'formularios/crear/crear_supervisor.html', {'form': form})

@login_required
@permiso_requerido("crear_trabajador")
def crear_trabajador(request):
    if request.method == 'POST':
        form = TrabajadorForm(request.POST, user=request.user)
        if form.is_valid():
            trabajador = form.save(commit=False)
            trabajador.role = 'trabajador'  # Asegúrate de establecer el rol correctamente
            if request.user.role != 'admin':
                trabajador.empresa = request.user.empresa
            trabajador.save()
            form.save_m2m()
            if request.user.role == 'admin':
                return redirect('lista_empresas')
            else:
                return redirect('detalles_empresa', empresa_id=trabajador.empresa.id)
    else:
        form = TrabajadorForm(user=request.user)
    return render(request, 'formularios/crear/crear_trabajador.html', {'form': form})


#redirige a la pagina de lista de usuarios  
@login_required
@permiso_requerido("lista_empresas")
def lista_empresas(request):
    query = request.GET.get('q')
    if query:
        empresas = RegistroEmpresas.objects.filter(
            Q(nombre__icontains=query) | Q(rut__icontains=query)
        )
    else:
        empresas = RegistroEmpresas.objects.all()
    
    permisos_usuario = request.user.permisos.all()
    puede_crear_empresa = permisos_usuario.filter(nombre="crear_empresa").exists()
    puede_ver_detalles_empresa = permisos_usuario.filter(nombre="detalles_empresa").exists()
    
    return render(request, 'listas/lista_empresas.html', {
        'empresas': empresas,
        'query': query,
        'puede_crear_empresa': puede_crear_empresa,
        'puede_ver_detalles_empresa': puede_ver_detalles_empresa
    })
#redirige a la pagina de detalles de la empresa


@login_required
@permiso_requerido("detalles_empresa")
def detalles_empresa(request, empresa_id=None):
    if request.user.role == 'admin' and empresa_id is None:
        # Si el usuario es admin y no se proporciona empresa_id, redirigir a lista_empresas
        return redirect('lista_empresas')
    
    # Si no es admin o se proporciona empresa_id, obtener la empresa específica
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    query = request.GET.get('q')
    if query:
        supervisores = empresa.usuarios.filter(role='supervisor', username__icontains=query)
        trabajadores = empresa.usuarios.filter(role='trabajador', username__icontains=query)
    else:
        supervisores = empresa.usuarios.filter(role='supervisor')
        trabajadores = empresa.usuarios.filter(role='trabajador')
    
    permisos_usuario = request.user.permisos.all()
    context = {
        'empresa': empresa,
        'supervisores': supervisores,
        'trabajadores': trabajadores,
        'query': query,
        'permisos_usuario': permisos_usuario,
    }
    return render(request, 'listas/detalles_empresa.html', context)

#redirige a la pagina para editar supervisores
@login_required
def editar_supervisor(request, pk):
    supervisor = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = SupervisorEditForm(request.POST, instance=supervisor, user=request.user)
        if form.is_valid():
            form.save()
            if request.user.role == 'admin':
                return redirect('lista_empresas')
            else:
                return redirect('detalles_empresa', empresa_id=supervisor.empresa.id)
    else:
        form = SupervisorEditForm(instance=supervisor, user=request.user)
    return render(request, 'formularios/edit/editar_supervisor.html', {'form': form, 'supervisor': supervisor})
#redirige a la pagina para editar trabajadores
@login_required
@permiso_requerido("editar_trabajador")
def editar_trabajador(request, pk):
    trabajador = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = TrabajadorEditForm(request.POST, instance=trabajador, user=request.user)
        if form.is_valid():
            form.save()
            if request.user.role == 'admin':
                return redirect('lista_empresas')
            else:
                return redirect('detalles_empresa', empresa_id=trabajador.empresa.id)
    else:
        form = TrabajadorEditForm(instance=trabajador, user=request.user)
    return render(request, 'formularios/edit/editar_trabajador.html', {'form': form, 'trabajador': trabajador})


#redirige a la pagina para editar supervisores
@login_required
@permiso_requerido("eliminar_usuario")
def eliminar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    empresa_id = usuario.empresa.id if usuario.empresa else None
    usuario.delete()
    if empresa_id:
        return redirect('detalles_empresa', empresa_id=empresa_id)
    else:
        return redirect('lista_empresas')

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

@login_required
def base_view(request):
    return render(request, 'base.html', {'role': request.user.role})


#redirige a la pagina para actualizar los limites de la empresa
@login_required
def actualizar_limites(request, empresa_id):
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    if request.method == 'POST':
        form = LimiteEmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Límites actualizados exitosamente.')
            return redirect('listar_empresas')
    else:
        form = LimiteEmpresaForm(instance=empresa)
    return render(request, 'formularios/limites/actualizar_limites.html', {'form': form, 'empresa': empresa})
# redirige a la pagina para listar las empresas
@login_required
def listar_empresas(request):
    query = request.GET.get('q')
    empresas = RegistroEmpresas.objects.all()
    
    if query:
        empresas = empresas.filter(nombre__icontains=query)
    
    return render(request, 'listas/listar_empresas.html', {'empresas': empresas})

# estas 2 anteriores rigen 1 funcion 