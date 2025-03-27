from django.views.generic import TemplateView, FormView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib import messages
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect
from django_recaptcha.fields import ReCaptchaField  
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.utils import timezone
#from django.contrib.gis.geos import Point
from WEB.models import *
from WEB.forms import *
from django.views import View


class RoleBasedLoginMixin:
    role = None  # Debe ser definido en las clases hijas
    max_attempts = 5  # Intentos máximos antes de bloquear
    captcha_threshold = 3  # Intentos para mostrar CAPTCHA

    def form_valid(self, form):
        user = form.get_user()
        
        # Verificación de rol y estado de cuenta
        if not self.validate_role(user):
            return self.handle_invalid_role()
            
        if not self.check_account_status(user):
            return self.handle_locked_account()
            
        self.handle_successful_login(user)
        return super().form_valid(form)

    def form_invalid(self, form):
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

    def handle_invalid_role(self):
        messages.error(self.request, 'Acceso no autorizado para este tipo de usuario')
        return self.form_invalid(None)

    def check_account_status(self, user):
        return not user.is_locked

    def handle_locked_account(self):
        messages.error(self.request, 'Cuenta bloqueada. Contacte al administrador')
        return self.form_invalid(None)

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
#----------------------------------------------------------------------
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

class LoginSelectorView(TemplateView):
    template_name = 'login/home/login_selector.html'
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('redirect_after_login')
        return super().dispatch(request, *args, **kwargs)
    
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

@login_required
def trabajador_home(request):
    context = {
        'form_entrada': RegistroEntradaForm(),
        'form_salida': RegistroSalidaForm()
    }

    if request.method == 'POST':
        if 'entrada' in request.POST:
            return handle_entrada(request, context)
        elif 'salida' in request.POST:
            return handle_salida(request, context)

    return render(request, 'home/trabajador_home.html', context)

def handle_entrada(request, context):
    form = RegistroEntradaForm(request.POST, request.FILES)
    
    #if form.is_valid():
        #entrada = form.save(commit=False)
       # entrada.trabajador = request.user
        
        # Registrar geolocalización
        #if form.cleaned_data['metodo'] == 'geo':
           # entrada.ubicacion = Point(
               # float(request.POST.get('longitud')),
                #float(request.POST.get('latitud'))
           # )
           # entrada.precision = float(request.POST.get('precision', 0))
            
            #if not entrada.esta_dentro_rango(request.user.empresa):
              #  raise forms.ValidationError("Está fuera del área permitida")
        
       # entrada.save()
       # messages.success(request, 'Entrada registrada correctamente')
       # return redirect('trabajador_home')

def handle_salida(request, context):
    form = RegistroSalidaForm(request.POST)
    entrada_activa = get_entrada_activa(request.user)
    
    if not entrada_activa:
        messages.warning(request, 'No hay entrada activa')
        return redirect('trabajador_home')
    
    if form.is_valid():
        entrada_activa.hora_salida = timezone.now()
        entrada_activa.save()
        messages.success(request, 'Salida registrada correctamente')
        return redirect('trabajador_home')
    
    context['form_salida'] = form
    return render(request, 'home/trabajador_home.html', context)

# Funciones auxiliares
def puede_registrar_entrada(user):
    return not RegistroEntrada.objects.filter(
        trabajador=user,
        hora_salida__isnull=True
    ).exists()

def get_entrada_activa(user):
    try:
        return RegistroEntrada.objects.get(
            trabajador=user,
            hora_salida__isnull=True
        )
    except RegistroEntrada.DoesNotExist:
        return None
#----------------------------------------------------------------------
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin

class AdminUserMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'admin'
    
class AdminAsistenciaView(LoginRequiredMixin, TemplateView):
    template_name = 'home/admin/asistencia/modulo_asistencia.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresas'] = RegistroEmpresas.objects.filter(
            plan_contratado__nombre__icontains='asistencia'
        )
        return context

class GestionUsuariosView(AdminUserMixin, ListView):
    model = Usuario
    template_name = 'admin/gestion_usuarios.html'
    context_object_name = 'usuarios'
    
    def get_queryset(self):
        return Usuario.objects.all()

class EditarLimitePlanView(AdminUserMixin, UpdateView):
    model = Plan
    fields = ['max_usuarios']
    template_name = 'admin/editar_limite_plan.html'
    success_url = reverse_lazy('gestion_planes')

class EliminarUsuarioView(AdminUserMixin, DeleteView):
    model = Usuario
    template_name = 'admin/confirmar_eliminacion.html'
    success_url = reverse_lazy('gestion_usuarios')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipo_usuario'] = self.object.get_role_display()
        return context
#----------------------------------------------------------------------

from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse
from django.http import JsonResponse

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
            return render(request, 'access_denied.html')  # O redirigir a otra página
        
        empresa = request.user.empresa
        supervisores = Usuario.objects.filter(empresa=empresa, role='supervisor')
        trabajadores = Usuario.objects.filter(empresa=empresa, role='trabajador')
        
        return render(request, 'supervisor_home.html', {
            'empresa': empresa,
            'supervisores': supervisores,
            'trabajadores': trabajadores
        })