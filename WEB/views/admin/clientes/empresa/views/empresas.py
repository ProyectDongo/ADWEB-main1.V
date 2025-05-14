from WEB.models import *
from WEB.forms import *
from WEB.views.scripts import *
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404,redirect,render
from django.http import JsonResponse,HttpResponse
from django.views.decorators.http import require_POST
from django.db.models import Prefetch
from django.forms.models import modelformset_factory
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings



@login_required
@permiso_requerido("WEB.crear_empresa")
def crear_empresa(request):
    """
    Vista para crear una nueva empresa y su vigencia de plan.
    Ya NO crea el usuario supervisor ni envía ningún correo.
    """
    if request.method == 'POST':
        empresa_form = EmpresaForm(request.POST)
        vigencia_form = PlanVigenciaForm(request.POST)

        # Quitamos el campo 'empresa' del form de vigencia (lo asignamos manual)
        vigencia_form.fields.pop('empresa', None)

        if empresa_form.is_valid() and vigencia_form.is_valid():
            # Guardamos la empresa
            empresa = empresa_form.save(commit=False)
            empresa.plan_contratado = vigencia_form.cleaned_data['plan']
            empresa.save()

            # Guardamos la vigencia de plan enlazando la empresa
            vigencia = vigencia_form.save(commit=False)
            vigencia.empresa = empresa
            vigencia.save()

            # Mensaje de éxito
            messages.success(request,
                "Empresa y vigencia de plan creadas correctamente."
            )
            return redirect('listar_clientes')

        # Si hay errores, se volverá a renderizar el formulario con los mensajes automáticos
    else:
        empresa_form = EmpresaForm()
        vigencia_form = PlanVigenciaForm()
        vigencia_form.fields.pop('empresa', None)

    return render(request,
                  'admin/clientes/lista_clientes/crear_empresa/crear_empresa.html',
                  {
                      'empresa_form': empresa_form,
                      'vigencia_form': vigencia_form
                  }
    )










@login_required
@permiso_requerido("WEB.detalles_empresa")
def detalle_empresa(request, pk):
    """
    Vista para mostrar y editar los detalles de una empresa específica.

    Esta vista permite a los usuarios autenticados ver y editar los detalles de una empresa específica.
    También permite eliminar la empresa si se solicita. Además, muestra un historial de cambios recientes
    y una lista de supervisores y trabajadores asociados a la empresa.

    :param request: HttpRequest
    :param pk: ID de la empresa a mostrar y editar
    :return: Renderizado del template 'empresas/detalles_empresa.html' con los detalles de la empresa
    """
    # Obtener el objeto RegistroEmpresas o devolver un 404 si no existe
    supervisores = Usuario.objects.filter(role='Supervisor', empresa_id=pk)
    empresa = get_object_or_404(RegistroEmpresas, pk=pk)
    vigencias = empresa.vigencias.all()
    
    # Obtener el historial de cambios recientes para la empresa
    historial = HistorialCambios.objects.filter(empresa=empresa).order_by('-fecha')[:10]
    
    # Filtrar usuarios por grupo y empresa
    trabajadores = Usuario.objects.filter(role='Trabajador', empresa_id=pk)

    if request.method == 'POST':
        if 'guardar' in request.POST:
            # Si se solicita guardar, crear un formulario con los datos enviados y la instancia de la empresa
            form = EmpresaForm(request.POST, instance=empresa)
            if form.is_valid():
                # Si el formulario es válido, guardar los cambios
                form.save()
                # Registrar en historial
                HistorialCambios.objects.create(
                    empresa=empresa,
                    usuario=request.user,
                    descripcion="Modificación de datos empresariales"
                )
                # Mostrar un mensaje de éxito
                messages.success(request, 'Cambios guardados exitosamente!')
                # Redirigir a la vista de detalles de la empresa
                return redirect('detalle_empresa', pk=pk)
                
        elif 'eliminar' in request.POST:
            # Si se solicita eliminar, eliminar la empresa
            empresa.delete()
            # Mostrar un mensaje de éxito
            messages.success(request, 'Empresa eliminada correctamente')
            # Redirigir a la lista de empresas
            return redirect('listar_clientes')

    else:
        # Si la solicitud es GET, crear un formulario con la instancia de la empresa
        form = EmpresaForm(instance=empresa)

    # Renderizar el template con la empresa, el formulario, los supervisores, los trabajadores y el historial
    return render(request, 'admin/clientes/lista_clientes/administrar/detalles_empresa.html', {
        'empresa': empresa,
        'vigencias': vigencias,
        'form': form,
        'supervisores': supervisores,
        'trabajadores': trabajadores,
        'historial': historial
    })








@login_required
@permiso_requerido("WEB.vista_empresas")
def listar_clientes(request):
    empresas = RegistroEmpresas.objects.filter(eliminada=False)
    
    query = request.GET.get('q')
    if query:
        empresas = empresas.filter(nombre__icontains=query)
    
  
    empresas = empresas.prefetch_related(
        Prefetch('cobros', queryset=Cobro.objects.filter(vigencia_plan__isnull=True)),
        Prefetch('vigencias', queryset=VigenciaPlan.objects.prefetch_related('cobros_relacionados'))
    )
    
    for empresa in empresas:
    
        one_time_cobro_paid = any(
            cobro.vigencia_plan is None and cobro.estado == 'pagado'
            for cobro in empresa.cobros.all()
        )
        
        for vigencia in empresa.vigencias.all():
            if one_time_cobro_paid:
                vigencia.pago_pendiente = False
            else:
                
                has_pending = any(c.estado == 'pendiente' for c in vigencia.cobros_relacionados.all())
                vigencia.pago_pendiente = has_pending
    
    return render(request, 'admin/clientes/lista_clientes/home/listar_clientes.html', {'empresas': empresas})





@login_required
def eliminar_empresa(request, pk):
    empresa = get_object_or_404(RegistroEmpresas, id=pk)
    empresa.eliminada = True
    empresa.save()
    messages.success(request, 'Empresa marcada como eliminada')
    return redirect('listar_clientes')
@login_required
def listar_empresas_eliminadas(request):
    empresas = RegistroEmpresas.objects.filter(eliminada=True)
    return render(request, 'admin/clientes/lista_clientes/ver_eliminados/listar_empresas_eliminadas.html', {'empresas': empresas})
@login_required
def recuperar_empresa(request, id):
    empresa = get_object_or_404(RegistroEmpresas, id=id)
    empresa.eliminada = False
    empresa.save()
    messages.success(request, 'Empresa recuperada exitosamente')
    return redirect('listar_empresas_eliminadas')









@login_required
def vigencia_planes(request, pk):
    empresa = get_object_or_404(RegistroEmpresas, id=pk)
    plan_id = request.GET.get('plan_id')
    plan = get_object_or_404(Plan, id=plan_id) if plan_id else None

    if request.method == 'POST':
        form = PlanVigenciaForm(request.POST)
        if form.is_valid():
            vigencia_plan = form.save(commit=False)
            vigencia_plan.empresa = empresa
            if plan:
                vigencia_plan.plan = plan
            try:
                vigencia_plan.calcular_monto()
                vigencia_plan.save()
                return redirect('listar_clientes')
            except ValueError as e:
                form.add_error(None, str(e))
    else:
        initial = {'empresa': empresa.id, 'plan': plan.id if plan else None}
        if plan:
            initial.update({
                'precio_original': plan.valor,
                'codigo_plan': f"{empresa.nombre}_{plan.nombre}".replace(' ', '_').upper()
            })
        form = PlanVigenciaForm(initial=initial)
        form.fields['empresa'].disabled = True

    return render(request, 'admin/clientes/lista_clientes/nuevo_plan/vigencia_planes.html', {
        'form': form,
        'plan': plan,
        'empresa': empresa
    })





@login_required
def check_codigo_plan(request):
    codigo = request.GET.get('codigo', '')
    exists = VigenciaPlan.objects.filter(codigo_plan__iexact=codigo).exists()
    return JsonResponse({'exists': exists})




