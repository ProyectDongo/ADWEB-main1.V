from django.contrib.auth.models import Permission


def permisos_usuario(request):
    if request.user.is_authenticated:
        # Obtener permisos directos + permisos de grupos (usando related_name correcto)
        permisos = request.user.user_permissions.all() | Permission.objects.filter(group__usuario_groups=request.user)
        return {"user_permisos": permisos}
    return {"user_permisos": []}

def user_role(request):
    if request.user.is_authenticated:
        return {'role': request.user.role}
    return {}