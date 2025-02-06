"""
Módulo de vistas para el sistema de gestión empresarial.

Incluye funcionalidades para:
- Gestión de ubicaciones geográficas (regiones, provincias, comunas)
- Autenticación y redirección de usuarios
- Vistas principales para diferentes roles
- Registro de entradas/salidas de trabajadores
- CRUD completo para empresas, usuarios y permisos
- Gestión de planes y vigencias
- Generación de reportes (actualmente en desarrollo)
"""

from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.conf import settings
from .decorators import permiso_requerido
from django.contrib.auth.decorators import login_required
from .forms import LimiteEmpresaForm, RegistroSalidaForm, RegistroEntradaForm, EmpresaForm, PermisoForm, AdminForm, SupervisorForm, TrabajadorForm, SupervisorEditForm, TrabajadorEditForm, PlanVigenciaForm,PlanForm
from .models import RegistroEmpresas, Usuario, RegistroPermisos, RegistroEntrada, Plan, Region, Provincia, Comuna, VigenciaPlan
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.views.generic import ListView
from django.utils import timezone
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db import IntegrityError
# =====================
# Vistas de Utilidades
# =====================

def get_comunas(request):
    """
    Obtiene las comunas de una provincia específica en formato JSON.
    
    :param request: HttpRequest con parámetro GET 'provincia_id'
    :return: JsonResponse con lista de comunas o mensaje de error
    :rtype: JsonResponse
    """
    provincia_id = request.GET.get('provincia_id')
    if provincia_id:
        comunas = Comuna.objects.filter(provincia_id=provincia_id).values('id', 'nombre')
        return JsonResponse(list(comunas), safe=False)
    return JsonResponse({'error': 'No provincia_id provided'}, status=400)

def get_provincias(request):
    """
    Obtiene las provincias de una región específica en formato JSON.
    
    :param request: HttpRequest con parámetro GET 'region_id'
    :return: JsonResponse con lista de provincias o mensaje de error
    :rtype: JsonResponse
    """
    region_id = request.GET.get('region_id')
    if region_id:
        provincias = Provincia.objects.filter(region_id=region_id).values('id', 'nombre')
        return JsonResponse(list(provincias), safe=False)
    return JsonResponse({'error': 'No region_id provided'}, status=400)

def get_regiones(request):
    """
    Obtiene todas las regiones disponibles en formato JSON.
    
    :param request: HttpRequest
    :return: JsonResponse con lista de regiones
    :rtype: JsonResponse
    """
    regiones = Region.objects.all().values('id', 'nombre')
    return JsonResponse(list(regiones), safe=False)

# =====================
# Vistas de Autenticación
# =====================

@login_required
def redirect_after_login(request):
    """
    Redirige al usuario a la vista correspondiente según su rol después del login.
    
    :param request: HttpRequest con usuario autenticado
    :return: HttpResponseRedirect a la vista correspondiente
    :raises Redirect: Si el usuario no tiene rol definido o es inválido
    """
    if not hasattr(request.user, 'role'):
        return redirect('login')
    
    role = request.user.role
    if role == 'admin':
        return redirect('admin_home')
    elif role == 'supervisor':
        return redirect('supervisor_home')
    elif role == 'trabajador':
        return redirect('trabajador_home')
    return redirect('login')

def logout_view(request):
    """
    Cierra la sesión del usuario y redirige al login.
    
    :param request: HttpRequest
    :return: Redirección a la página de login
    """
    logout(request)
    return redirect('login')

# =====================
# Vistas Principales
# =====================

@login_required
def admin_home(request):
    """
    Vista principal del administrador con filtros avanzados.
    
    :param request: HttpRequest
    :return: Renderizado de template con datos agrupados por empresa
    
    Parámetros GET aceptados:
    - q: Término de búsqueda (nombre de trabajador o empresa)
    - fecha_inicio: Fecha inicial para filtrar entradas
    - fecha_fin: Fecha final para filtrar entradas
    - empresa_id: ID de empresa específica para filtrar
    """
    query = request.GET.get('q')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    empresa_id = request.GET.get('empresa_id')
    
    empresas = RegistroEmpresas.objects.all()
    entradas = RegistroEntrada.objects.all()
    
    if empresa_id:
        entradas = entradas.filter(trabajador__empresa_id=empresa_id)
    
    if query:
        entradas = entradas.filter(
            Q(trabajador__username__icontains=query) | 
            Q(trabajador__empresa__nombre__icontains(query))
        )
    
    if fecha_inicio and fecha_fin:
        entradas = entradas.filter(hora_entrada__range=[fecha_inicio, fecha_fin])
    
    entradas_por_empresa = {
        empresa.nombre: entradas.filter(trabajador__empresa=empresa)
        for empresa in empresas
    }
    
    return render(request, 'home/admin_home.html', {
        'entradas_por_empresa': entradas_por_empresa,
        'empresas': empresas,
        'selected_empresa_id': empresa_id,
    })

@login_required
def supervisor_home(request):
    """
    Vista principal del supervisor con filtros para su empresa asignada.
    
    :param request: HttpRequest de usuario con rol supervisor
    :return: Renderizado de template con registros filtrados
    """
    if request.user.role == 'supervisor':
        empresa_id = request.user.empresa.id if request.user.empresa else None
        if empresa_id:
            return redirect('detalles_empresa', empresa_id=empresa_id)
        return redirect('lista_empresas')

    query = request.GET.get('q')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    entradas = RegistroEntrada.objects.filter(trabajador__empresa=request.user.empresa)
    
    if query:
        entradas = entradas.filter(Q(trabajador__username__icontains=query))
    
    if fecha_inicio and fecha_fin:
        entradas = entradas.filter(hora_entrada__range=[fecha_inicio, fecha_fin])
    
    return render(request, 'home/supervisor_home.html', {'entradas': entradas})

@login_required
def trabajador_home(request):
    """
    Vista principal del trabajador para registro de entradas/salidas.
    
    :param request: HttpRequest de usuario con rol trabajador
    :return: Renderizado de template con formularios correspondientes
    
    Maneja dos tipos de POST:
    - 'entrada': Registra hora de entrada con validación de 6 horas
    - 'salida': Registra hora de salida si existe entrada sin cerrar
    """
    if request.method == 'POST':
        if 'entrada' in request.POST:
            hace_seis_horas = timezone.now() - timezone.timedelta(hours=6)
            ultima_entrada = RegistroEntrada.objects.filter(
                trabajador=request.user,
                hora_entrada__gte=hace_seis_horas,
                permitir_otra_entrada=False
            ).exists()
            
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
            entrada_sin_salida = RegistroEntrada.objects.filter(
                trabajador=request.user,
                hora_salida__isnull=True
            ).last()
            
            if entrada_sin_salida:
                entrada_sin_salida.hora_salida = timezone.now()
                entrada_sin_salida.save()
                messages.success(request, 'Salida registrada exitosamente.')
                return redirect('trabajador_home')
            
            messages.warning(request, 'No hay una entrada sin salida registrada.')
            return redirect('trabajador_home')
    
    return render(request, 'home/trabajador_home.html', {
        'form_entrada': RegistroEntradaForm(),
        'form_salida': RegistroSalidaForm()
    })

# =====================
# Gestión de Registros
# =====================

@login_required
def habilitar_otra_entrada(request, entrada_id):
    """
    Permite a un supervisor o admin habilitar otra entrada antes de 6 horas.
    
    :param request: HttpRequest
    :param entrada_id: ID del registro de entrada
    :return: Redirección a supervisor_home con mensaje de estado
    """
    entrada = get_object_or_404(RegistroEntrada, id=entrada_id)
    if request.user.role == 'admin' or (request.user.role == 'supervisor' and entrada.trabajador.empresa == request.user.empresa):
        entrada.permitir_otra_entrada = True
        entrada.save()
        messages.success(request, 'Se ha habilitado el registro de otra entrada antes de las 6 horas.')
    else:
        messages.error(request, 'No tienes permiso para realizar esta acción.')
    return redirect('supervisor_home')

# =====================
# CRUD de Empresas
# =====================

@login_required
@permiso_requerido("crear_empresa")
def crear_empresa(request):
    """
    Vista para creación de nuevas empresas.
    
    :param request: HttpRequest
    :return: Renderizado de formulario o redirección tras éxito
    """
    if request.method == 'POST':
        form = EmpresaForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect('listar_empresas')
            except IntegrityError:
                # Maneja errores de unicidad no capturados por el formulario
                form.add_error('codigo_cliente', 'Este código ya existe')
    else:
        form = EmpresaForm()
    
    return render(request, 'formularios/crear/crear_empresa.html', {'form': form})
            

@login_required
def listar_empresas(request):
    """
    Lista todas las empresas registradas con capacidad de búsqueda.
    
    :param request: HttpRequest
    :return: Renderizado de template con lista de empresas
    """
    query = request.GET.get('q')
    empresas = RegistroEmpresas.objects.all()
    
    if query:
        empresas = empresas.filter(nombre__icontains=query)
    
    return render(request, 'empresas/listar_empresas.html', {'empresas': empresas})

def detalle_empresa(request, pk):
    """
    Muestra el detalle completo de una empresa específica.
    
    :param request: HttpRequest
    :param pk: ID de la empresa
    :return: Renderizado de template con detalles de la empresa
    """
    empresa = get_object_or_404(RegistroEmpresas, pk=pk)
    return render(request, 'empresas/detalles_empresa.html', {'empresa': empresa})

def editar_empresa(request, pk):
    """
    Vista para edición de información de una empresa existente.
    
    :param request: HttpRequest
    :param pk: ID de la empresa a editar
    :return: Renderizado de formulario o redirección tras éxito
    """
    empresa = get_object_or_404(RegistroEmpresas, pk=pk)
    if request.method == 'POST':
        form = EmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            return redirect('lista_empresas')
    else:
        form = EmpresaForm(instance=empresa)
    return render(request, 'empresas/empresa_form.html', {'form': form})

def eliminar_empresa(request, pk):
    """
    Vista para eliminación de una empresa existente.
    
    :param request: HttpRequest
    :param pk: ID de la empresa a eliminar
    :return: Confirmación de eliminación o redirección
    """
    empresa = get_object_or_404(RegistroEmpresas, pk=pk)
    if request.method == 'POST':
        empresa.delete()
        return redirect('listar_empresas')
    return render(request, 'empresas/eliminar_empresa.html', {'empresa': empresa})

# =====================
# CRUD de Usuarios
# =====================

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
    return render(request, 'formularios/crear/crear_permiso.html', {'form': form})

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
            return redirect('lista_empresas')
    else:
        form = AdminForm()
    return render(request, 'formularios/crear/crear_admin.html', {'form': form})

@login_required
@permiso_requerido("crear_supervisor")
def crear_supervisor(request):
    """
    Vista para creación de nuevos usuarios supervisores.
    
    :param request: HttpRequest
    :return: Renderizado de formulario o redirección tras éxito
    """
    if request.method == 'POST':
        form = SupervisorForm(request.POST, user=request.user)
        if form.is_valid():
            supervisor = form.save(commit=False)
            supervisor.role = 'supervisor'
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
                return redirect('lista_empresas')
            else:
                return redirect('detalles_empresa', empresa_id=trabajador.empresa.id)
    else:
        form = TrabajadorForm(user=request.user)
    return render(request, 'formularios/crear/crear_trabajador.html', {'form': form})

@login_required
def editar_supervisor(request, pk):
    """
    Vista para edición de usuarios supervisores.
    
    :param request: HttpRequest
    :param pk: ID del supervisor a editar
    :return: Renderizado de formulario o redirección tras éxito
    """
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

@login_required
@permiso_requerido("editar_trabajador")
def editar_trabajador(request, pk):
    """
    Vista para edición de usuarios trabajadores.
    
    :param request: HttpRequest
    :param pk: ID del trabajador a editar
    :return: Renderizado de formulario o redirección tras éxito
    """
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

@login_required
@permiso_requerido("eliminar_usuario")
def eliminar_usuario(request, user_id):
    """
    Vista para eliminación de usuarios.
    
    :param request: HttpRequest
    :param user_id: ID del usuario a eliminar
    :return: Redirección a lista correspondiente
    """
    usuario = get_object_or_404(Usuario, id=user_id)
    empresa_id = usuario.empresa.id if usuario.empresa else None
    usuario.delete()
    if empresa_id:
        return redirect('detalles_empresa', empresa_id=empresa_id)
    else:
        return redirect('listar_empresas')

# =====================
# Gestión de Planes
# =====================

class MantenimientoPlanes(ListView):
    """
    Vista basada en clase para el mantenimiento de planes.
    
    Atributos:
        model (Plan): Modelo utilizado
        template_name (str): Ruta del template
        context_object_name (str): Nombre del objeto en el contexto
    """
    model = Plan
    template_name = 'mantenimiento_planes.html'
    context_object_name = 'planes'

def vigencia_planes(request):
    """
    Gestiona la vigencia de los planes con cálculo automático de montos.
    
    :param request: HttpRequest
    :return: Renderizado de formulario de vigencia de planes
    """
    plan_id = request.GET.get('plan_id')
    plan = None
    if plan_id:
        plan = Plan.objects.get(id=plan_id)
    
    if request.method == 'POST':
        form = PlanVigenciaForm(request.POST)
        if form.is_valid():
            vigencia_plan = form.save(commit=False)
            if plan:
                vigencia_plan.plan = plan
            try:
                vigencia_plan.calcular_monto()
                vigencia_plan.save()
                return redirect('empresas_vigentes')
            except ValueError as e:
                form.add_error(None, str(e))
    else:
        form = PlanVigenciaForm(initial={'plan': plan})
    
    return render(request, 'empresas/vigencia_planes.html', {'form': form, 'plan': plan})

# =====================
# Reportes y Exportación
# =====================

def empresas_vigentes(request):
    """
    Muestra listado de empresas con planes vigentes.
    
    :param request: HttpRequest
    :return: Renderizado de template con empresas vigentes
    """
    empresas_vigentes = RegistroEmpresas.objects.prefetch_related('vigencias').all()
    context = {
        'empresas_vigentes': empresas_vigentes,
    }
    return render(request, 'empresas/empresas_vigente.html', context)

def generar_boleta(request, empresa_id):
    """
    Genera una boleta en PDF para una empresa (actualmente deshabilitado).
    
    :param request: HttpRequest
    :param empresa_id: ID de la empresa
    :return: HttpResponse con PDF generado (en desarrollo)
    """
    empresa = RegistroEmpresas.objects.get(id=empresa_id)
    vigencias = empresa.vigencias.all()
    context = {
        'empresa': empresa,
        'vigencias': vigencias,
    }
    # Implementación futura de generación de PDF
    return HttpResponse("Generación de PDF actualmente deshabilitada")

@login_required
def lista_permisos(request):
    """
    Lista todos los permisos registrados.
    
    :param request: HttpRequest
    :return: Renderizado de template con lista de permisos
    """
    permisos = RegistroPermisos.objects.all()
    return render(request, 'listas/listas_permisos.html', {'permisos': permisos})

@login_required
def actualizar_limites(request, empresa_id):
    """
    Actualiza los límites de supervisores y trabajadores de una empresa.
    
    :param request: HttpRequest
    :param empresa_id: ID de la empresa
    :return: Renderizado de template con formulario de actualización de límites
    """
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    if request.method == 'POST':
        form = LimiteEmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Límites actualizados exitosamente.')
            return redirect('listar_empresas')
    else:
        form = LimiteEmpresaForm(instance=empresa)
    return render(request, 'empresas/actualizar_limites.html', {'form': form, 'empresa': empresa})

@login_required
def listar_planes(request):
    """
    Lista todos los planes registrados.
    
    :param request: HttpRequest
    :return: Renderizado de template con lista de planes
    """
    planes = Plan.objects.all()
    return render(request, 'empresas/listar_planes.html', {'planes': planes})

@login_required
def crear_plan(request):
    """
    Vista para crear un nuevo plan.
    
    :param request: HttpRequest
    :return: Renderizado de template con formulario de creación de plan
    """
    if request.method == 'POST':
        form = PlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Plan creado exitosamente.')
            return redirect('listar_planes')
    else:
        form = PlanForm()
    return render(request, 'formularios/crear/crear_plan.html', {'form': form})
login_required
def configuracion_home(request):
    """
    Vista para la página de configuración del home.
    
    :param request: HttpRequest
    :return: Renderizado del template de configuración del home
    """
    return render(request, 'home/configuracion_home.html')
