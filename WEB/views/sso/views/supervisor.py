
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




from django.views.generic import  UpdateView
from django.views import View
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from WEB.models import RegistroEmpresas, Usuario, VigenciaPlan, RegistroEmpresas
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
    def post(self, request, vigencia_plan_id=None, user_id=None):
        vigencia_plan = get_object_or_404(VigenciaPlan, pk=vigencia_plan_id)
        form = UsuarioForm(request.POST, instance=Usuario(pk=user_id) if user_id else UsuarioForm(request.POST))
        
        if form.is_valid():
            user = form.save(commit=False)
            user.empresa = vigencia_plan.empresa
            user.vigencia_plan = vigencia_plan
            
            if not user_id and 'password' in request.POST:
                user.set_password(request.POST['password'])
            
            user.save()
            return JsonResponse({'message': 'Usuario guardado exitosamente'}, status=200)
        
        return JsonResponse({'errors': form.errors.get_json_data()}, status=400)

class ValidationView(View):
    def get(self, request):
        field = request.GET.get('field')
        value = request.GET.get('value')
        
        if field == 'rut':
            exists = Usuario.objects.filter(rut=value).exists()
            return JsonResponse({'exists': exists})
            
        if field == 'email':
            exists = Usuario.objects.filter(email=value).exists()
            return JsonResponse({'exists': exists})
            
        return JsonResponse({'error': 'Campo inválido'}, status=400)



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