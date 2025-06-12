   window.toggleEstado = function(vigenciaId, button) {
            const url = `/vigencia_plan/${vigenciaId}/toggle_estado/`;
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Accept': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const row = button.closest('tr');
                    const estadoCell = row.querySelector('td:nth-child(6)');
                    estadoCell.textContent = data.new_estado_display;
                    
                    row.classList.toggle('table-danger', data.new_estado === 'suspendido');
                    
                    if (data.new_estado === 'suspendido') {
                        button.textContent = 'Habilitar';
                        button.classList.replace('btn-warning', 'btn-success');
                    } else {
                        button.textContent = 'Deshabilitar';
                        button.classList.replace('btn-success', 'btn-warning');
                    }
                    
                    row.querySelectorAll('.action-btn').forEach(btn => {
                        btn.disabled = data.new_estado === 'suspendido';
                    });
                }
            });
        };

            
            // Efecto de vibración periódica para el mensaje
            const mensaje = document.getElementById('mensaje-pago-atrasado');
            if (mensaje) {
                setInterval(() => {
                    mensaje.classList.add('shake');
                    setTimeout(() => {
                        mensaje.classList.remove('shake');
                    }, 1000);
                }, 5000);
            }