from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from WEB.models import RegistroEmpresas,VigenciaPlan
from .models import Transaccion
from .forms import TransaccionForm



# Vista para la página de inicio del supervisor en el módulo de contabilidad
@login_required
def supervisor_home_contabilidad(request, empresa_id,vigencia_plan_id):
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    vigencia_plan = get_object_or_404(VigenciaPlan, id=vigencia_plan_id, empresa=empresa)  

    if request.method == 'POST':
        form = TransaccionForm(request.POST)
        if form.is_valid():
            transaccion = form.save(commit=False)
            transaccion.empresa = empresa
            transaccion.save()
            return redirect('supervisor_home_contabilidad', empresa_id=empresa.id)
    else:
        form = TransaccionForm()
    
    # Obtener lista de transacciones para mostrar en la tabla
    transacciones = Transaccion.objects.filter(empresa=empresa)
    
    context = {
        'empresa': empresa,
        'vigencia_plan': vigencia_plan,
        'form_transaccion': form,
        'transacciones': transacciones,
    }
    return render(request, 'Modulo_contabilidad/supervisor_home_contabilidad.html', context)