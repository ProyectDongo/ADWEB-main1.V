from WEB.models import *
from WEB.forms import *
from WEB.views import *
from WEB.decorators import permiso_requerido
import datetime,email,logging,os,imaplib,base64
from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from email.mime.image import MIMEImage
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
from dateutil.relativedelta import relativedelta
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from email.header import decode_header






logger = logging.getLogger(__name__)
def get_next_due(empresa):
    """Devuelve la fecha (primer día del mes actual o del siguiente) del próximo pago pendiente."""
    hoy = timezone.now()
    current_due = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if not Pago.objects.filter(
        empresa=empresa,
        fecha_pago__year=current_due.year,
        fecha_pago__month=current_due.month
    ).exists():
        return current_due
    next_due = current_due + relativedelta(months=1)
    while Pago.objects.filter(
        empresa=empresa,
        fecha_pago__year=next_due.year,
        fecha_pago__month=next_due.month
    ).exists():
        next_due += relativedelta(months=1)
    return next_due

def gestion_pagos(request, empresa_id):
    """
    Vista para gestionar el pago de una empresa.
    Según el método de pago seleccionado:
      - Si es **abono** se toma el monto ingresado; si es menor que el total, se crea
        un pago pendiente para el siguiente mes.
      - Si es **cobranza**, se crea el pago pendiente y se envía el correo de cobranza.
      - Otros métodos (cheque, automático, tarjeta, débito, manual) confirman el pago.
    """
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    vigencia_planes_activos = empresa.vigencias.filter(estado='indefinido')
    vigencia_planes_suspendidos = empresa.vigencias.filter(estado='suspendido')
    total = sum(vp.monto_final for vp in vigencia_planes_activos)
    
    hoy = timezone.now()
    next_due = get_next_due(empresa)
    
    if request.method == 'POST':
        # Si no se confirma y la fecha de pago corresponde a otro mes, se muestra la confirmación
        if not request.POST.get('confirmar') and (next_due.month != hoy.month or next_due.year != hoy.year):
            selected_planes_ids = request.POST.getlist('planes')
            metodo = request.POST.get('metodo')
            context = {
                'empresa': empresa,
                'codigo_cliente': empresa.codigo_cliente,
                'proximo_mes': next_due,
                'planes': selected_planes_ids,
                'metodo': metodo,
            }
            return render(request, 'side_menu/clientes/lista_clientes/pagos/confirmacion/confirmar_pago.html', context)
        
        if request.POST.get('confirmar'):
            next_due_str = request.POST.get('next_due')
            next_due = datetime.datetime.strptime(next_due_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.get_current_timezone())
                
        selected_planes_ids = request.POST.getlist('planes')
        selected_planes = vigencia_planes_activos.filter(id__in=selected_planes_ids)
        metodo = request.POST.get('metodo')
        total_amount = sum(vp.monto_final for vp in selected_planes)
        
        if metodo == 'abono':
            try:
                abono_amount = float(request.POST.get('monto_abono', 0))
            except ValueError:
                abono_amount = 0
            if abono_amount <= 0 or abono_amount > total_amount:
                messages.error(request, "El monto de abono debe ser mayor que 0 y menor o igual al total.")
                return redirect('gestion_pagos', empresa_id=empresa.id)
            # Crear pago de abono confirmado
            pago_abono = Pago.objects.create(
                empresa=empresa,
                monto=abono_amount,
                metodo=metodo,
                pagado=True,
                fecha_pago=timezone.now()
            )
            pago_abono.vigencia_planes.set(selected_planes)
            pending_amount = total_amount - abono_amount
            if pending_amount > 0:
                # Crear pago pendiente para el próximo mes
                next_due_pending = get_next_due(empresa)
                Pago.objects.create(
                    empresa=empresa,
                    monto=pending_amount,
                    metodo=metodo,
                    pagado=False,
                    fecha_pago=next_due_pending
                )
        elif metodo == 'cobranza':
            pago = Pago.objects.create(
                empresa=empresa,
                monto=total_amount,
                metodo=metodo,
                pagado=False,
                fecha_pago=next_due
            )
            pago.vigencia_planes.set(selected_planes)
            send_cobranza_email(empresa, total_amount)
        else:
            # Para métodos: cheque, automático, tarjeta_credito, débito, manual
            pago = Pago.objects.create(
                empresa=empresa,
                monto=total_amount,
                metodo=metodo,
                pagado=True,
                fecha_pago=timezone.now()
            )
            pago.vigencia_planes.set(selected_planes)
            if metodo == 'manual':
                send_manual_payment_email(empresa, timezone.now())
        
        # Una vez efectuado el pago, se marca la empresa como al día.
        empresa.estado = 'aldia'
        empresa.save()
        messages.success(request, 'Los pagos se efectuaron correctamente')
        return redirect('listar_clientes')
    
    return render(request, 'side_menu/clientes/lista_clientes/pagos/gestion_pagos.html', {
        'empresa': empresa,
        'codigo_cliente': empresa.codigo_cliente,
        'vigencia_planes_activos': vigencia_planes_activos,
        'vigencia_planes_suspendidos': vigencia_planes_suspendidos,
        'total': total,
    })

def toggle_plan(request, vigencia_id):
    """Alterna el estado de un plan (de indefinido a suspendido y viceversa)."""
    vigencia = get_object_or_404(VigenciaPlan, id=vigencia_id)
    vigencia.estado = 'suspendido' if vigencia.estado == 'indefinido' else 'indefinido'
    vigencia.save()
    return redirect('gestion_pagos', empresa_id=vigencia.empresa.id)

def historial_pagos(request, empresa_id):
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    return render(request, 'side_menu/clientes/lista_clientes/pagos/historial/historial_pagos.html', {
        'empresa': empresa,
        'pagos': empresa.pagos.all()
    })

def actualizar_estado_pago(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id)
    pago.pagado = not pago.pagado
    pago.save()
    messages.success(request, f"El estado del pago se actualizó a: {'Pagado' if pago.pagado else 'Pendiente'}.")
    return redirect('historial_pagos', empresa_id=pago.empresa.id)

def send_manual_payment_email(empresa, next_due): 
    """Envía correo con instrucciones para pago manual."""
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
    html_content = render_to_string('empresas/email/instrucciones_pago_manual.html', context)
    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    with open(logo_path, "rb") as img:
        logo = MIMEImage(img.read())
        logo.add_header("Content-ID", "<logo_cid>")
        logo.add_header("Content-Disposition", "inline")
        msg.attach(logo)
    msg.send()

def send_cobranza_email(empresa, deuda):
    """Envía correo de cobranza con los datos de la cuenta para realizar la transferencia."""
    transfer_data = {
        'banco': 'Banco Ficticio',
        'tipo_cuenta': 'Cuenta Corriente',
        'numero_cuenta': '1234567890',
        'titular': empresa.nombre,
    }
    subject = f"Notificación de Cobranza | Cliente: {empresa.codigo_cliente} | EmpresaID: {empresa.id}"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = [empresa.email]
    logo_path = os.path.join(settings.BASE_DIR, "static/png/logo.png")
    context = {
        'empresa': empresa,
        'codigo_cliente': empresa.codigo_cliente,
        'transfer_data': transfer_data,
        'deuda': deuda,
        'empresa_id': empresa.id,
    }
    html_content = render_to_string('empresas/email/notificacion_cobranza.html', context)
    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    with open(logo_path, "rb") as img:
        logo = MIMEImage(img.read())
        logo.add_header("Content-ID", "<logo_cid>")
        logo.add_header("Content-Disposition", "inline")
        msg.attach(logo)
    msg.send()

def planes_por_empresa(request, empresa_id):
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    vigencias = VigenciaPlanes.objects.filter(empresa=empresa)
    return render(request, 'planes_por_empresa.html', {'vigencias': vigencias})


def get_comprobantes():
    """Obtiene comprobantes de pago extrayendo el código cliente y empresa_id."""
    comprobantes = []
    try:
        IMAP_SERVER = 'imap.gmail.com'
        EMAIL_ACCOUNT = 'anghello3569molina@gmail.com'
        PASSWORD = 'bncuzhavbtvuqjpi'
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

def lista_deudas(request):
    """
    Vista que recopila todas las empresas que tienen pagos pendientes,
    calculando la deuda total (suma de los montos de pagos no confirmados).
    """
    empresas = RegistroEmpresas.objects.all()
    empresas_con_deuda = []
    for empresa in empresas:
        pending_payments = empresa.pagos.filter(pagado=False)
        deuda = sum(p.monto for p in pending_payments)
        if deuda > 0:
            empresa.deuda_pendiente = deuda
            empresas_con_deuda.append(empresa)
    return render(request, 'side_menu/clientes/lista_clientes/pagos/deudas/deudas_empresas.html', {'empresas': empresas_con_deuda})

def notificar_cobranza(request, empresa_id):
    """
    Al presionar el botón “Notificar Cobranza” de la plantilla,
    se envía el correo con los datos de la cuenta para transferir.
    """
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    pending_payments = empresa.pagos.filter(pagado=False)
    deuda = sum(p.monto for p in pending_payments)
    if deuda <= 0:
        messages.info(request, "La empresa no tiene deuda pendiente.")
        return redirect('lista_deudas')
    send_cobranza_email(empresa, deuda)
    messages.success(request, "Correo de cobranza enviado correctamente.")
    return redirect('lista_deudas')

def actualizar_pagos_vencidos(request):
    """
    Recorre los pagos con fecha de creación mayor a 1 mes y que aún no se han confirmado,
    marcando la empresa como pendiente y suspendiendo los planes activos.
    """
    one_month_ago = timezone.now() - relativedelta(months=1)
    overdue_payments = Pago.objects.filter(pagado=False, fecha_pago__lt=one_month_ago)
    for pago in overdue_payments:
        empresa = pago.empresa
        empresa.estado = 'pendiente'
        empresa.save()
        vigencias = empresa.vigencias.filter(estado='indefinido')
        for vp in vigencias:
            vp.estado = 'suspendido'
            vp.save()
    messages.success(request, "Se han actualizado los pagos vencidos a pendiente y suspendido los planes correspondientes.")
    return redirect('listar_clientes')
