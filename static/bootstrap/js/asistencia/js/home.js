
document.addEventListener('DOMContentLoaded', function() {
    const vigenciaPlanId = "{{ vigencia_plan.id }}";
    const empresaId = "{{ empresa.id }}";
    const usuarioModal = new bootstrap.Modal('#usuarioModal');
    const urlData = document.getElementById('urls').dataset;
    let currentUser = null;
    let originalEmail = null;

    $.ajaxSetup({
        headers: {
            "X-CSRFToken": "{{ csrf_token }}"
        }
    });

    // Configurar modal
   $('#usuarioModal').on('show.bs.modal', function(e) {
    const isEdit = $(e.relatedTarget).hasClass('edit-user');
    const tipo = $(e.relatedTarget).closest('[data-tipo]').data('tipo') || 'trabajador';
    currentUser = isEdit ? $(e.relatedTarget).data('id') : null;

    if (isEdit) {
        $('#modalTitle').text('Editar Usuario');
        const updateUrl = urlData.update.replace('0', currentUser);
        console.log('URL de actualización:', updateUrl); // Depuración

        // Hacer la petición para obtener los datos del usuario
        fetch(updateUrl, {
            method: 'GET',
            headers: {
                'X-CSRFToken': "{{ csrf_token }}"
            }
        })
        .then(response => {
            if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
            return response.json();
        })
        .then(data => {
            console.log('Datos recibidos:', data); // Depuración
            // Asignar los datos a los campos del formulario
            $('input[name="rut"]').val(data.rut || '');
            $('input[name="username"]').val(data.username || '');
            $('input[name="first_name"]').val(data.first_name || '');
            $('input[name="last_name"]').val(data.last_name || '');
            $('input[name="email"]').val(data.email || '');
            $('input[name="celular"]').val(data.celular || '');
            $('select[name="role"]').val(data.role || '');
            $('select[name="horario"]').val(data.horario || '');
            $('select[name="turno"]').val(data.turno || '');
            $('select[name="metodo_registro_permitido"]').val(data.metodo_registro_permitido || '');
            // Configurar el campo de contraseña para edición
            $('input[name="password"]').val('').attr('placeholder', 'Dejar en blanco para no cambiar').removeAttr('required');
            // Eliminar la opción "admin" del select de roles
            $('select[name="role"] option[value="admin"]').remove();
            originalEmail = data.email;
        })
        .catch(error => {
            console.error('Error al cargar datos:', error);
            Swal.fire('Error', 'No se pudo cargar los datos del usuario', 'error');
        });
    } else {
        $('#modalTitle').text(`Nuevo ${tipo.charAt(0).toUpperCase() + tipo.slice(1)}`);
        // Resetear el formulario para creación
        $('#usuarioForm')[0].reset();
        $('input[name="password"]').attr({'required': true, 'placeholder': 'Contraseña'}).val('');
        $('select[name="role"]').val(tipo);
        // Eliminar la opción "admin" del select de roles
        $('select[name="role"] option[value="admin"]').remove();
        originalEmail = null;
    }

    // Configurar la acción del formulario
    $('#usuarioForm').attr('action', isEdit ? 
        urlData.update.replace('0', currentUser) : 
        urlData.create);
});

    // Validación RUT en tiempo real
    $('body').on('input', '[name="rut"]', _.debounce(function() {
        const rut = $(this).val();
        if (!validarFormatoRUT(rut)) {
            showValidationError(this, 'Formato RUT inválido');
            return;
        }
        
        fetch(`${urlData.validate}?rut=${rut}`)
            .then(r => r.json())
            .then(data => {
                if (data.exists && (!currentUser || $('input[name="rut"]').val() !== data.rut)) {
                    showValidationError(this, 'RUT ya registrado');
                } else {
                    clearValidationError(this);
                }
            });
    }, 300));

    // Validación Celular en tiempo real
    $('body').on('input', '[name="celular"]', _.debounce(function() {
        const celular = $(this).val();
        if (celular && (!celular.startsWith('+') || celular.length < 9)) {
            showValidationError(this, 'Formato inválido. Ej: +56 9 1234 5678');
        } else {
            clearValidationError(this);
        }
    }, 300));

    // Validación Email en tiempo real
    $('body').on('input', '[name="email"]', _.debounce(function() {
        const email = $(this).val();
        if (!isValidEmail(email)) {
            showValidationError(this, 'Formato email inválido');
            return;
        }
        
        if (originalEmail && email === originalEmail) {
            clearValidationError(this);
            return;
        }
        
        fetch(`${urlData.validate}?email=${email}`)
            .then(r => r.json())
            .then(data => {
                if (data.exists) {
                    showValidationError(this, 'Email ya registrado');
                } else {
                    clearValidationError(this);
                }
            });
    }, 300));

    // Envío del formulario
    $('#usuarioForm').on('submit', function(e) {
        e.preventDefault();
        const form = $(this);
        const btn = form.find('button[type="submit"]');
        
        btn.prop('disabled', true);
        btn.find('.submit-text').hide();
        btn.find('.spinner-border').removeClass('d-none');

        $.ajax({
            url: form.attr('action'),
            method: 'POST',
            data: form.serialize(),
            xhrFields: {
                withCredentials: true
            },
            success: function(response) {
                usuarioModal.hide();
                Swal.fire({
                    icon: 'success',
                    title: '¡Guardado!',
                    text: response.message,
                    showConfirmButton: false,
                    timer: 1500
                }).then(() => {
                    if (response.redirect_url) {
                        window.location.replace(response.redirect_url);
                    } else {
                        window.location.replace(`/supervisor/${empresaId}/${vigenciaPlanId}/`);
                    }
                });
            },
            error: function(xhr) {
                if (xhr.status === 403) {
                    Swal.fire({
                        icon: 'warning',
                        title: 'Advertencia',
                        text: 'No puedes cambiar tu propio rol.',
                        confirmButtonText: 'Entendido'
                    });
                } else {
                    const errors = xhr.responseJSON?.errors || {};
                    $('.is-invalid').removeClass('is-invalid');
                    $('.invalid-feedback').remove();
                    
                    Object.keys(errors).forEach(field => {
                        const input = $(`[name="${field}"]`);
                        const container = input.closest('.form-group');
                        
                        input.addClass('is-invalid');
                        if (container.length) {
                            container.append(
                                `<div class="invalid-feedback d-block">${errors[field].join(' ')}</div>`
                            );
                        } else {
                            input.after(
                                `<div class="invalid-feedback d-block">${errors[field].join(' ')}</div>`
                            );
                        }
                    });
                    
                    if (Object.keys(errors).length === 0) {
                        Swal.fire('Error', xhr.responseJSON?.error || 'Error desconocido', 'error');
                    }
                }
            },
            complete: function() {
                btn.prop('disabled', false);
                btn.find('.submit-text').show();
                btn.find('.spinner-border').addClass('d-none');
            }
        });
    });

    // Eliminar usuario
    $('body').on('click', '.delete-user', function() {
        const userId = $(this).data('id');
        
        Swal.fire({
            title: '¿Eliminar usuario?',
            text: 'Esta acción no se puede deshacer',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: `${urlData.delete.replace('0', userId)}`,
                    method: 'DELETE',
                    success: function(response) {
                        Swal.fire({
                            icon: 'success',
                            title: '¡Eliminado!',
                            text: response.message,
                            showConfirmButton: false,
                            timer: 1500
                        }).then(() => {
                            location.reload();
                        });
                    },
                    error: function(xhr) {
                        Swal.fire('Error', xhr.responseJSON?.error || 'Error al eliminar', 'error');
                    }
                });
            }
        });
    });

    // Funciones de ayuda
    function validarFormatoRUT(rut) {
        return /^[0-9]{7,8}-[0-9kK]$/.test(rut);
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function showValidationError(field, message) {
        $(field).addClass('is-invalid');
        $(field).next('.invalid-feedback').text(message).show();
    }

    function clearValidationError(field) {
        $(field).removeClass('is-invalid');
        $(field).next('.invalid-feedback').hide();
    }

    async function actualizarNotificaciones() {
        try {
            const url = document.getElementById('notificaciones-url').dataset.url;
            const response = await fetch(url);
            const data = await response.json();

            if (data.error) {
                console.error('Error fetching notifications:', data.error);
                return;
            }

            const badge = document.getElementById('notificacionesBadge');
            badge.textContent = data.count;
            badge.classList.toggle('invisible', data.count === 0);
            const acordeon = document.getElementById('notificacionesAcordeon');
            acordeon.innerHTML = '';

            data.notifications.forEach((noti, index) => {
                const itemId = `noti-${index}`;
                const fecha = new Date(noti.timestamp).toLocaleString();
                let mensaje = `${noti.worker} registró ${noti.tipo} a las ${fecha}`;
                let nombreUbicacion = noti.ubicacion_nombre ? ` desde ${noti.ubicacion_nombre}` : (noti.ip_address ? ` desde IP ${noti.ip_address}` : '');
                mensaje += nombreUbicacion;

                // Botón para asignar o cambiar nombre
                const ubicacionBtn = noti.ubicacion_nombre ? `
                    <button class="btn btn-sm btn-outline-secondary mt-2 cambiar-nombre-btn" 
                            data-vigencia-plan-id="${vigenciaPlanId}" 
                            data-ip-address="${noti.ip_address}">
                        Cambiar nombre de ubicación
                    </button>` : `
                    <button class="btn btn-sm btn-outline-primary mt-2 asignar-nombre-btn" 
                            data-vigencia-plan-id="${vigenciaPlanId}" 
                            data-ip-address="${noti.ip_address}">
                        Asignar nombre a ubicación
                    </button>`;

                const itemHTML = `
                    <div class="notificacion-item">
                        <div class="accordion-item">
                            <h2 class="accordion-header">
                                <button class="accordion-button collapsed" type="button" 
                                        data-bs-toggle="collapse" data-bs-target="#${itemId}">
                                    <i class="bi bi-clock notificacion-icon"></i>
                                    <div class="d-flex flex-column">
                                        <span class="small text-muted">${fecha}</span>
                                        <div class="text-truncate" style="max-width: 250px;">
                                            ${noti.worker} - ${noti.tipo}
                                        </div>
                                    </div>
                                </button>
                            </h2>
                            <div id="${itemId}" class="accordion-collapse collapse" 
                                 data-bs-parent="#notificacionesAcordeon">
                                <div class="accordion-body notificacion-body">
                                    <p>${mensaje}</p>
                                    ${ubicacionBtn}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                acordeon.insertAdjacentHTML('beforeend', itemHTML);
            });
        } catch (error) {
            console.error('Error actualizando notificaciones:', error);
        }
    }

    // Función para asignar o cambiar nombre
    function asignarNombre(vigenciaPlanId, ipAddress, isCambiar = false) {
        const promptMessage = isCambiar ? 'Ingrese el nuevo nombre para esta ubicación:' : 'Ingrese el nombre para esta ubicación:';
        const nombre = prompt(promptMessage);
        if (nombre) {
            fetch(`/set_ubicacion_nombre/${vigenciaPlanId}/${ipAddress}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `nombre=${encodeURIComponent(nombre)}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(isCambiar ? 'Nombre cambiado correctamente' : 'Nombre asignado correctamente');
                    actualizarNotificaciones();
                } else {
                    alert('Error al asignar nombre: ' + (data.error || 'Desconocido'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al asignar nombre');
            });
        }
    }

    // Delegación de eventos para asignar y cambiar nombre
    document.getElementById('notificacionesAcordeon').addEventListener('click', function(event) {
        if (event.target.classList.contains('asignar-nombre-btn')) {
            const vigenciaPlanId = event.target.getAttribute('data-vigencia-plan-id');
            const ipAddress = event.target.getAttribute('data-ip-address');
            asignarNombre(vigenciaPlanId, ipAddress);
        } else if (event.target.classList.contains('cambiar-nombre-btn')) {
            const vigenciaPlanId = event.target.getAttribute('data-vigencia-plan-id');
            const ipAddress = event.target.getAttribute('data-ip-address');
            asignarNombre(vigenciaPlanId, ipAddress, true);
        }
    });

    // Actualizar notificaciones al cargar y cada 30 segundos
    setInterval(actualizarNotificaciones, 30000);
    actualizarNotificaciones();

    // Función para obtener el CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
// Manejo de botones "Siguiente" y "Anterior" para cambiar de pestaña en el modal
$('#usuarioModal').on('shown.bs.modal', function() {
    const nextButtons = document.querySelectorAll('#usuarioModal .next-btn');
    nextButtons.forEach(button => {
        button.addEventListener('click', function() {
            const currentSectionId = this.getAttribute('data-current');
            const nextSectionId = this.getAttribute('data-next');
            let valid = true;

            const currentSection = document.getElementById(currentSectionId);
            const inputs = currentSection.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                if (!input.checkValidity()) {
                    valid = false;
                    input.classList.add('is-invalid');
                } else {
                    input.classList.remove('is-invalid');
                }
            });

            if (valid) {
                const nextTabButton = document.querySelector(`#usuarioModal [data-bs-target="#${nextSectionId}"]`);
                if (nextTabButton) {
                    const tab = new bootstrap.Tab(nextTabButton);
                    tab.show();
                }
            } else {
                currentSection.classList.add('was-validated');
            }
        });
    });
});
});
async function actualizarNotificaciones() {
    try {
        const response = await fetch(`{% url 'notificaciones_supervisor_json' vigencia_plan.id %}`);
        const data = await response.json();

        if (data.error) {
            console.error('Error fetching notifications:', data.error);
            return;
        }

        const badge = document.getElementById('notificacionesBadge');
        badge.textContent = data.count;
        badge.classList.toggle('invisible', data.count === 0);

        const acordeon = document.getElementById('notificacionesAcordeon');
        acordeon.innerHTML = '';

        data.notifications.forEach((noti, index) => {
            const itemId = `noti-${index}`;
            const fecha = new Date(noti.timestamp).toLocaleString();
            let mensaje = `${noti.worker} registró ${noti.tipo} a las ${fecha}`;
            let ubicacionInfo = noti.ubicacion_nombre ? ` desde ${noti.ubicacion_nombre}` : (noti.ip_address ? ` desde IP ${noti.ip_address}` : '');
            if (noti.latitud && noti.longitud) {
                ubicacionInfo += ` (Lat: ${noti.latitud}, Lon: ${noti.longitud})`;
            }
            mensaje += ubicacionInfo;

            const ubicacionBtn = noti.ubicacion_nombre ? `
                <button class="btn btn-sm btn-outline-secondary mt-2 cambiar-nombre-btn" 
                        data-vigencia-plan-id="${vigenciaPlanId}" 
                        data-ip-address="${noti.ip_address}">
                    Cambiar nombre de ubicación
                </button>` : `
                <button class="btn btn-sm btn-outline-primary mt-2 asignar-nombre-btn" 
                        data-vigencia-plan-id="${vigenciaPlanId}" 
                        data-ip-address="${noti.ip_address}">
                    Asignar nombre a ubicación
                </button>`;

            const itemHTML = `
                <div class="notificacion-item">
                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button collapsed" type="button" 
                                    data-bs-toggle="collapse" data-bs-target="#${itemId}">
                                <i class="bi bi-clock notificacion-icon"></i>
                                <div class="d-flex flex-column">
                                    <span class="small text-muted">${fecha}</span>
                                    <div class="text-truncate" style="max-width: 250px;">
                                        ${noti.worker} - ${noti.tipo}
                                    </div>
                                </div>
                            </button>
                        </h2>
                        <div id="${itemId}" class="accordion-collapse collapse" 
                             data-bs-parent="#notificacionesAcordeon">
                            <div class="accordion-body notificacion-body">
                                <p>${mensaje}</p>
                                ${ubicacionBtn}
                            </div>
                        </div>
                    </div>
                </div>
            `;
            acordeon.insertAdjacentHTML('beforeend', itemHTML);
        });
    } catch (error) {
        console.error('Error actualizando notificaciones:', error);
 
    }




}

document.addEventListener('DOMContentLoaded', function() {
    const sendCodeButtons = document.querySelectorAll('.send-code-btn');
    if (sendCodeButtons.length > 0) {
        console.log('Botones "Enviar Código" encontrados:', sendCodeButtons.length);
        sendCodeButtons.forEach(button => {
            button.addEventListener('click', function(event) {
                event.preventDefault();
                const notiId = button.getAttribute('data-noti-id');
                console.log('Botón "Enviar Código" clicado, ID:', notiId);
                const url = `/ModuloAsistencia/send_access_code/${notiId}/`;
                console.log('Enviando solicitud a:', url);
                console.log('Token CSRF:', getCookie('csrftoken'));
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json',
                    },
                })
                .then(response => {
                    console.log('Respuesta del servidor:', response.status, response.ok);
                    if (!response.ok) throw new Error('Error en la solicitud: ' + response.status);
                    return response.json();
                })
                .then(data => {
                    console.log('Datos recibidos:', data);
                    if (data.success) {
                        const codeDisplay = button.nextElementSibling;
                        codeDisplay.textContent = 'Código enviado con éxito al usuario.';
                        codeDisplay.style.display = 'block';
                        button.remove();
                    } else {
                        alert('Error al enviar código: ' + (data.error || 'Desconocido'));
                    }
                })
                .catch(error => {
                    console.error('Error en fetch:', error);
                    alert('Ocurrió un error al enviar el código');
                });
            });
        });
    } else {
        console.error('No se encontraron botones "Enviar Código"');
    }
});
