def permisos_usuario(request):
    if request.user.is_authenticated:
        permisos = request.user.permisos.all()
        return {"user_permisos": permisos}
    return {"user_permisos": []}
