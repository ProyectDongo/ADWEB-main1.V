from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def permiso_requerido(nombre_permiso):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Verifica si el usuario tiene el permiso
            if request.user.is_authenticated and request.user.permisos.filter(nombre=nombre_permiso).exists():
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "No tienes permiso para acceder a esta página.")
                return redirect('pagina_por_defecto')  # Redirige a una página segura
        return _wrapped_view
    return decorator
