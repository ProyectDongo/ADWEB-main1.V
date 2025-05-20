from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from WEB.models import RegistroEmpresas, VigenciaPlan,Usuario
from WEB.forms import UsuarioForm
from django.views.generic import ListView, CreateView, UpdateView, DeleteView,View
from django.views import View
from django.urls import reverse,reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from WEB.models import RegistroEmpresas, Usuario, VigenciaPlan, Horario, Turno ,RegistroEntrada,DiaHabilitado
from WEB.forms import UsuarioForm, HorarioForm, TurnoForm ,RegistroEntradaForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta, date
from calendar import monthrange
import logging
from django import template




logger = logging.getLogger(__name__)
@login_required
def supervisor_home_asistencia(request, empresa_id, vigencia_plan_id):
    logger.info(f"Usuario autenticado: {request.user.is_authenticated}")
    # Verificar si el usuario está autenticado explícitamente
    if not request.user.is_authenticated:
        return render(request, 'error/error.html', {'message': 'Debes iniciar sesión para acceder a esta página'})

    # Validar permisos
    if request.user.role != 'supervisor':
        return render(request, 'error/error.html', {'message': 'Acceso no autorizado'})
    
    # Obtener objetos necesarios
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    vigencia_plan = get_object_or_404(VigenciaPlan, id=vigencia_plan_id, empresa=empresa)
    
    # Filtrar usuarios
    usuarios = Usuario.objects.filter(
        vigencia_plan=vigencia_plan
    ).select_related('vigencia_plan').order_by('role', 'last_name')
    
    # Separar por roles
    supervisores = usuarios.filter(role='supervisor')
    trabajadores = usuarios.filter(role='trabajador')
    
    context = {
        'empresa': empresa,
        'vigencia_plan': vigencia_plan,
        'supervisores': supervisores,
        'trabajadores': trabajadores,
        'form': UsuarioForm()
    }
    return render(request, 'home/supervisores/supervisor_home_asistencia.html', context)







class ValidationView(View):
    def get(self, request):
        rut = request.GET.get('rut')
        email = request.GET.get('email')
        
        if rut:
            exists = Usuario.objects.filter(rut=rut).exists()
            return JsonResponse({'exists': exists})
            
        if email:
            exists = Usuario.objects.filter(email=email).exists()
            return JsonResponse({'exists': exists})
            
        return JsonResponse({'error': 'Campo inválido'}, status=400)
    



class GetFormTemplateView(View):
    def get(self, request, action):
        form = UsuarioForm()
        if action == 'create':
            return render(request, 'formularios/supervisor/supervisor.asistencia.html', {'form': form})
        elif action == 'edit':
            form.fields['password'].required = False  # Hacer opcional el campo password
            return render(request, 'formularios/supervisor/supervisor.edit.html', {'form': form})
        return HttpResponse(status=404)
    







# AQUI EN ADELANTE ESTA TODO LO NUEVO LA IMPLEMETNACION DE GESTION DE HORAIOS Y TURNOS Y BLOQUEOS ACCESO 





# Manejo de Horarios

class HorarioListView(LoginRequiredMixin, ListView):
    model = Horario
    template_name = 'home/supervisores/horario/horarios_list.html'
    context_object_name = 'horarios'

    def get_queryset(self):
        # Filtra los horarios por la empresa del usuario autenticado
        return Horario.objects.filter(empresa=self.request.user.empresa)

    def get_context_data(self, **kwargs):
        # Obtiene el contexto base
        context = super().get_context_data(**kwargs)
        # Agrega empresa_id y vigencia_plan_id al contexto
        context['empresa_id'] = self.request.user.empresa.id if self.request.user.empresa else None
        context['vigencia_plan_id'] = self.request.user.vigencia_plan.id if self.request.user.vigencia_plan else None
        return context




class HorarioCreateView(LoginRequiredMixin, CreateView):
    model = Horario
    form_class = HorarioForm
    template_name = 'home/supervisores/horario/horario_form.html'
    success_url = reverse_lazy('horarios_list')

    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        return super().form_valid(form)
    
class HorarioUpdateView(LoginRequiredMixin, UpdateView):
    model = Horario
    form_class = HorarioForm
    template_name = 'home/supervisores/horario/horario_form.html'
    success_url = reverse_lazy('horarios_list')

class HorarioDeleteView(LoginRequiredMixin, DeleteView):
    model = Horario
    template_name = 'home/supervisores/horario/horario_confirm_delete.html'
    success_url = reverse_lazy('horarios_list')







# Manejo de Turnos

class TurnoListView(LoginRequiredMixin, ListView):
    model = Turno
    template_name = 'home/supervisores/turno/turnos_list.html'
    context_object_name = 'turnos'

    def get_queryset(self):
        return Turno.objects.filter(empresa=self.request.user.empresa)
    
    # ESTO MANEJA EL VOLVER AL HOME
    def get_queryset(self):
        # Filtra los horarios por la empresa del usuario autenticado
        return Turno.objects.filter(empresa=self.request.user.empresa)

    def get_context_data(self, **kwargs):
        # Obtiene el contexto base
        context = super().get_context_data(**kwargs)
        # Agrega empresa_id y vigencia_plan_id al contexto
        context['empresa_id'] = self.request.user.empresa.id if self.request.user.empresa else None
        context['vigencia_plan_id'] = self.request.user.vigencia_plan.id if self.request.user.vigencia_plan else None
        return context
    



class TurnoCreateView(LoginRequiredMixin, CreateView):
    model = Turno
    form_class = TurnoForm
    template_name = 'home/supervisores/turno/turno_form.html'
    success_url = reverse_lazy('turnos_list')

    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        return super().form_valid(form)

class TurnoUpdateView(LoginRequiredMixin, UpdateView):
    model = Turno
    form_class = TurnoForm
    template_name = 'home/supervisores/turno/turno_form.html'
    success_url = reverse_lazy('turnos_list')

class TurnoDeleteView(LoginRequiredMixin, DeleteView):
    model = Turno
    template_name = 'home/supervisores/turno/turno_confirm_delete.html'
    success_url = reverse_lazy('turnos_list')







    

# Updated UserCreateUpdateView
class UserCreateUpdateView(LoginRequiredMixin, View):
    def get(self, request, vigencia_plan_id, user_id=None):  
        if user_id:
            user = get_object_or_404(Usuario, pk=user_id)
            data = {
                'username': user.username,
                'rut': user.rut,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'celular': user.celular, 
                'role': user.role,
                'horario': user.horario_id,
                'turno': user.turno_id,
                'metodo_registro_permitido': user.metodo_registro_permitido
            }
            return JsonResponse(data)
        return JsonResponse({'error': 'ID de usuario no proporcionado'}, status=400)

    def delete(self, request, vigencia_plan_id, user_id):
        user = get_object_or_404(Usuario, pk=user_id)
        try:
            user.delete()
            return JsonResponse({'message': 'Usuario eliminado exitosamente'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def post(self, request, vigencia_plan_id, user_id=None):
        vigencia_plan = get_object_or_404(VigenciaPlan, pk=vigencia_plan_id)
        user = get_object_or_404(Usuario, pk=user_id) if user_id else None
        
        form = UsuarioForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.empresa = vigencia_plan.empresa
            user.vigencia_plan = vigencia_plan
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
            user.save()
            print(f"Usuario autenticado tras guardar: {request.user.is_authenticated}")  # Depuración
            return JsonResponse({
                'message': 'Usuario guardado exitosamente',
                'redirect_url': reverse('supervisor_home_asistencia', kwargs={
                    'empresa_id': vigencia_plan.empresa.id,
                    'vigencia_plan_id': vigencia_plan.id
                })
            }, status=200)
        else:
            errors = {f: [str(e) for e in e_list] for f, e_list in form.errors.items()}
            return JsonResponse({'errors': errors}, status=400)
        







class CalendarioTurnoView(LoginRequiredMixin, View):
    template_name = 'home/supervisores/turno/calendario_turno.html'

    def get(self, request, user_id):
        usuario = get_object_or_404(Usuario, pk=user_id)
        año = int(request.GET.get('año', date.today().year))
        
        # Generar todos los días del año
        inicio_año = date(año, 1, 1)
        fin_año = date(año, 12, 31)
        dias = []
        current = inicio_año
        while current <= fin_año:
            dia_habilitado = DiaHabilitado.objects.filter(usuario=usuario, fecha=current).first()
            estado = dia_habilitado.habilitado if dia_habilitado else usuario.debe_trabajar(current)
            dias.append({
                'fecha': current,
                'habilitado': estado,
                'mes': current.month,
                'dia_semana': current.weekday(),
            })
            current += timedelta(days=1)

        # Organizar los días por mes
        meses = {}
        for i in range(1, 13):
            meses[i] = [d for d in dias if d['mes'] == i]

        context = {
            'usuario': usuario,
            'año': año,
            'meses': meses,
            'empresa_id': usuario.vigencia_plan.empresa.id,
            'vigencia_plan_id': usuario.vigencia_plan.id,
        }
        return render(request, self.template_name, context)

    def post(self, request, user_id):
        usuario = get_object_or_404(Usuario, pk=user_id)
        año = int(request.POST.get('año', date.today().year))
        
        # Procesar los datos enviados
        inicio_año = date(año, 1, 1)
        fin_año = date(año, 12, 31)
        current = inicio_año
        while current <= fin_año:
            fecha_str = current.strftime('%Y-%m-%d')
            habilitado = request.POST.get(f'dia_{fecha_str}') == 'on'
            DiaHabilitado.objects.update_or_create(
                usuario=usuario,
                fecha=current,
                defaults={'habilitado': habilitado}
            )
            current += timedelta(days=1)

        # Redirigir a supervisor_home_asistencia con empresa_id y vigencia_plan_id
        return redirect('supervisor_home_asistencia', 
                        empresa_id=usuario.vigencia_plan.empresa.id, 
                        vigencia_plan_id=usuario.vigencia_plan.id)
    

class ActualizarDiaView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        # Obtener el usuario o devolver 404 si no existe
        usuario = get_object_or_404(Usuario, pk=user_id)
        
        # Obtener datos del cuerpo de la solicitud
        fecha = request.POST.get('fecha')
        habilitado = request.POST.get('habilitado') == 'true'
        
        # Validar que se proporcione la fecha
        if not fecha:
            return JsonResponse({'success': False, 'error': 'Fecha no proporcionada'}, status=400)
        
        # Actualizar o crear el registro en DiaHabilitado
        dia, created = DiaHabilitado.objects.update_or_create(
            usuario=usuario,
            fecha=fecha,
            defaults={'habilitado': habilitado}
        )
        
        # Devolver respuesta JSON exitosa
        return JsonResponse({'success': True})