from django.views.generic import UpdateView
from django.views import View
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from WEB.models import RegistroEmpresas, Usuario, VigenciaPlan, Horario, Turno ,RegistroEntrada
from WEB.forms import UsuarioForm, HorarioForm, TurnoForm ,RegistroEntradaForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required



class UserManagementView(LoginRequiredMixin, View):
    def get(self, request, vigencia_plan_id):
        vigencia_plan = get_object_or_404(VigenciaPlan, pk=vigencia_plan_id)
        context = {
            'empresa': vigencia_plan.empresa,
            'vigencia_plan': vigencia_plan,
            'supervisores': Usuario.objects.filter(
                vigencia_plan=vigencia_plan,
                role='supervisor',
                empresa=vigencia_plan.empresa
            ),
            'trabajadores': Usuario.objects.filter(
                vigencia_plan=vigencia_plan,
                role='trabajador',
                empresa=vigencia_plan.empresa
            )
        }
        return render(request, 'admin/user_management.html', context)

    def post(self, request, vigencia_plan_id, user_id=None):
        vigencia_plan = get_object_or_404(VigenciaPlan, pk=vigencia_plan_id)
        user = get_object_or_404(Usuario, pk=user_id) if user_id else None
        
        try:
            form = UsuarioForm(request.POST, instance=user)
            if form.is_valid():
                user = form.save(commit=False)
                user.empresa = vigencia_plan.empresa
                user.vigencia_plan = vigencia_plan
                if form.cleaned_data['password']:
                    user.set_password(form.cleaned_data['password'])
                user.save()
                return JsonResponse({'message': 'Usuario guardado exitosamente'}, status=200)
            else:
                # Convertir errores de formulario a formato serializable
                errors = {f: [str(e) for e in e_list] for f, e_list in form.errors.items()}
                return JsonResponse({'errors': errors}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)




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
            return render(request, 'formularios/supervisor.asistencia.html', {'form': form})
        elif action == 'edit':
            form.fields['password'].required = False  # Hacer opcional el campo password
            return render(request, 'formularios/supervisor.edit.html', {'form': form})
        return HttpResponse(status=404)
    



# AQUI EN ADELANTE ESTA TODO LO NUEVO LA IMPLEMETNACION DE GESTION DE HORAIOS Y TURNOS Y BLOQUEOS ACCESO 

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404





# Manejo de Horarios

class HorarioListView(LoginRequiredMixin, ListView):
    model = Horario
    template_name = 'home/supervisores/horarios_list.html'
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
    template_name = 'home/supervisores/horario_form.html'
    success_url = reverse_lazy('horarios_list')

    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        return super().form_valid(form)
    

class HorarioUpdateView(LoginRequiredMixin, UpdateView):
    model = Horario
    form_class = HorarioForm
    template_name = 'home/supervisores/horario_form.html'
    success_url = reverse_lazy('horarios_list')

class HorarioDeleteView(LoginRequiredMixin, DeleteView):
    model = Horario
    template_name = 'home/supervisores/horario_confirm_delete.html'
    success_url = reverse_lazy('horarios_list')










# Manejo de Turnos

class TurnoListView(LoginRequiredMixin, ListView):
    model = Turno
    template_name = 'home/supervisores/turnos_list.html'
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
    template_name = 'home/supervisores/turno_form.html'
    success_url = reverse_lazy('turnos_list')

    def form_valid(self, form):
        form.instance.empresa = self.request.user.empresa
        return super().form_valid(form)

class TurnoUpdateView(LoginRequiredMixin, UpdateView):
    model = Turno
    form_class = TurnoForm
    template_name = 'home/supervisores/turno_form.html'
    success_url = reverse_lazy('turnos_list')

class TurnoDeleteView(LoginRequiredMixin, DeleteView):
    model = Turno
    template_name = 'home/supervisores/turno_confirm_delete.html'
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
                'horario': user.horario_id,  # ID del horario
                'turno': user.turno_id,      # ID del turno
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
        
        try:
            form = UsuarioForm(request.POST, instance=user)
            if form.is_valid():
                user = form.save(commit=False)
                user.empresa = vigencia_plan.empresa
                user.vigencia_plan = vigencia_plan
                # Solo establecer la contraseña si se proporciona una no vacía
                password = form.cleaned_data.get('password')
                if password:
                    user.set_password(password)
                user.save()
                return JsonResponse({'message': 'Usuario guardado exitosamente'}, status=200)
            else:
                errors = {f: [str(e) for e in e_list] for f, e_list in form.errors.items()}
                return JsonResponse({'errors': errors}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

