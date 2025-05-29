from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib import messages
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect
from django_recaptcha.fields import ReCaptchaField  
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect, Http404
#from django.contrib.gis.geos import Point
from WEB.models import  Usuario, RegistroEmpresas, RegistroEntrada, VigenciaPlan
from WEB.forms import *
from django.views import View
from django.views.generic import DetailView
import logging
import datetime
from datetime import timedelta, date
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors






class RoleBasedLoginMixin:
    role = None  # Debe ser definido en las clases hijas
    max_attempts = 5  # Intentos máximos antes de bloquear
    captcha_threshold = 3  # Intentos para mostrar CAPTCHA

    def form_valid(self, form):
        user = form.get_user()
        
        # Verificación de rol y estado de cuenta
        if not self.validate_role(user):
            messages.error(self.request, 'Acceso no autorizado para este tipo de usuario')
            return self.form_invalid(form)
            
        if not self.check_account_status(user):
            messages.error(self.request, 'Cuenta bloqueada. Contacte al administrador')
            return self.form_invalid(form)
            
        self.handle_successful_login(user)
        return super().form_valid(form)

    def form_invalid(self, form):
        if form is not None:  # Verificamos que form no sea None
            username = form.cleaned_data.get('username')
            user = self.get_user_safe(username)
            
            # Actualizar intentos fallidos
            self.update_failed_attempts(user)
            self.update_session_attempts()
            
            # Aplicar medidas de seguridad
            self.add_captcha_if_needed(form)
            self.check_and_lock_account(user)
        
        return super().form_invalid(form)

    # Métodos auxiliares
    def validate_role(self, user):
        return hasattr(user, 'role') and user.role == self.role

    def check_account_status(self, user):
        return not user.is_locked

    def handle_successful_login(self, user):
        user.failed_login_attempts = 0
        user.last_failed_login = None
        user.save()
        
        # Reiniciar contador de sesión
        if 'failed_attempts' in self.request.session:
            del self.request.session['failed_attempts']

    def get_user_safe(self, username):
        try:
            return Usuario.objects.get(username=username)
        except Usuario.DoesNotExist:
            return None

    def update_failed_attempts(self, user):
        if user:
            user.failed_login_attempts += 1
            user.last_failed_login = timezone.now()
            user.save()

    def update_session_attempts(self):
        attempts = self.request.session.get('failed_attempts', 0) + 1
        self.request.session['failed_attempts'] = attempts

    def add_captcha_if_needed(self, form):
        session_attempts = self.request.session.get('failed_attempts', 0)
        if session_attempts >= self.captcha_threshold:
            form.fields['captcha'] = ReCaptchaField()
            messages.warning(self.request, 'Verificación de seguridad requerida')

    def check_and_lock_account(self, user):
        if user and user.failed_login_attempts >= self.max_attempts:
            user.is_locked = True
            user.save()
            messages.error(self.request, 'Cuenta bloqueada por seguridad')






class LoginUnificado(LoginView):
    template_name = 'login/home/unified_login.html'
    success_url = reverse_lazy('redirect_after_login')

@login_required
def redirect_after_login(request):
    if not hasattr(request.user, 'role'):
        return redirect('login')
    role = request.user.role
    if role == 'admin':
        return redirect('admin_home')
    elif role == 'supervisor':
        return redirect('supervisor_selector')
    elif role == 'trabajador':
        return redirect('trabajador_home')
    return redirect('login')








# Vista para la página de inicio del administrador
# Esta vista se encarga de mostrar la página de inicio del administrador
@login_required
def admin_home(request):
    return render(request, 'home/admin/admin_home.html')








# generar_reporte
# Vista para generar el reporte de gestión
@login_required
def generar_reporte(request):
    # Cálculo de fechas
    hoy = timezone.now().date()
    inicio_mes = date(hoy.year, hoy.month, 1)
    trimestre_actual = (hoy.month - 1) // 3 + 1
    inicio_trimestre = date(hoy.year, (trimestre_actual - 1) * 3 + 1, 1)
    inicio_año = date(hoy.year, 1, 1)

    # Cálculo de métricas
    # Rentabilidad
    ganancias_mensuales = sum(cobro.monto_pagado() for cobro in Cobro.objects.filter(
        fecha_inicio__gte=inicio_mes, estado='pagado'
    ))
    ganancias_trimestrales = sum(cobro.monto_pagado() for cobro in Cobro.objects.filter(
        fecha_inicio__gte=inicio_trimestre, estado='pagado'
    ))
    ganancias_anuales = sum(cobro.monto_pagado() for cobro in Cobro.objects.filter(
        fecha_inicio__gte=inicio_año, estado='pagado'
    ))

    # Financiamiento
    ingresos = sum(cobro.monto_pagado() for cobro in Cobro.objects.filter(estado='pagado'))
    egresos = Transaccion.objects.filter(tipo='Egreso').aggregate(total=Sum('monto'))['total'] or 0
    saldo_acumulado = ingresos - egresos

    # Usuarios
    usuarios_activos = Usuario.objects.filter(is_active=True).count()
    usuarios_inactivos = Usuario.objects.filter(is_active=False).count()
    nuevos_usuarios = Usuario.objects.filter(date_joined__date__gte=inicio_mes).count()
    usuarios_activados = Usuario.objects.filter(date_joined__date__gte=inicio_mes, is_active=True).count()
    tasa_activacion = (usuarios_activados / nuevos_usuarios * 100) if nuevos_usuarios > 0 else 0

    # Módulos
    operaciones_asistencia = RegistroEntrada.objects.count()
    operaciones_almacen = ItemInventario.objects.count()
    operaciones_contabilidad = Transaccion.objects.count()

    # Configuración del PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=80,  # Aumentado para dar más espacio al encabezado
        bottomMargin=60
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    styles.add(ParagraphStyle(
        name='Header1',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12
    ))
    
    styles.add(ParagraphStyle(
        name='Header2',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#2980b9'),
        spaceAfter=8,
        spaceBefore=12
    ))
    
    body_text_style = styles['BodyText']
    body_text_style.textColor = colors.HexColor('#2c3e50')
    body_text_style.spaceAfter = 6

    elements = []
    
    # Encabezado con logo y texto
    logo_path = 'static/png/logo.png'
    logo = Image(logo_path, width=150, height=50)  # Tamaño ajustado del logo

    header_text = Paragraph(
        f"<b>Reporte de Gestión</b><br/>"
        f"Período: {inicio_mes.strftime('%d/%m/%Y')} - {hoy.strftime('%d/%m/%Y')}<br/>"
        f"Generado por: {request.user.get_full_name() or request.user.username}",
        styles['Header1']
    )
    
    # Tabla para alinear logo y texto
    header_table = Table([
        [logo, header_text]
    ], colWidths=[150, 400])  # Ajustar el ancho de las columnas
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),  # Alinear verticalmente al tope
        ('ALIGN', (0,0), (0,0), 'LEFT'),    # Alinear el logo a la izquierda
        ('ALIGN', (1,0), (1,0), 'LEFT'),    # Alinear el texto a la izquierda
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 24))  # Espacio después del encabezado

    # Función para formatear moneda
    def currency(value):
        return f"${value:,.2f}" if value else "$0.00"

    # Función para añadir secciones
    def add_section(title, data):
        elements.append(Paragraph(title, styles['Header2']))
        table_data = [
            [Paragraph('<b>Concepto</b>', styles['BodyText']), 
             Paragraph('<b>Valor</b>', styles['BodyText'])]
        ]
        for label, value in data:
            table_data.append([
                Paragraph(label, styles['BodyText']),
                Paragraph(str(value), styles['BodyText'])
            ])
        section_table = Table(table_data, colWidths=[250, 150])
        section_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#2c3e50')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#bdc3c7')),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#ecf0f1'))
        ]))
        elements.append(section_table)
        elements.append(Spacer(1, 12))

    # Sección de Rentabilidad
    add_section('Indicadores de Rentabilidad', [
        ('Ganancias del Mes', currency(ganancias_mensuales)),
        ('Ganancias del Trimestre', currency(ganancias_trimestrales)),
        ('Ganancias Anuales', currency(ganancias_anuales))
    ])

    # Sección Financiera
    add_section('Situación Financiera', [
        ('Ingresos Totales', currency(ingresos)),
        ('Egresos Totales', currency(egresos)),
        ('Saldo Neto', currency(saldo_acumulado))
    ])

    # Sección de Usuarios
    add_section('Estadísticas de Usuarios', [
        ('Usuarios Activos', usuarios_activos),
        ('Usuarios Inactivos', usuarios_inactivos),
        ('Nuevos Registros (Mes)', nuevos_usuarios),
        ('Tasa de Activación', f"{tasa_activacion:.2f}%")
    ])

    # Sección de Módulos
    elements.append(Paragraph('Actividad por Módulos', styles['Header2']))
    modules_data = [
        ['Módulo', 'Operaciones'],
        ['Control de Asistencia', operaciones_asistencia],
        ['Gestión de Almacén', operaciones_almacen],
        ['Operaciones Contables', operaciones_contabilidad]
    ]
    
    module_table = Table(modules_data, colWidths=[250, 150])
    module_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#bdc3c7')),
        ('BOTTOMPADDING', (0,0), (-1,0), 6)
    ]))
    elements.append(module_table)
    elements.append(Spacer(1, 24))

    # Pie de página
    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#7f8c8d'))
        canvas.drawString(40, 40, f"Página {doc.page} | Reporte generado el {hoy.strftime('%d/%m/%Y %H:%M')}")
        canvas.drawRightString(550, 40, "Sistema de Gestión Integral v1.0")
        canvas.restoreState()

    # Generar PDF
    doc.build(elements, onFirstPage=add_footer, onLaterPages=add_footer)

    # Preparar respuesta
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_gestion.pdf"'
    response.write(pdf)
    return response












# Vista para la página de configuración
@login_required
def configuracion_home(request):
    return render(request, 'admin/sofware/home/configuracion_home.html')




# Vista para seleccionar el módulo del supervisor
# Esta vista se encarga de mostrar los módulos disponibles para el supervisor
@login_required
def supervisor_selector_modulo(request, empresa_id):
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    
    # Obtener todos los planes activos agrupados por tipo
    active_vigencias = VigenciaPlan.objects.filter(
        empresa=empresa,
        estado__in=['indefinido', 'mensual'],
        fecha_inicio__lte=timezone.now().date()
    ).filter(
        Q(fecha_fin__gte=timezone.now().date()) | Q(fecha_fin__isnull=True)
    ).select_related('plan').order_by('plan__codigo', '-fecha_inicio')
    
    # Agrupar por tipo de módulo
    grouped_modules = {}
    for vp in active_vigencias:
        module_type = vp.plan.codigo
        if module_type not in grouped_modules:
            grouped_modules[module_type] = {
                'display_name': vp.plan.nombre,
                'icon': MODULE_ICONS.get(module_type, 'fas fa-cube'),
                'items': []
            }
        grouped_modules[module_type]['items'].append(vp)
    
    context = {
        'empresa': empresa,
        'grouped_modules': grouped_modules
    }
    return render(request, 'login/supervisor/supervisor.selector.html', context)

MODULE_ICONS = {
    'asistencia': 'fas fa-fingerprint',
    'contabilidad': 'fas fa-calculator',
    'almacen': 'fas fa-warehouse'
}





#------------ FIN ------------


