from django.shortcuts import redirect
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from functools import wraps

def permiso_requerido(permiso):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.has_perm(permiso):
                return view_func(request, *args, **kwargs)
            else:
                return render(request, 'error\error.html', status=403)
        return _wrapped_view
    return decorator