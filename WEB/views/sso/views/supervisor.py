from django.views.generic import UpdateView
from django.views import View
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from WEB.models import RegistroEmpresas, Usuario, VigenciaPlan
from WEB.forms import UsuarioForm
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

class UserCreateUpdateView(LoginRequiredMixin, View):
    def get(self, request, vigencia_plan_id, user_id=None):  # Añade parámetros
        if user_id:
            user = get_object_or_404(Usuario, pk=user_id)
            data = {
                'rut': user.rut,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'username': user.username ,
                'celular': user.celular, 
                'role': user.role 
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