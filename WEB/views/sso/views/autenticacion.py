from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from WEB.models.asistencia.asistencia import RegistroEntrada
from WEB.models import *
from WEB.forms.asistencia.forms import RegistroEntradaForm, RegistroSalidaForm
from django.utils import timezone

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('redirect_after_login')  # Redirige a la página principal después de iniciar sesión
        else:
            messages.error(request, 'Credenciales incorrectas. Por favor, inténtelo de nuevo.')
    return render(request, 'login/login.html')

@login_required
def redirect_after_login(request):
    if not hasattr(request.user, 'role'):
        return redirect('login')
    
    role = request.user.role
    if role == 'admin':
        return redirect('admin_home')
    elif role == 'supervisor':
        return redirect('supervisor_home', empresa_id=request.user.empresa_id)
    elif role == 'trabajador':
        return redirect('trabajador_home')
    return redirect('login')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def admin_home(request):
    return render(request, 'home/admin_home.html')

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

def configuracion_home(request):
    return render(request, 'side_menu/sofware/home/configuracion_home.html')