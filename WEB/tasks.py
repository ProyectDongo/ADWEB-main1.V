from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_reports_task():
    # Ejemplo de envío de reporte por correo
    subject = 'Reporte Automático Diario'
    message = 'Este es el reporte automático generado por tu aplicación Django.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = ['anghello_md@hotmail.com']  # Cambia esto según tus necesidades
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)