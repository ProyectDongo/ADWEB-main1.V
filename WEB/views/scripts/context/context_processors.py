def permisos_usuario(request):
    if request.user.is_authenticated:
        permisos = request.user.permisos.all()
        return {"user_permisos": permisos}
    return {"user_permisos": []}

def user_role(request):
    if request.user.is_authenticated:
        return {'role': request.user.role}
    return {}

def permisos_usuario(request):
    if request.user.is_authenticated:
        return {'user_permisos': request.user.permisos.all()}
    return {}