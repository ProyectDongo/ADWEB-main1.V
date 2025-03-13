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
from WEB.models import *
from WEB.forms import RegistroEntradaForm, RegistroSalidaForm




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
    return render(request, 'home/admin_home.html')

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
    return render(request, 'home/home_supervisor/supervisor_home.html', context)

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
    
    if form.is_valid():
        entrada = form.save(commit=False)
        entrada.trabajador = request.user
        
        # Validación de entrada única
        if not puede_registrar_entrada(request.user):
            messages.warning(request, 'Ya tiene una entrada activa')
            return redirect('trabajador_home')
        
        entrada.save()
        messages.success(request, 'Entrada registrada correctamente')
        return redirect('trabajador_home')
    
    context['form_entrada'] = form
    return render(request, 'home/trabajador_home.html', context)

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
