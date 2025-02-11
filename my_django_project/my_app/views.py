from django.shortcuts import render, get_object_or_404, redirect
from .models import VigenciaPlan
from .forms import VigenciaPlanForm

def editar_vigencia_plan(request, id):
    vigencia_plan = get_object_or_404(VigenciaPlan, id=id)
    if request.method == 'POST':
        form = VigenciaPlanForm(request.POST, instance=vigencia_plan)
        if form.is_valid():
            form.save()
            return redirect('listar_empresas')  # Redirect to the list view after saving
    else:
        form = VigenciaPlanForm(instance=vigencia_plan)
    return render(request, 'empresas/editar_vigencia_plan.html', {'form': form})