function addForm(formsetId) {
    const formsContainer = document.getElementById(`${formsetId}-forms`);
    if (!formsContainer || formsContainer.children.length === 0) {
        console.error(`No se encontró el contenedor o está vacío para ${formsetId}`);
        return;
    }
    
    const formCount = formsContainer.children.length;
    const totalForms = document.getElementById(`id_${formsetId}-TOTAL_FORMS`);
    const newForm = formsContainer.children[0].cloneNode(true);
    
    const inputs = newForm.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        if (input.type === 'checkbox') {
            input.checked = false;
        } else if (input.type !== 'button') {
            input.value = '';
        }
        const name = input.getAttribute('name');
        if (name) {
            input.setAttribute('name', name.replace(/-\d+-/, `-${formCount}-`));
        }
        const id = input.getAttribute('id');
        if (id) {
            input.setAttribute('id', id.replace(/-\d+-/, `-${formCount}-`));
        }
    });
    
    formsContainer.appendChild(newForm);
    totalForms.value = parseInt(totalForms.value) + 1;
}

function markForDeletion(button, formsetId) {
    const row = button.closest('tr');
    const deleteInput = row.querySelector('input[name$="-DELETE"]');
    if (deleteInput) {
        deleteInput.checked = true; // Marcar para eliminación
        row.style.display = 'none'; // Ocultar la fila visualmente
    } else {
        row.remove(); // Si es un formulario nuevo, eliminarlo directamente
        updateTotalForms(formsetId);
    }
}

function updateTotalForms(formsetId) {
    const formsContainer = document.getElementById(`${formsetId}-forms`);
    const totalForms = document.getElementById(`id_${formsetId}-TOTAL_FORMS`);
    totalForms.value = formsContainer.children.length;
}
