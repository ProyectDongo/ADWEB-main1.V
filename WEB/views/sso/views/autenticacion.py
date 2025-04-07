from django.views.generic import TemplateView, FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib import messages
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect
from django_recaptcha.fields import ReCaptchaField  
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import HttpResponseRedirect, Http404
#from django.contrib.gis.geos import Point
from WEB.models import  Usuario, RegistroEmpresas, RegistroEntrada, VigenciaPlan
from WEB.forms import *
from django.views import View
from django.views.generic import DetailView


class RoleBasedLoginMixin:
    role = None  # Debe ser definido en las clases hijas
    max_attempts = 5  # Intentos máximos antes de bloquear
    captcha_threshold = 3  # Intentos para mostrar CAPTCHA

    def form_valid(self, form):
        user = form.get_user()
        
        # Verificación de rol y estado de cuenta
        if not self.validate_role(user):
            messages.error(self.request, 'Acceso no autorizado para este tipo de usuario')
            return self.form_invalid(form)
            
        if not self.check_account_status(user):
            messages.error(self.request, 'Cuenta bloqueada. Contacte al administrador')
            return self.form_invalid(form)
            
        self.handle_successful_login(user)
        return super().form_valid(form)

    def form_invalid(self, form):
        if form is not None:  # Verificamos que form no sea None
            username = form.cleaned_data.get('username')
            user = self.get_user_safe(username)
            
            # Actualizar intentos fallidos
            self.update_failed_attempts(user)
            self.update_session_attempts()
            
            # Aplicar medidas de seguridad
            self.add_captcha_if_needed(form)
            self.check_and_lock_account(user)
        
        return super().form_invalid(form)

    # Métodos auxiliares
    def validate_role(self, user):
        return hasattr(user, 'role') and user.role == self.role

    def check_account_status(self, user):
        return not user.is_locked

    def handle_successful_login(self, user):
        user.failed_login_attempts = 0
        user.last_failed_login = None
        user.save()
        
        # Reiniciar contador de sesión
        if 'failed_attempts' in self.request.session:
            del self.request.session['failed_attempts']

    def get_user_safe(self, username):
        try:
            return Usuario.objects.get(username=username)
        except Usuario.DoesNotExist:
            return None

    def update_failed_attempts(self, user):
        if user:
            user.failed_login_attempts += 1
            user.last_failed_login = timezone.now()
            user.save()

    def update_session_attempts(self):
        attempts = self.request.session.get('failed_attempts', 0) + 1
        self.request.session['failed_attempts'] = attempts

    def add_captcha_if_needed(self, form):
        session_attempts = self.request.session.get('failed_attempts', 0)
        if session_attempts >= self.captcha_threshold:
            form.fields['captcha'] = ReCaptchaField()
            messages.warning(self.request, 'Verificación de seguridad requerida')

    def check_and_lock_account(self, user):
        if user and user.failed_login_attempts >= self.max_attempts:
            user.is_locked = True
            user.save()
            messages.error(self.request, 'Cuenta bloqueada por seguridad')

# Vistas de login específicas para cada rol
class AdminLoginView(RoleBasedLoginMixin, LoginView):
    role = 'admin'
    template_name = 'login/admin/admin_login.html'
    success_url = reverse_lazy('admin_home')

class SupervisorLoginView(RoleBasedLoginMixin, LoginView):
    role = 'supervisor'
    template_name = 'login/supervisor/supervisor_login.html'
    success_url = reverse_lazy('supervisor_home')

class TrabajadorLoginView(RoleBasedLoginMixin, LoginView):
    role = 'trabajador'
    template_name = 'login/user/user_login.html'
    success_url = reverse_lazy('trabajador_home')

# Vista para seleccionar el tipo de login
class LoginSelectorView(TemplateView):
    template_name = 'login/home/login_selector.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('redirect_after_login')
        return super().dispatch(request, *args, **kwargs)

# Funciones auxiliares para redirección y vistas de inicio
@login_required
def redirect_after_login(request):
    """
    Redirige al usuario según su rol después del login
    """
    if not hasattr(request.user, 'role'):
        return redirect('login_selector')
    
    role = request.user.role
    if role == 'admin':
        return redirect('admin_home')
    elif role == 'supervisor':
        return redirect('supervisor_home', empresa_id=request.user.empresa_id)
    elif role == 'trabajador':
        return redirect('trabajador_home')
    return redirect('login_selector')

@login_required
def admin_home(request):
    return render(request, 'home/admin/admin_home.html')

def configuracion_home(request):
    return render(request, 'admin/sofware/home/configuracion_home.html')

@login_required
def supervisor_home(request, empresa_id):
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    supervisores = empresa.usuarios.filter(role='supervisor')
    trabajadores = empresa.usuarios.filter(role='trabajador')
    context = {
        'empresa': empresa,
        'supervisores': supervisores,
        'trabajadores': trabajadores,
    }
    return render(request, 'home/supervisores/supervisor_home.html', context)

#------------ FIN ------------


#--------------------------------------------------------------
#inicio de trabajador home 
from django.db.models import Sum, F
from datetime import timedelta, datetime
import time

#maneja las entradas 
def handle_entrada(request):
    context = {
        'form_entrada': RegistroEntradaForm(),
        'ultima_entrada_activa': RegistroEntrada.objects.filter(
            trabajador=request.user,
            hora_salida__isnull=True
        ).order_by('-hora_entrada').first(),
        'ultima_entrada': RegistroEntrada.objects.filter(trabajador=request.user).last()
    }
    
    if request.user.empresa is None:
        messages.error(request, "No tienes una empresa asociada. Contacta al administrador.")
        return redirect('trabajador_home')
    
    # Validación de entrada activa existente
    if RegistroEntrada.objects.filter(trabajador=request.user, hora_salida__isnull=True).exists():
        messages.error(request, 'Debes registrar la salida de tu entrada anterior antes de una nueva entrada')
        return redirect('trabajador_home')
    
    hoy = timezone.now().date()
    entradas_hoy = RegistroEntrada.objects.filter(
        trabajador=request.user,
        hora_entrada__date=hoy
    ).count()
   
    if entradas_hoy >= 3:
        messages.error(request, 'Máximo 3 entradas diarias alcanzado')
        return redirect('trabajador_home')
    
    entrada = RegistroEntrada(trabajador=request.user, empresa=request.user.empresa)
    form = RegistroEntradaForm(request.POST, request.FILES, instance=entrada)
    
    if form.is_valid():
        entrada = form.save(commit=False)
        entrada.trabajador = request.user
        entrada.empresa = request.user.empresa
        
        if form.cleaned_data['metodo'] == 'geo':
            latitud = request.POST.get('latitud')
            longitud = request.POST.get('longitud')
            if latitud and longitud:
                entrada.latitud = latitud
                entrada.longitud = longitud
            else:
                messages.error(request, 'Geolocalización requerida')
                context['form_entrada'] = form
                return render(request, 'home/users/trabajador_home.html', context)
        
        entrada.save()
        messages.success(request, 'Entrada registrada correctamente')
        return redirect('trabajador_home')
    
    messages.error(request, 'Error en el formulario')
    context['form_entrada'] = form
    return render(request, 'home/users/trabajador_home.html', context)

#maneja las salidas    
def handle_salida(request):
    entrada_activa = RegistroEntrada.objects.filter(
        trabajador=request.user,
        hora_salida__isnull=True
    ).order_by('-hora_entrada').first()
    
    if not entrada_activa:
        messages.error(request, 'No hay entrada activa')
        return redirect('trabajador_home')
    
    try:
        entrada_activa.hora_salida = timezone.now()
        entrada_activa.save()
        messages.success(request, f'Salida registrada a las {entrada_activa.hora_salida.strftime("%H:%M")}')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    
    return HttpResponseRedirect(reverse('trabajador_home'))

@login_required
def trabajador_home(request):
    context = {
        'form_entrada': RegistroEntradaForm(),
        'ultima_entrada_activa': RegistroEntrada.objects.filter(
            trabajador=request.user,
            hora_salida__isnull=True
        ).order_by('-hora_entrada').first(),
        'ultima_entrada': RegistroEntrada.objects.filter(trabajador=request.user).last()
    }
    
    if request.method == 'POST':
        if 'entrada' in request.POST:
            return handle_entrada(request)
        if 'salida' in request.POST:
            return handle_salida(request)
    
    return render(request, 'home/users/trabajador_home.html', context)

# Funciones auxiliares
def puede_registrar_entrada(user):
    return not RegistroEntrada.objects.filter(
        trabajador=user,
        hora_salida__isnull=True
    ).exists()
def get_entrada_activa(user):
    return RegistroEntrada.objects.filter(
        trabajador=user,
        hora_salida__isnull=True
    ).order_by('-hora_entrada').first()
    
# registros 
@login_required
@login_required
def ver_registros(request):
    def formatear_duracion(td):
        if td is None:
            return "00:00:00"
        total_segundos = td.total_seconds()
        horas = int(total_segundos // 3600)
        minutos = int((total_segundos % 3600) // 60)
        segundos = int(total_segundos % 60)
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

    registros = RegistroEntrada.objects.filter(
        trabajador=request.user
    ).order_by('-hora_entrada')
    
    hoy = timezone.now().date()
    
    # Manejo de fecha seleccionada
    fecha_seleccionada = hoy
    if 'fecha' in request.GET:
        try:
            fecha_seleccionada = datetime.strptime(
                request.GET['fecha'], '%Y-%m-%d'
            ).date()
        except ValueError:
            pass

    # Registros filtrados
    registros_filtrados = registros.filter(
        hora_entrada__date=fecha_seleccionada
    )
    
    # Calcular duraciones para cada registro
    for registro in registros_filtrados:
        if registro.hora_salida:
            delta = registro.hora_salida - registro.hora_entrada
            registro.duracion = formatear_duracion(delta)
        else:
            registro.duracion = '-'

    # Funciones agregadas
    def calcular_totales(queryset):
        resultado = queryset.aggregate(
            total=Sum(F('hora_salida') - F('hora_entrada'))
        )['total']
        return formatear_duracion(resultado)

    # Totales
    total_diario = calcular_totales(registros.filter(
        hora_entrada__date=hoy,
        hora_salida__isnull=False
    ))
    
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    total_semanal = calcular_totales(registros.filter(
        hora_entrada__date__gte=inicio_semana,
        hora_salida__isnull=False
    ))
    
    inicio_mes = hoy.replace(day=1)
    total_mensual = calcular_totales(registros.filter(
        hora_entrada__date__gte=inicio_mes,
        hora_salida__isnull=False
    ))

    context = {
        'registros': registros_filtrados,
        'total_diario': total_diario,
        'total_semanal': total_semanal,
        'total_mensual': total_mensual,
        'fecha_seleccionada': fecha_seleccionada,
        'hoy': hoy,
    }
    return render(request, 'home/users/ver_registros.html', context)

#fin de trabajador home
#----------------------------------------------------------------------
# inicio de admin home
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView

#------------------------------

# Bloqueo de acceso para usuarios no autorizados
class AdminUserMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'admin'

# Vista para gestionar empresas
class EmpresaDetailView(DetailView):
    model = RegistroEmpresas
    template_name = 'home/admin/empresa_detalles.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vigencias = self.object.vigencias.all()
        planes_data = []
        for vigencia in vigencias:
            supervisores = vigencia.usuarios.filter(role='supervisor')
            trabajadores = vigencia.usuarios.filter(role='trabajador')
            planes_data.append({
                'vigencia': vigencia,
                'supervisores': supervisores,
                'trabajadores': trabajadores
            })
        context['planes_data'] = planes_data
        return context
# crear supervisor
def validate_rut(request):
    rut = request.GET.get('rut', None)
    data = {'exists': Usuario.objects.filter(rut=rut).exists()}
    return JsonResponse(data)

class UsuarioCreateVigenciaView(AdminUserMixin, CreateView):
    model = Usuario
    template_name = 'home/admin/asistencia/usuario_create.html'
    fields = ['username', 'rut', 'email', 'celular', 'password']

    def form_valid(self, form):
        empresa = get_object_or_404(RegistroEmpresas, pk=self.kwargs['empresa_pk'])
        vigencia = get_object_or_404(VigenciaPlan, pk=self.kwargs['vigencia_pk'], empresa=empresa)
        
        user = form.save(commit=False)
        user.role = 'trabajador'  # Rol fijo
        user.empresa = empresa
        user.vigencia_plan = vigencia
        user.set_password(form.cleaned_data['password'])
        user.save()
        
        messages.success(self.request, 'Trabajador creado exitosamente')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            empresa = get_object_or_404(RegistroEmpresas, pk=self.kwargs.get('empresa_pk'))
            context['empresa'] = empresa
            context['vigencia'] = get_object_or_404(VigenciaPlan, pk=self.kwargs.get('vigencia_pk'), empresa=empresa)
        except Http404:
            raise Http404("Recurso no encontrado")
        return context
    
    def get_success_url(self):
        return reverse('empresa_detail', kwargs={'pk': self.kwargs.get('empresa_pk')})

class SupervisorCreateView(AdminUserMixin, CreateView):
    model = Usuario
    template_name = 'home/admin/asistencia/supervisor_create.html'
    fields = ['username', 'rut', 'email', 'celular', 'password']

    def form_valid(self, form):
        empresa = get_object_or_404(RegistroEmpresas, pk=self.kwargs['empresa_pk'])
        vigencia = get_object_or_404(VigenciaPlan, pk=self.kwargs['vigencia_pk'], empresa=empresa)
        
        user = form.save(commit=False)
        user.role = 'supervisor'  # Rol fijo
        user.empresa = empresa
        user.vigencia_plan = vigencia
        user.set_password(form.cleaned_data['password'])
        user.save()
        
        messages.success(self.request, 'Supervisor creado exitosamente')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            empresa = get_object_or_404(RegistroEmpresas, pk=self.kwargs.get('empresa_pk'))
            context['empresa'] = empresa
            context['vigencia'] = get_object_or_404(VigenciaPlan, pk=self.kwargs.get('vigencia_pk'), empresa=empresa)
        except Http404:
            raise Http404("Recurso no encontrado")
        return context
    
    def get_success_url(self):
        return reverse('empresa_detail', kwargs={'pk': self.kwargs.get('empresa_pk')})
# Usuario editado

class UsuarioUpdateView(AdminUserMixin, UpdateView):
    model = Usuario
    template_name = 'home/admin/asistencia/usuario_edit.html'
    fields = ['username', 'rut', 'email', 'celular', 'role', 'is_locked']

    def get_success_url(self):
        return reverse('empresa_detail', kwargs={'pk': self.object.empresa.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa'] = self.object.empresa
        context['all_groups'] = Group.objects.all()
        context['all_permissions'] = Permission.objects.all()
        return context

    def form_valid(self, form):
        # Procesar grupos y permisos
        selected_groups = self.request.POST.getlist('groups', [])
        selected_permissions = self.request.POST.getlist('user_permissions', [])
        
        self.object = form.save()
        self.object.groups.set(selected_groups)
        self.object.user_permissions.set(selected_permissions)
        
        messages.success(self.request, 'Usuario actualizado correctamente')
        return super().form_valid(form)
# Usuario eliminado
class UsuarioDeleteView(AdminUserMixin, DeleteView):
    model = Usuario
    template_name = 'home/admin/asistencia/usuario_confirm_delete.html'
    success_url = reverse_lazy('gestion_usuarios')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Usuario eliminado correctamente')
        return super().delete(request, *args, **kwargs)


# Nueva vista para editar VigenciaPlan
class VigenciaPlanUpdateView(AdminUserMixin, UpdateView):
    model = VigenciaPlan
    template_name = 'home/admin/asistencia/vigencia_plan_edit.html'
    fields = ['descuento', 'max_usuarios_override', 'estado']

    def get_success_url(self):
        return reverse('empresa_detail', kwargs={'pk': self.object.empresa.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Vigencia del plan actualizada correctamente')
        return super().form_valid(form)

# Vigencia plan estado
class VigenciaPlanStatusToggleView(AdminUserMixin, View):
    def post(self, request, *args, **kwargs):
        vigencia = get_object_or_404(VigenciaPlan, pk=kwargs['pk'])
        nuevo_estado = request.POST.get('nuevo_estado')
        
        if nuevo_estado in dict(VigenciaPlan.TIPO_DURACION).keys():
            vigencia.estado = nuevo_estado
            vigencia.save()
            
            # Modificado: Bloquear solo usuarios del plan específico
            usuarios_plan = Usuario.objects.filter(vigencia_plan=vigencia)
            
            if nuevo_estado == 'suspendido':
                usuarios_plan.update(is_locked=True)
            elif nuevo_estado == 'indefinido':
                usuarios_plan.update(is_locked=False)
            
            messages.success(request, f'Estado del plan actualizado a {vigencia.get_estado_display()}')
        
        return redirect('empresa_detail', pk=vigencia.empresa.pk)

# Cuenta Bloqueada View
class CuentaBloqueadaView(TemplateView):
    template_name = 'error/cuenta_bloqueada.html'
# fin de admin home
#----------------------------------------------------------------------
# inicio de supervisor home

from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse
from django.http import JsonResponse

# vista para crear usuario
class CrearUsuarioMixin:
    form_class = UsuarioForm
    template_name = 'admin/crear_usuario.html'
    role = None
    success_message = "Usuario creado exitosamente"

    def form_valid(self, form):
        form.instance.role = self.role
        form.instance.empresa_id = self.kwargs['empresa_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('supervisor_home', kwargs={'empresa_id': self.kwargs['empresa_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa'] = get_object_or_404(RegistroEmpresas, pk=self.kwargs['empresa_id'])
        return context

# Vista para editar empresa
class EditarEmpresaView(UpdateView):
    model = RegistroEmpresas
    fields = ['nombre', 'rut', 'direccion', 'telefono']
    template_name = 'empresa/editar_empresa.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Empresa actualizada exitosamente")
        return response

    def get_success_url(self):
        return reverse('supervisor_home', kwargs={'empresa_id': self.object.id})

# Vista para crear usuario
def crear_usuario(request, empresa_id):
    empresa = get_object_or_404(RegistroEmpresas, pk=empresa_id)
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.role = request.POST.get('tipo_usuario')
            usuario.empresa = empresa
            usuario.save()
            return JsonResponse({'success': True})
        else:
            errors = {field: errors[0] for field, errors in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors})
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

#  vista para editar Usuarios
def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            errors = {field: errors[0] for field, errors in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors})
    else:
        data = {
            'rut': usuario.rut,
            'username': usuario.username,
            'first_name': usuario.first_name,
            'last_name': usuario.last_name,
            'email': usuario.email,
        }
        return JsonResponse(data)
# Vista para eliminar usuario
def eliminar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    empresa_id = usuario.empresa.id
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado correctamente!')
    return redirect('supervisor_home', empresa_id=empresa_id)

class SupervisorHomeView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.role != 'supervisor':
            return render(request, 'error/error.html')  
        
        empresa = request.user.empresa
        supervisores = Usuario.objects.filter(empresa=empresa, role='supervisor')
        trabajadores = Usuario.objects.filter(empresa=empresa, role='trabajador')
        
        return render(request, 'home/supervisores/supervisor_home.html', {
            'empresa': empresa,
            'supervisores': supervisores,
            'trabajadores': trabajadores
        })
#fin de supervisor home
#----------------------------------------------------------------------