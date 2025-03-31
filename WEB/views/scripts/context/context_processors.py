from django.contrib.auth.models import Permission


def permisos_usuario(request):
    if request.user.is_authenticated:
        # Obtener permisos directos + permisos de grupos (usando related_name correcto)
       permisos = request.user.user_permissions.all() | Permission.objects.filter(group__usuarios=request.user)
       return {'permisos_usuario': permisos}
    return {'permisos_usuario': []}

def user_role(request):
    if request.user.is_authenticated:
        return {'role': request.user.role}
    return {}