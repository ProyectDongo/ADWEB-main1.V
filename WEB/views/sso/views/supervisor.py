from django.views.generic import UpdateView
from django.views import View
from django.urls import reverse
from django.http import JsonResponse
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
                'username': user.username  # Asegúrate de enviar el username
            }
            return JsonResponse(data)
        return JsonResponse({'error': 'ID de usuario no proporcionado'}, status=400)
    

    def post(self, request, vigencia_plan_id, user_id=None):
        vigencia_plan = get_object_or_404(VigenciaPlan, pk=vigencia_plan_id)
        user = get_object_or_404(Usuario, pk=user_id) if user_id else None
        
        try:
            form = UsuarioForm(request.POST, instance=user)
            if form.is_valid():
                user = form.save(commit=False)
                user.empresa = vigencia_plan.empresa
                user.vigencia_plan = vigencia_plan

                if not user_id:  # Solo generar username para nuevos
                    user.username = user.rut.replace('-', '')
                
                if form.cleaned_data['password']:
                    user.set_password(form.cleaned_data['password'])
                
                user.save()
                return JsonResponse({'message': 'Usuario guardado exitosamente'}, status=200)
            else:
                return JsonResponse({'errors': form.errors}, status=400)
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
    

class SupervisorHomeView(LoginRequiredMixin, View):
    def get(self, request,vigencia_plan_id):
        if request.user.role != 'supervisor':
            return render(request, 'error/error.html')
        
        # Obtener vigencia_plan del usuario actual
        vigencia_plan = request.user.vigencia_plan
        vigencia_plan = get_object_or_404(VigenciaPlan, pk=vigencia_plan_id)
        # Filtrar usuarios por la misma vigencia_plan
        supervisores = Usuario.objects.filter(
            vigencia_plan=vigencia_plan,
            role='supervisor'
        ).select_related('vigencia_plan')
        
        trabajadores = Usuario.objects.filter(
            vigencia_plan=vigencia_plan,
            role='trabajador'
        ).select_related('vigencia_plan')
        
        return render(request, 'home/supervisores/supervisor_home.html', {
            'empresa': vigencia_plan.empresa,
            'supervisores': supervisores,
            'trabajadores': trabajadores,
            'vigencia_plan': vigencia_plan
        })