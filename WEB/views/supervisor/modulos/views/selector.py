# En views.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
from WEB.forms import RegistroEntradaForm  
from WEB.models import RegistroEntrada
from WEB.views.trabajador.views.trabajadores import calcular_horas_extra, calcular_retraso




# Maneja las entradas
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
        return redirect('supervisor_register')
    
    # Verificación modificada con puede_trabajar
    if not request.user.puede_trabajar(timezone.now().date()):
        messages.error(request, "No tienes permiso para trabajar hoy.")
        return redirect('supervisor_register')
    
    if RegistroEntrada.objects.filter(trabajador=request.user, hora_salida__isnull=True).exists():
        messages.error(request, 'Debes registrar la salida de tu entrada anterior antes de una nueva entrada')
        return redirect('supervisor_register')
    
    hoy = timezone.now().date()
    entradas_hoy = RegistroEntrada.objects.filter(
        trabajador=request.user,
        hora_entrada__date=hoy
    ).count()
   
    if entradas_hoy >= 3:
        messages.error(request, 'Máximo 3 entradas diarias alcanzado')
        return redirect('supervisor_register')
    
    entrada = RegistroEntrada(trabajador=request.user, empresa=request.user.empresa)
    form = RegistroEntradaForm(request.POST, request.FILES, instance=entrada)
    
    if form.is_valid():
        metodo_seleccionado = form.cleaned_data['metodo']
        if metodo_seleccionado != request.user.metodo_registro_permitido:
            messages.error(request, 'No tienes habilitado este método de registro.')
            context['form_entrada'] = form
            return render(request, 'home/supervisores/supervisor_register.html', context)
        
        entrada = form.save(commit=False)
        entrada.trabajador = request.user
        entrada.empresa = request.user.empresa
        
        if form.cleaned_data['metodo'] == 'geo':
            latitud = request.POST.get('latitud')
            longitud = request.POST.get('longitud')
            if latitud and longitud:
                try:
                    latitud = float(latitud)
                    longitud = float(longitud)
                    if not (-90 <= latitud <= 90) or not (-180 <= longitud <= 180):
                        raise ValueError("Coordenadas fuera de rango")
                    entrada.latitud = latitud
                    entrada.longitud = longitud
                except ValueError:
                    messages.error(request, 'Coordenadas inválidas')
                    context['form_entrada'] = form
                    return render(request, 'home/supervisores/supervisor_register.html', context)
            else:
                messages.error(request, 'Geolocalización requerida')
                context['form_entrada'] = form
                return render(request, 'home/supervisores/supervisor_register.html', context)
        
        entrada.save()
        if request.user.horario:
            calcular_retraso(entrada, request.user.horario)
            entrada.save()
        messages.success(request, 'Entrada registrada correctamente')
        return redirect('supervisor_register')
    else:
        print("Errores del formulario:", form.errors)
        messages.error(request, f'Error en el formulario: {form.errors.as_text()}')
        context['form_entrada'] = form
        return render(request, 'home/supervisores/supervisor_register.html', context)










# Manejo de salidas
def handle_salida(request):
    entrada_activa = RegistroEntrada.objects.filter(
        trabajador=request.user,
        hora_salida__isnull=True
    ).order_by('-hora_entrada').first()
    
    if not entrada_activa:
        messages.error(request, 'No hay entrada activa')
        return redirect('supervisor_register')
    
    try:
        entrada_activa.hora_salida = timezone.now()
        if request.user.horario:
            calcular_horas_extra(entrada_activa, request.user.horario)
        entrada_activa.save()
        messages.success(request, f'Salida registrada a las {entrada_activa.hora_salida.strftime("%H:%M")}')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    
    return HttpResponseRedirect(reverse('supervisor_register'))

class SupervisorSelectorView(LoginRequiredMixin, TemplateView):
    template_name = 'login/supervisor/supervisor_selector_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empresa'] = self.request.user.empresa
        return context
    




@login_required
def supervisor_register(request):
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
            return handle_entrada(request)  # Reutilizamos la función existente
        if 'salida' in request.POST:
            return handle_salida(request)   # Reutilizamos la función existente
    
    return render(request, 'home/supervisores/supervisor_register.html', context)