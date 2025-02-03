def permisos_usuario(request):
    if request.user.is_authenticated:
        # Asegúrate de que 'request.user.permisos.all()' te da el objeto que necesitas
        permisos = request.user.permisos.all()
        return {"user_permisos": permisos}
    return {"user_permisos": []}
