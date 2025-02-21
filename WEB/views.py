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
from dateutil.relativedelta import relativedelta
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.conf import settings
from .decorators import permiso_requerido
from django.contrib.auth.decorators import login_required
from .forms import LimiteEmpresaForm, RegistroSalidaForm, RegistroEntradaForm, EmpresaForm, PermisoForm, AdminForm, SupervisorForm, TrabajadorForm, SupervisorEditForm, TrabajadorEditForm, PlanVigenciaForm,PlanForm
from .models import RegistroEmpresas, Usuario, RegistroPermisos, RegistroEntrada, Plan, Region, Provincia, Comuna, VigenciaPlan,HistorialCambios,Pago
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.views.generic import ListView
from django.utils import timezone
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.crypto import get_random_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


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
def supervisor_home(request,empresa_id):
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    supervisores = empresa.usuarios.filter(role='supervisor')
    trabajadores = empresa.usuarios.filter(role='trabajador')
    context = {
        'empresa': empresa,
        'supervisores': supervisores,
        'trabajadores': trabajadores,
    }
    return render(request, 'home/supervisor_home.html', context)


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
    Vista para crear una nueva empresa junto con la vigencia de su plan y crear un usuario supervisor.
    """
    if request.method == 'POST':
        empresa_form = EmpresaForm(request.POST)
        vigencia_form = PlanVigenciaForm(request.POST)
        
        # Eliminar el campo 'empresa' del formulario de vigencia
        vigencia_form.fields.pop('empresa', None)
        
        if empresa_form.is_valid() and vigencia_form.is_valid():
            # Guardamos la empresa
            empresa = empresa_form.save(commit=False)
            # Asignar el plan desde el formulario de vigencia
            empresa.plan_contratado = vigencia_form.cleaned_data['plan']
            empresa.save()
            
            # Guardamos la vigencia asignándole la empresa creada
            vigencia_plan = vigencia_form.save(commit=False)
            vigencia_plan.empresa = empresa
            vigencia_plan.save()
            
            # --- Crear el usuario supervisor ---
            # Generamos una contraseña aleatoria de 8 caracteres
            password = get_random_string(8)
            
            # Creamos el usuario supervisor
            # Puedes ajustar el username según tus necesidades (por ejemplo, usando el código_cliente)
            supervisor = Usuario.objects.create_user(
                username=empresa.codigo_cliente,  # Asegúrate que sea único
                email=empresa.email,
                password=password,
                role='supervisor',
                empresa=empresa,
                rut=empresa.rut,       # O asignar otro valor si es necesario
                nombre=empresa.nombre, # Por ejemplo, el nombre de la empresa
            )
            
            # Opcional: podrías enviar un correo electrónico con las credenciales
            # O bien, mostrar un mensaje de éxito con las credenciales generadas.
            
            # Por ejemplo, usando mensajes de Django:
            from django.contrib import messages
            messages.success(request, 
                f"Empresa creada correctamente. Se ha creado un usuario supervisor con username: {supervisor.username} y contraseña: {password}"
            )
            
            return redirect('listar_empresas')
    else:
        empresa_form = EmpresaForm()
        vigencia_form = PlanVigenciaForm()
        vigencia_form.fields.pop('empresa', None)  # También en GET para evitar error en template

    return render(request, 'formularios/crear/crear_empresa.html', {
        'empresa_form': empresa_form,
        'vigencia_form': vigencia_form
    })


@login_required

def detalle_empresa(request, pk):
    """
    Vista para mostrar y editar los detalles de una empresa específica.

    Esta vista permite a los usuarios autenticados ver y editar los detalles de una empresa específica.
    También permite eliminar la empresa si se solicita. Además, muestra un historial de cambios recientes
    y una lista de supervisores y trabajadores asociados a la empresa.

    :param request: HttpRequest
    :param pk: ID de la empresa a mostrar y editar
    :return: Renderizado del template 'empresas/detalles_empresa.html' con los detalles de la empresa
    """
    # Obtener el objeto RegistroEmpresas o devolver un 404 si no existe
    supervisores = Usuario.objects.filter(role='Supervisor', empresa_id=pk)
    empresa = get_object_or_404(RegistroEmpresas, pk=pk)
    vigencias = empresa.vigencias.all()
    
    # Obtener el historial de cambios recientes para la empresa
    historial = HistorialCambios.objects.filter(empresa=empresa).order_by('-fecha')[:10]
    
    # Filtrar usuarios por grupo y empresa
    supervisores = Usuario.objects.filter(role='Supervisor', empresa_id=pk)
    trabajadores = Usuario.objects.filter(role='Trabajador', empresa_id=pk)

    if request.method == 'POST':
        if 'guardar' in request.POST:
            # Si se solicita guardar, crear un formulario con los datos enviados y la instancia de la empresa
            form = EmpresaForm(request.POST, instance=empresa)
            if form.is_valid():
                # Si el formulario es válido, guardar los cambios
                form.save()
                # Registrar en historial
                HistorialCambios.objects.create(
                    empresa=empresa,
                    usuario=request.user,
                    descripcion="Modificación de datos empresariales"
                )
                # Mostrar un mensaje de éxito
                messages.success(request, 'Cambios guardados exitosamente!')
                # Redirigir a la vista de detalles de la empresa
                return redirect('detalle_empresa', pk=pk)
                
        elif 'eliminar' in request.POST:
            # Si se solicita eliminar, eliminar la empresa
            empresa.delete()
            # Mostrar un mensaje de éxito
            messages.success(request, 'Empresa eliminada correctamente')
            # Redirigir a la lista de empresas
            return redirect('listar_empresas')

    else:
        # Si la solicitud es GET, crear un formulario con la instancia de la empresa
        form = EmpresaForm(instance=empresa)

    # Renderizar el template con la empresa, el formulario, los supervisores, los trabajadores y el historial
    return render(request, 'empresas/detalles_empresa.html', {
        'empresa': empresa,
        'vigencias': vigencias,
        'form': form,
        'supervisores': supervisores,
        'trabajadores': trabajadores,
        'historial': historial
    })

@login_required
@permiso_requerido("vista_empresas")
def listar_empresas(request):
    """
    Lista todas las empresas registradas con capacidad de búsqueda.
    
    :param request: HttpRequest
    :return: Renderizado de template con lista de empresas
    """
    empresas = RegistroEmpresas.objects.filter(eliminada=False)
    
    query = request.GET.get('q')
    if query:
        empresas = empresas.filter(nombre__icontains=query)
    
    return render(request, 'empresas/listar_empresas.html', {'empresas': empresas})

@login_required
def eliminar_empresa(request, pk):
    empresa = get_object_or_404(RegistroEmpresas, id=pk)
    empresa.eliminada = True
    empresa.save()
    messages.success(request, 'Empresa marcada como eliminada')
    return redirect('listar_empresas')

def listar_empresas_eliminadas(request):
    empresas = RegistroEmpresas.objects.filter(eliminada=True)
    return render(request, 'empresas/listar_empresas_eliminadas.html', {'empresas': empresas})

def recuperar_empresa(request, id):
    empresa = get_object_or_404(RegistroEmpresas, id=id)
    empresa.eliminada = False
    empresa.save()
    messages.success(request, 'Empresa recuperada exitosamente')
    return redirect('listar_empresas_eliminadas')
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
            return redirect('home')
    else:
        form = AdminForm()
    return render(request, 'formularios/crear/crear_admin.html', {'form': form})

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
                return redirect('listar_empresas')
            else:
                return redirect('detalles_empresa', empresa_id=trabajador.empresa.id)
    else:
        form = TrabajadorForm(user=request.user)
    return render(request, 'formularios/crear/crear_trabajador.html', {'form': form})

@login_required
@permiso_requerido("editar_supervisor")
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
            return redirect('detalle_empresa', pk=supervisor.empresa.id)

    else:
        form = SupervisorEditForm(instance=supervisor, user=request.user)
    return render(request, 'formularios/edit/editar_supervisor.html', {'form': form, 'supervisor': supervisor})

@login_required
@permiso_requerido("editar_trabajador")
def editar_trabajador(request, pk):
    """
    Vista para la edición de un trabajador.
    """
    trabajador = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = TrabajadorEditForm(request.POST, instance=trabajador, user=request.user)
        if form.is_valid():
            form.save()
            # Redirige siempre a la página de detalles de la empresa
            return redirect('detalle_empresa', pk=trabajador.empresa.id)
    else:
        form = TrabajadorEditForm(instance=trabajador, user=request.user)
    return render(request, 'formularios/edit/editar_trabajador.html', {
        'form': form,
        'trabajador': trabajador
    })

@login_required
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

@login_required
def vigencia_planes(request, pk):
    empresa = get_object_or_404(RegistroEmpresas, id=pk)
    
    # Si existe un plan_id en la query string, lo obtenemos (opcional)
    plan_id = request.GET.get('plan_id')
    plan = None
    if plan_id:
        plan = get_object_or_404(Plan, id=plan_id)
    
    if request.method == 'POST':
        form = PlanVigenciaForm(request.POST)
        if form.is_valid():
            vigencia_plan = form.save(commit=False)
            # Asigna la empresa capturada de la URL
            vigencia_plan.empresa = empresa
            if plan:
                vigencia_plan.plan = plan
            try:
                vigencia_plan.calcular_monto()
                vigencia_plan.save()
                return redirect('empresas_vigentes')
            except ValueError as e:
                form.add_error(None, str(e))
    else:
        form = PlanVigenciaForm(initial={'empresa': empresa, 'plan': plan})
        # Opcional: si no deseas que se pueda modificar la empresa, deshabilita el campo
        form.fields['empresa'].disabled = True
    
    return render(request, 'empresas/vigencia_planes.html', {
        'form': form,
        'plan': plan,
        'empresa': empresa
    })


# =====================
# Reportes y Exportación
# =====================

@login_required
def empresas_vigentes(request):
    
    """
    Vista para listar las vigencias de los planes de las empresas con capacidad de búsqueda y filtrado.

    Esta vista obtiene todos los registros de VigenciaPlan y carga la empresa relacionada. Permite filtrar
    los resultados por empresa, código de plan y código de cliente.

    Parámetros GET aceptados:
    - empresa_id: ID de la empresa para filtrar las vigencias.
    - codigo_plan: Código del plan para filtrar las vigencias (búsqueda parcial, insensible a mayúsculas).
    - codigo_cliente: Código del cliente para filtrar las vigencias (búsqueda parcial, insensible a mayúsculas).

    :param request: HttpRequest
    :return: Renderizado del template 'empresas/empresas_vigente.html' con el contexto de las vigencias filtradas.
    """
    # Inicia con todos los registros de VigenciaPlan y carga la empresa relacionada.
    qs = VigenciaPlan.objects.select_related('empresa').all()

    # Obtén los parámetros de búsqueda desde la URL
    empresa_id = request.GET.get('empresa_id')
    codigo_plan = request.GET.get('codigo_plan')
    codigo_cliente = request.GET.get('codigo_cliente')

    # Filtrar por el valor de la clave foránea 'empresa_id'
    if empresa_id:
        qs = qs.filter(empresa_id=empresa_id)
    
    # Filtrar por código de plan (se permite búsqueda parcial, insensible a mayúsculas)
    if codigo_plan:
        qs = qs.filter(codigo_plan__icontains=codigo_plan)
    
    # Filtrar por código cliente, que está en el modelo relacionado (RegistroEmpresas)
    if codigo_cliente:
        qs = qs.filter(empresa__codigo_cliente__icontains = codigo_cliente)
     # Ordena el queryset por el código de cliente para que el regroup funcione correctamente
    qs = qs.order_by('empresa__codigo_cliente', 'codigo_plan')


    context = {
        'vigencias': qs,
        'search_params': {
            'empresa_id': empresa_id,
            'codigo_plan': codigo_plan,
            'codigo_cliente': codigo_cliente,
        }
    }
    
    return render(request, 'empresas/empresas_vigente.html', context)

@login_required
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
@permiso_requerido("lista_permisos")
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
#@permiso_requerido("vista_planes")
def listar_planes(request):
    """
    Lista todos los planes registrados.
    
    :param request: HttpRequest
    :return: Renderizado de template con lista de planes
    """
    planes = Plan.objects.all()
    return render(request, 'empresas/listar_planes.html', {'planes': planes})

@login_required
#@permiso_requerido("crear_plan")
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



@login_required
#@permiso_requerido("editar_vigencia")
def editar_vigencia_plan(request, plan_id):
    """
    Vista para editar la vigencia de un plan existente.

    Esta vista permite a los usuarios autenticados editar los detalles de la vigencia de un plan específico.
    Si la solicitud es un POST, se valida y guarda el formulario. Si es GET, se muestra el formulario con los
    datos actuales del plan.

    :param request: HttpRequest
    :param plan_id: ID de la vigencia del plan a editar
    :return: Renderizado del template 'empresas/editar_vigencia_plan.html' con el formulario de edición
    """
    # Obtener el objeto VigenciaPlan o devolver un 404 si no existe
    plan = get_object_or_404(VigenciaPlan, id=plan_id)
    
    if request.method == 'POST':
        # Si la solicitud es POST, crear un formulario con los datos enviados y la instancia del plan
        form = PlanVigenciaForm(request.POST, instance=plan)
        if form.is_valid():
            # Si el formulario es válido, guardar los cambios
            form.save()
            # Mostrar un mensaje de éxito
            messages.success(request, 'Plan actualizado exitosamente.')
            # Redirigir a la lista de empresas
            return redirect('empresas_vigentes')
    else:
        # Si la solicitud es GET, crear un formulario con la instancia del plan
        form = PlanVigenciaForm(instance=plan)
    
    # Renderizar el template con el formulario y el plan
    return render(request, 'empresas/editar_vigencia_plan.html', {'form': form, 'plan': plan})



@login_required
@permiso_requerido("eliminar_supervisor")
def eliminar_supervisor(request, supervisor_id):
    supervisor = get_object_or_404(Usuario, id=supervisor_id, role='Supervisor')
    empresa_id = supervisor.empresa_id
    supervisor.delete()
    messages.success(request, 'Supervisor eliminado exitosamente.')
    return redirect('detalle_empresa', pk=empresa_id)

@login_required
@permiso_requerido("eliminar_trabajador")
def eliminar_trabajador(request, trabajador_id):
    trabajador = get_object_or_404(Usuario, id=trabajador_id, role='Trabajador')
    empresa_id = trabajador.empresa_id
    trabajador.delete()
    messages.success(request, 'Trabajador eliminado exitosamente.')
    return redirect('detalle_empresa', pk=empresa_id)


@require_POST
def suspender_empresa(request, empresa_id):
    """
    Suspende la empresa: actualiza estado a 'suspendido' y vigente a False.
    """
    empresa = get_object_or_404(RegistroEmpresas, pk=empresa_id)
    empresa.estado = 'suspendido'
    empresa.vigente = False
    empresa.save()
    return JsonResponse({'success': True})

@require_POST
def habilitar_empresa(request, empresa_id):
    """
    Habilita la empresa: actualiza estado a 'aldia' y vigente a True.
    """
    empresa = get_object_or_404(RegistroEmpresas, pk=empresa_id)
    empresa.estado = 'aldia'
    empresa.vigente = True
    empresa.save()
    return JsonResponse({'success': True})

def toggle_estado(request, pk):
    vigencia = get_object_or_404(VigenciaPlan, pk=pk)
    
    # Toggle del estado
    if vigencia.estado == 'indefinido':
        vigencia.estado = 'suspendido'
    else:
        vigencia.estado = 'indefinido'
    
    vigencia.save()
    
    return JsonResponse({
        'success': True,
        'new_estado': vigencia.estado,
        'new_estado_display': vigencia.get_estado_display()
    })


# pagos 
def get_next_due(empresa):
    """Devuelve la fecha (primer día del mes) del próximo pago pendiente."""
    hoy = timezone.now()
    next_due = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    while Pago.objects.filter(
        empresa=empresa,
        fecha_pago__year=next_due.year,
        fecha_pago__month=next_due.month
    ).exists():
        next_due += relativedelta(months=1)
    return next_due

def gestion_pagos(request, empresa_id):
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    vigencia_planes_activos = empresa.vigencias.filter(estado='indefinido')
    vigencia_planes_suspendidos = empresa.vigencias.filter(estado='suspendido')
    total = sum(vp.monto_final for vp in vigencia_planes_activos)
    
    hoy = timezone.now()
    next_due = get_next_due(empresa)
    
    if request.method == 'POST':
        if (next_due.month != hoy.month or next_due.year != hoy.year) and not request.POST.get('confirmar'):
            selected_planes_ids = request.POST.getlist('planes')
            metodo = request.POST.get('metodo')
            context = {
                'empresa': empresa,
                'proximo_mes': next_due,
                'planes': selected_planes_ids,
                'metodo': metodo,
            }
            return render(request, 'empresas/confirmar_pago.html', context)
        
        selected_planes_ids = request.POST.getlist('planes')
        selected_planes = vigencia_planes_activos.filter(id__in=selected_planes_ids)
        metodo = request.POST.get('metodo')
        
        pago = Pago.objects.create(
            empresa=empresa,
            monto=sum(vp.monto_final for vp in selected_planes),
            metodo=metodo,
            pagado=(metodo == 'manual' or metodo == 'otro_metodo'),  # Ajusta según lógica
            fecha_pago=next_due
        )
        
        if metodo == 'manual':
            # Se envía el correo personalizado con las instrucciones de pago manual
            send_manual_payment_email(empresa, next_due)
        
        pago.vigencia_planes.set(selected_planes)
        empresa.estado = 'aldia'
        empresa.save()
        return redirect('detalle_empresa', pk=empresa.id)
    
    return render(request, 'empresas/gestion_pagos.html', {
        'empresa': empresa,
        'vigencia_planes_activos': vigencia_planes_activos,
        'vigencia_planes_suspendidos': vigencia_planes_suspendidos,
        'total': total,
    })
    
def toggle_plan(request, vigencia_id):
    vigencia = get_object_or_404(VigenciaPlan, id=vigencia_id)
    vigencia.estado = 'suspendido' if vigencia.estado == 'indefinido' else 'indefinido'
    vigencia.save()
    return redirect('gestion_pagos', empresa_id=vigencia.empresa.id)

def historial_pagos(request, empresa_id):
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    return render(request, 'empresas/historial_pagos.html', {
        'empresa': empresa,
        'pagos': empresa.pagos.all()
    })

def confirmar_pago_extra(request, empresa_id):
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    if request.method == 'POST':
        if 'confirmar' in request.POST:
            pago_data = request.session.get('pago_data', {})
            # Procesar pago extra...
            return redirect('gestion_pagos', empresa_id=empresa_id)
        return redirect('gestion_pagos', empresa_id=empresa_id)
    return render(request, 'empresas/confirmar_pago_extra.html', {'empresa': empresa})


#envio de correo 

def send_manual_payment_email(empresa, next_due):
    """
    Envía un correo con instrucciones de pago manual personalizado.
    """
    # Datos ficticios de transferencia
    transfer_data = {
        'banco': 'Banco Ficticio',
        'tipo_cuenta': 'Cuenta Corriente',
        'numero_cuenta': '9876543210',
        'titular': empresa.nombre,
    }
    # URL del logo de la empresa (puede ser una URL absoluta a un recurso en tus estáticos)
    logo_url = 'static/png/Logo.png'
    
    subject = "Instrucciones de Pago Manual"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [empresa.email]
    
    context = {
        'empresa': empresa,
        'transfer_data': transfer_data,
        'logo_url': logo_url,
        'proximo_mes': next_due,
    }
    # Renderizamos el contenido HTML del correo usando una plantilla
    html_content = render_to_string('empresas/email/instrucciones_pago_manual.html', context)
    # Extraemos el contenido en texto plano (por si el cliente de correo no soporta HTML)
    text_content = strip_tags(html_content)
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def planes_por_empresa(request, empresa_id):
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    vigencias = VigenciaPlanes.objects.filter(empresa=empresa)
    return render(request, 'planes_por_empresa.html', {'vigencias': vigencias})