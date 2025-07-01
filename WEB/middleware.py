from django.shortcuts import redirect
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib import messages
from WEB.views.scripts.utils import hay_pagos_atrasados

class EmpresaStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.empresa is not None:
            if request.user.empresa.estado != 'aldia' and request.path != reverse('cuenta_bloqueada'):
                return redirect('cuenta_bloqueada')
        response = self.get_response(request)
        return response
    

class ValidationErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, ValidationError):
            messages.error(request, str(exception))
            return redirect(request.path)
        return None
    

class NotificacionPagosMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if request.user.is_authenticated and hasattr(request.user, 'vigencia_plan'):
            empresa = request.user.vigencia_plan.empresa
            vigencia_plan = request.user.vigencia_plan
            response.context_data['mostrar_mensaje'] = hay_pagos_atrasados(empresa, vigencia_plan)
        return response
    
