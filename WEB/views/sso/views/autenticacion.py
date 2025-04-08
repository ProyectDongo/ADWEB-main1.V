from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
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

@login_required
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


