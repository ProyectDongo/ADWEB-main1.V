
from .asistencia.asistencia import RegistroEntrada
from .empresa.empresa import RegistroEmpresas, VigenciaPlan,Plan
from .pagos.pago import Pago
from .cobro.cobro import Cobro
from .historial.historial import HistorialCambios,HistorialPagos
from .usuarios.usuario import Usuario
from .notificaciones.notificacion import EmailNotification,HistorialNotificaciones
from .ubicacion.region import Region, Provincia, Comuna
from .secure.permisos import RegistroPermisos
