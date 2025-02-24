import imaplib
import email
import re
import base64
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

def get_comprobantes():
    """Obtiene comprobantes de pago del correo electrónico con manejo robusto de errores."""
    comprobantes = []
    
    try:
        # Configuración IMAP (deberías usar variables de entorno en producción)
        IMAP_SERVER = 'imap.gmail.com'
        EMAIL_ACCOUNT = 'anghello3569molina@gmail.com'
        PASSWORD = 'bncuzhavbtvuqjpi'

        # Conexión segura con timeout
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, timeout=10)
        
        try:
            # Autenticación
            mail.login(EMAIL_ACCOUNT, PASSWORD)
            mail.select('inbox')

            # Búsqueda de mensajes
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
                        'imagenes': []
                    }

                    # Procesamiento del cuerpo
                    body = ""
                    for part in msg.walk():
                        if part.get_content_type() == 'text/plain':
                            try:
                                body = part.get_payload(decode=True).decode(errors='replace')
                                break
                            except Exception as decode_error:
                                logger.error(f"Error decodificando cuerpo: {decode_error}")
                                continue

                    # Extracción código cliente
                    if body:
                        match = re.search(r'Código Cliente:\s*(\w+)', body)
                        if match:
                            comprobante['codigo_cliente'] = match.group(1)

                    # Procesamiento de imágenes
                    for part in msg.walk():
                        if part.get_content_maintype() == 'image':
                            try:
                                imagen_data = part.get_payload(decode=True)
                                if imagen_data and len(imagen_data) > 0:
                                    comprobante['imagenes'].append({
                                        'tipo': part.get_content_type(),
                                        'datos': base64.b64encode(imagen_data).decode('utf-8')
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
            except Exception as logout_error:
                logger.error(f"Error cerrando conexión: {logout_error}")

    except Exception as general_error:
        logger.error(f"Error general en get_comprobantes: {general_error}", exc_info=True)
        raise

    return comprobantes