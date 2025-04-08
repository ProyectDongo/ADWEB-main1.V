
from django.views.generic import  UpdateView
from django.views import View
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from WEB.models import RegistroEmpresas, Usuario
from WEB.forms import UsuarioForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required   



# vista para crear usuario
@login_required
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