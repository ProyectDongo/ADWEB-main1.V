from django.contrib import admin

from WEB.models import Usuario,RegistroEmpresas,VigenciaPlan,Plan, Pago, Cobro, HistorialCambios, HistorialPagos, EmailNotification, HistorialNotificaciones, Region, Provincia, Comuna, RegistroEntrada

# Register your models here.
admin.site.register(Usuario)
admin.site.register(RegistroEmpresas)
admin.site.register(VigenciaPlan)
admin.site.register(Plan)
admin.site.register(Pago)
admin.site.register(Cobro)
admin.site.register(HistorialCambios)
admin.site.register(HistorialPagos)
admin.site.register(EmailNotification)
admin.site.register(HistorialNotificaciones)
admin.site.register(Region)
admin.site.register(Provincia)
admin.site.register(Comuna)
admin.site.register(RegistroEntrada)
# Register your models here.
