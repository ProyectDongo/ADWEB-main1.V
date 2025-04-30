# inicio de admin home
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, TemplateView, View
from django.shortcuts import get_object_or_404, redirect    
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from WEB.models import RegistroEmpresas, Usuario, VigenciaPlan
from django.utils.safestring import mark_safe
from biometrics.models import *






# Bloqueo de acceso para usuarios no autorizados
class AdminUserMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'admin'




# Vista para gestionar empresas
class EmpresaDetailView(DetailView):
    model = RegistroEmpresas
    template_name = 'modules/empresa_detalles.html'

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

#valida rut ajax
def validate_rut(request):
    rut = request.GET.get('rut', None)
    data = {'exists': Usuario.objects.filter(rut=rut).exists()}
    return JsonResponse(data)







# crear Usuario
class UsuarioCreateVigenciaView(AdminUserMixin, CreateView):
    model = Usuario
    template_name = 'modules/asistencia/usuario_create.html'
    fields = ['username', 'rut', 'email', 'celular', 'password']

    def form_valid(self, form):
        empresa = get_object_or_404(RegistroEmpresas, pk=self.kwargs['empresa_pk'])
        vigencia = get_object_or_404(VigenciaPlan, pk=self.kwargs['vigencia_pk'], empresa=empresa)
        
        user = form.save(commit=False)
        user.role = 'trabajador' 
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





#crear supervisor
class SupervisorCreateView(AdminUserMixin, CreateView):
    model = Usuario
    template_name = 'modules/asistencia/supervisor_create.html'
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
    template_name = 'modules/asistencia/usuario_edit.html'
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
    template_name = 'modules/asistencia/usuario_confirm_delete.html'
    success_url = reverse_lazy('gestion_usuarios')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Usuario eliminado correctamente')
        return super().delete(request, *args, **kwargs)







# Nueva vista para editar VigenciaPlan

class VigenciaPlanUpdateView(AdminUserMixin, UpdateView):
    model = VigenciaPlan
    template_name = 'modules/asistencia/vigencia_plan_edit.html'
    fields = ['codigo_plan', 'monto_plan', 'descuento', 'max_usuarios_override']
    
    def get_success_url(self):
        return reverse('vigencia_plan_edit', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            self.object.calcular_monto()
            messages.success(self.request, mark_safe(
                f'<i class="fas fa-check-circle me-2"></i>'
                f'Actualización exitosa:<br>'
                f'<strong>{self.object.codigo_plan}</strong> | '
                f'Monto final: ${self.object.monto_final:,.2f}'
            ))
            return response
        except Exception as e:
            messages.error(self.request, f'Error al actualizar: {str(e)}')
            return self.form_invalid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['codigo_plan'].widget.attrs.update({
            'class': 'form-control',
            'pattern': '[A-Za-z0-9_-]{5,50}',
            'title': 'Solo letras, números, guiones y underscores (5-50 caracteres)'
        })
        form.fields['monto_plan'].widget.attrs.update({
            'class': 'form-control',
            'min': '0',
            'step': '0.01'
        })
        form.fields['descuento'].widget.attrs.update({
            'class': 'form-control',
            'min': '0',
            'max': '100',
            'step': '0.1'
        })
        form.fields['max_usuarios_override'].widget.attrs.update({
            'class': 'form-control',
            'min': '1'
        })
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        return context






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






@login_required
def eliminar_huella(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id)
    if request.method == 'POST':
        if usuario.has_huella:
            huella = huellas.objects.get(user=usuario)
            huella.delete()
        return redirect('empresa_detail', pk=usuario.empresa.pk)  
    return redirect('empresa_detail', pk=usuario.empresa.pk)



# fin de admin home


