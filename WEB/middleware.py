from django.shortcuts import redirect
from django.urls import reverse

class EmpresaStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.empresa is not None:
            if request.user.empresa.estado != 'aldia' and request.path != reverse('cuenta_bloqueada'):
                return redirect('cuenta_bloqueada')
        response = self.get_response(request)
        return response