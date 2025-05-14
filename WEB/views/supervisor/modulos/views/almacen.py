
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from WEB.models import RegistroEmpresas, VigenciaPlan, ItemInventario
from WEB.forms import ItemInventarioForm


@login_required
def supervisor_home_almacen(request, empresa_id,vigencia_plan_id):
    empresa = get_object_or_404(RegistroEmpresas, id=empresa_id)
    vigencia_plan = get_object_or_404(VigenciaPlan, id=vigencia_plan_id, empresa=empresa)  

    # Verificar si el usuario tiene permisos para acceder a esta vista  
    if request.method == 'POST':
        form = ItemInventarioForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.empresa = empresa
            item.save()
            return redirect('supervisor_home_almacen', empresa_id=empresa.id)
    else:
        form = ItemInventarioForm()
    
    # Obtener lista de ítems para mostrar en la tabla
    items = ItemInventario.objects.filter(empresa=empresa)
    
    context = {
        'empresa': empresa,
        'vigencia_plan': vigencia_plan,
        'form_inventario': form,
        'items': items,
    }
    return render(request, 'home/supervisores/supervisor_home_almacen.html', context)