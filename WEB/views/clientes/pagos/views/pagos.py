from django.shortcuts import render, redirect, get_object_or_404
from WEB.models import *
from WEB.views import *
from WEB.views.scripts import *
import datetime,email,logging,os,imaplib,base64
from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from email.mime.image import MIMEImage
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from email.header import decode_header
from django.forms import modelformset_factory
from django.db.models import  Sum
from django.views.decorators.http import require_POST
from django.conf import settings
import re

logger = logging.getLogger(__name__)

def registrar_cobro(request, empresa_id):
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    
    if request.method == 'POST':
        selector = request.POST.get('selector')
        fecha_inicio = request.POST.get('fechaInicio')
        fecha_fin = request.POST.get('fechaFin')
        
        vigencias_activas = empresa.vigencias.all()
        
        if selector == 'todos':
            valor_total = vigencias_activas.aggregate(total=Sum('monto_final'))['total'] or 0
            cobro = Cobro.objects.create(
                empresa=empresa,
                vigencia_plan=None,
                monto_total=valor_total,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            cobro.vigencias_planes.set(vigencias_activas)
            
        else:
            vigencia = get_object_or_404(vigencias_activas, id=selector)
            cobro = Cobro.objects.create(
                empresa=empresa,
                vigencia_plan=vigencia,
                monto_total=vigencia.monto_final,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            )
            cobro.vigencias_planes.add(vigencia)
        
        # Registrar en historial
        pago_historial = Pago.objects.create(
            empresa=empresa,
            cobro=cobro,
            monto=0,
            fecha_pago=timezone.now(),
            metodo='registro'
        )
        HistorialPagos.objects.create(
            pago=pago_historial,
            usuario=request.user,
            descripcion=f"Registro de cobro por ${cobro.monto_total:.2f} - Vigencia: {cobro.fecha_inicio} a {cobro.fecha_fin}"
        )
        
        messages.success(request, 'Cobro registrado exitosamente!')
        return redirect('gestion_pagos', empresa_id=empresa.id)
    
    else:
        vigencias = empresa.vigencias.all()
        cobros_pendientes = empresa.cobros.filter(estado='pendiente').prefetch_related('vigencia_plan')
        
        context = {
            'empresa': empresa,
            'vigencias': vigencias,
            'cobros': cobros_pendientes,
        }
        return render(request, 'side_menu/clientes/lista_clientes/pagos/gestion_pagos.html', context)

def actualizar_cobro(request, empresa_id, cobro_id):
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    cobro = get_object_or_404(Cobro, id=cobro_id, empresa=empresa)
    
    if request.method == 'POST':
        abono = request.POST.get('abono')
        descripcion = request.POST.get('descripcion')
        
        try:
            abono = float(abono)
            if abono <= 0:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, "El abono debe ser un número válido y mayor a 0.")
            return redirect('gestion_pagos', empresa_id=empresa.id)

        pago = Pago.objects.create(
            empresa=empresa,
            cobro=cobro,
            monto=abono,
            fecha_pago=timezone.now(),
            metodo='abono',
        )
        
        if cobro.vigencia_plan:
            pago.vigencia_planes.add(cobro.vigencia_plan)
        else:
            pago.vigencia_planes.set(cobro.vigencias_planes.all())
        
        HistorialPagos.objects.create(
            pago=pago,
            usuario=request.user,
            descripcion=f"Abono de ${abono:.2f} - {descripcion}"
        )

        if cobro.monto_restante() <= 0:
            cobro.estado = 'pagado'
            cobro.save()
            messages.success(request, '¡Cobro completado exitosamente!')
        else:
            messages.success(request, 'Abono registrado correctamente.')
        
        return redirect(f"{reverse('gestion_pagos', args=[empresa.id])}?open_cobro={cobro.id}")
    
    messages.error(request, "Método no permitido.")
    return redirect('gestion_pagos', empresa_id=empresa.id)

def gestion_pagos(request, empresa_id):
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    vigencias = empresa.vigencias.all()
    cobros_pendientes = empresa.cobros.filter(estado='pendiente')
    
    historial_notificaciones = HistorialNotificaciones.objects.filter(
        empresa=empresa
    ).order_by('-fecha_envio')[:10]
    
    historial = HistorialPagos.objects.filter(
        pago__empresa=empresa
    ).select_related('pago', 'usuario', 'pago__cobro').order_by('-fecha')
    
    context = {
        'empresa': empresa,
        'vigencias': vigencias,
        'cobros': cobros_pendientes,
        'historial': historial,
        'historial_notificaciones': historial_notificaciones,  # Añadir al contexto
    }
    return render(request, 'side_menu/clientes/lista_clientes/pagos/gestion_pagos.html', context)

def send_manual_payment_email(empresa, next_due):
    """Envía correo con instrucciones para pago manual."""
    try:
        transfer_data = {
            'banco': 'Banco Ficticio',
            'tipo_cuenta': 'Cuenta Corriente',
            'numero_cuenta': '9876543210',
            'titular': empresa.nombre,
        }

        subject = f"Instrucciones de Pago Manual | Cliente: {empresa.codigo_cliente} | EmpresaID: {empresa.id}"
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [empresa.email]
        logo_path = os.path.join(settings.BASE_DIR, "static/png/logo.png")
        
        context = {
            'empresa': empresa,
            'codigo_cliente': empresa.codigo_cliente,
            'transfer_data': transfer_data,
            'proximo_mes': next_due,
            'empresa_id': empresa.id,
        }
        html_content = render_to_string('email/instrucciones_pago.html', context)
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as img:
                logo = MIMEImage(img.read())
                logo.add_header("Content-ID", "<logo_cid>")
                logo.add_header("Content-Disposition", "inline")
                msg.attach(logo)
        else:
            logger.warning("Logo no encontrado en: %s", logo_path)
            
        msg.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error("Error enviando correo: %s", str(e), exc_info=True)
        return False

def get_comprobantes():
    """Obtiene comprobantes de pago extrayendo el código cliente y empresa_id."""
    comprobantes = []
    try:
        IMAP_SERVER = 'imap.gmail.com'
        EMAIL_ACCOUNT = 'anghello3569molina@gmail.com'
        PASSWORD = 'qzvebjzifrjwphgg'
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, timeout=10)
        try:
            mail.login(EMAIL_ACCOUNT, PASSWORD)
            mail.select('inbox')
            status, data = mail.search(None, '(SUBJECT "Instrucciones de Pago Manual")')
            if status != 'OK':
                raise Exception("Error en búsqueda de correos")
            for e_id in data[0].split():
                try:
                    status, msg_data = mail.fetch(e_id, '(RFC822)')
                    if status != 'OK':
                        continue
                    msg = email.message_from_bytes(msg_data[0][1])
                    comprobante = {
                        'subject': msg.get('Subject', 'Sin asunto'),
                        'from': msg.get('From', 'Remitente desconocido'),
                        'date': msg.get('Date', 'Fecha no disponible'),
                        'codigo_cliente': 'No encontrado',
                        'empresa_id': None,
                        'imagenes': []
                    }
                    subject = comprobante['subject']
                    subject_match = re.search(r'(?i)Cliente:\s*([A-Z0-9\-]+)', subject)
                    if subject_match:
                        comprobante['codigo_cliente'] = subject_match.group(1).strip()
                        logger.debug(f"Código detectado en asunto: {comprobante['codigo_cliente']}")
                    else:
                        body = ""
                        for part in msg.walk():
                            if part.get_content_type() in ['text/plain', 'text/html']:
                                try:
                                    body += " " + part.get_payload(decode=True).decode(errors='replace')
                                except Exception as e:
                                    logger.error(f"Error decodificando cuerpo: {e}")
                        full_text = f"{subject} {body}"
                        codigo_match = re.search(r'(?i)(?:Código|Codigo|Cód|Cod)[\s:\-]*Cliente?[\s:\-]*([A-Z0-9\-]+)', full_text)
                        if codigo_match:
                            comprobante['codigo_cliente'] = codigo_match.group(1).strip()
                            logger.debug(f"Código detectado en cuerpo: {comprobante['codigo_cliente']}")
                    empresa_id_match = re.search(r'(?i)EmpresaID:\s*([0-9]+)', subject)
                    if empresa_id_match:
                        comprobante['empresa_id'] = int(empresa_id_match.group(1))
                        logger.debug(f"Empresa ID detectado en asunto: {comprobante['empresa_id']}")
                    for part in msg.walk():
                        if part.get_content_maintype() == 'image':
                            try:
                                filename = part.get_filename() or ""
                                decoded_header = decode_header(filename)
                                filename = decoded_header[0][0]
                                if isinstance(filename, bytes):
                                    filename = filename.decode(decoded_header[0][1] or 'utf-8')
                                if 'comprobante' in filename.lower():
                                    imagen_data = part.get_payload(decode=True)
                                    if imagen_data:
                                        comprobante['imagenes'].append({
                                            'tipo': part.get_content_type(),
                                            'datos': base64.b64encode(imagen_data).decode('utf-8'),
                                            'nombre': filename
                                        })
                            except Exception as img_error:
                                logger.error(f"Error procesando imagen: {img_error}")
                    comprobantes.append(comprobante)
                except Exception as msg_error:
                    logger.error(f"Error procesando mensaje {e_id}: {msg_error}")
        except imaplib.IMAP4.error as auth_error:
            logger.error(f"Error de autenticación IMAP: {auth_error}")
            raise
        finally:
            try: 
                mail.logout()
            except:
                pass
    except Exception as e:
        logger.error(f"Error general: {e}", exc_info=True)
        raise
    return comprobantes

def notificaciones_json(request):
    """Endpoint para obtener notificaciones en formato JSON."""
    try:
        comprobantes = get_comprobantes()
        response_data = {
            'count': len(comprobantes),
            'notifications': [
                {
                    'asunto': c.get('subject', 'Sin asunto'),
                    'remitente': c.get('from', 'Remitente desconocido'),
                    'codigo_cliente': c.get('codigo_cliente', 'No encontrado'),
                    'fecha': c.get('date', 'Fecha no disponible'),
                    'imagenes': c.get('imagenes', []),
                    'empresa_id': c.get('empresa_id')
                } 
                for c in comprobantes
            ]
        }
        return JsonResponse(response_data)
    except Exception as e:
        logger.error(f"Error en notificaciones_json: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': 'Error al obtener notificaciones',
            'detalle': str(e)
        }, status=500, safe=False)


# de aqui empiezan lo correos
def actualizar_estado_pago(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id)
    pago.pagado = not pago.pagado
    pago.save()
    messages.success(request, f"El estado del pago se actualizó a: {'Pagado' if pago.pagado else 'Pendiente'}.")
    return redirect('historial_pagos', empresa_id=pago.empresa.id)

@require_POST
def enviar_notificacion(request, empresa_id):
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    try:
        ultimo_cobro = empresa.cobros.order_by('-fecha_fin').first()
        next_due = (ultimo_cobro.fecha_fin + relativedelta(months=1)) if ultimo_cobro else timezone.now().date()
        
        success = send_manual_payment_email(empresa, next_due)
        
        HistorialNotificaciones.objects.create(
            empresa=empresa,
            usuario=request.user,
            estado=success,
            fecha_envio=timezone.now()
        )
        
        if success:
            messages.success(request, 'Notificación enviada exitosamente')
        else:
            messages.error(request, 'Error al enviar la notificación')
            
    except Exception as e:
        logger.error(f"Error crítico: {str(e)}", exc_info=True)
        messages.error(request, 'Error grave al procesar la solicitud')
    
    return redirect('gestion_pagos', empresa_id=empresa_id)




