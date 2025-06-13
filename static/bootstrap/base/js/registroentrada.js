document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const geoSection = document.getElementById('geoSection');
    const geoStatus = document.getElementById('geoStatus');
    const submitBtn = document.querySelector('#entradaForm button[type="submit"]');
    let geoReady = false;

    // Función para habilitar/deshabilitar el botón de envío
    function toggleSubmitButton() {
        if (document.querySelector('input[name="metodo"]:checked').value === 'geo') {
            submitBtn.disabled = !geoReady;
        } else {
            submitBtn.disabled = false;
        }
    }

    // Estado inicial del botón
    if (!submitBtn.hasAttribute('disabled')) {
        toggleSubmitButton();
    }

    // Manejo de cambio en los métodos de registro
    document.querySelectorAll('input[name="metodo"]').forEach(radio => {
        radio.addEventListener('change', function() {
            geoReady = false;
            toggleSubmitButton();
            if (this.value === 'geo') {
                geoSection.classList.remove('d-none');
                geoStatus.innerHTML = `
                    <div class="alert alert-info d-flex align-items-center">
                        <div class="spinner-border text-primary me-3" role="status">
                            <span class="visually-hidden">Cargando...</span>
                        </div>
                        <div>
                            <h5 class="alert-heading">Obteniendo ubicación</h5>
                            <p class="mb-0">Por favor espera...</p>
                        </div>
                    </div>
                `;
                navigator.geolocation.getCurrentPosition(position => {
                    const lat = Number(position.coords.latitude.toFixed(6));
                    const lon = Number(position.coords.longitude.toFixed(6));
                    const accuracy = position.coords.accuracy; // Obtener la precisión
                    document.getElementById('latitudInput').value = lat;
                    document.getElementById('longitudInput').value = lon;
                    document.getElementById('precisionInput').value = accuracy; // Asignar la precisión
                    geoStatus.innerHTML = `
                        <div class="alert alert-success d-flex align-items-center">
                            <i class="fas fa-map-marker-alt fa-3x me-3"></i>
                            <div>
                                <h5 class="alert-heading">Ubicación obtenida</h5>
                                <small class="text-muted">
                                    Lat: ${lat}<br>
                                    Lon: ${lon}
                                    Precisión: ${accuracy} metros
                                </small>
                            </div>
                        </div>
                    `;
                    geoReady = true;
                    toggleSubmitButton();
                }, error => {
                    let errorMessage;
                    switch(error.code) {
                        case error.PERMISSION_DENIED:
                            errorMessage = "Permiso denegado para acceder a la ubicación.";
                            break;
                        case error.POSITION_UNAVAILABLE:
                            errorMessage = "La posición no está disponible.";
                            break;
                        case error.TIMEOUT:
                            errorMessage = "Tiempo de espera agotado.";
                            break;
                        default:
                            errorMessage = "Error desconocido.";
                            break;
                    }
                    geoStatus.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            ${errorMessage}
                        </div>
                    `;
                    submitBtn.disabled = true;
                });
            } else {
                geoSection.classList.add('d-none');
                geoStatus.innerHTML = '';
                toggleSubmitButton();
            }
        });
    });

    // Configuración inicial de la firma digital
    const canvas = document.getElementById('firmaCanvas');
    const ctx = canvas.getContext('2d');
    let dibujando = false;
    let lastX = 0;
    let lastY = 0;

    // Eventos de dibujo
    canvas.addEventListener('mousedown', iniciarDibujo);
    canvas.addEventListener('mousemove', dibujar);
    canvas.addEventListener('mouseup', terminarDibujo);
    canvas.addEventListener('mouseout', terminarDibujo);
    canvas.addEventListener('touchstart', iniciarDibujo);
    canvas.addEventListener('touchmove', dibujar);
    canvas.addEventListener('touchend', terminarDibujo);

    // Manejo de envío del formulario de salida
    document.getElementById('salidaForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const btn = this.querySelector('button');
        const originalHTML = btn.innerHTML;
        
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Obteniendo ubicación...';
        
        navigator.geolocation.getCurrentPosition(position => {
            const lat = Number(position.coords.latitude.toFixed(6));
            const lon = Number(position.coords.longitude.toFixed(6));
            document.getElementById('latitudSalidaInput').value = lat;
            document.getElementById('longitudSalidaInput').value = lon;
            
            btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Procesando...';
            
            fetch(this.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Accept': 'application/json'
                },
                body: new FormData(this)
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    return response.json().then(data => {
                        if (data.error) throw new Error(data.error);
                        window.location.reload();
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                btn.disabled = false;
                btn.innerHTML = originalHTML;
                alert(error.message);
            });
        }, error => {
            let errorMessage;
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    errorMessage = "Permiso denegado para acceder a la ubicación.";
                    break;
                case error.POSITION_UNAVAILABLE:
                    errorMessage = "La posición no está disponible.";
                    break;
                case error.TIMEOUT:
                    errorMessage = "Tiempo de espera agotado.";
                    break;
                default:
                    errorMessage = "Error desconocido.";
                    break;
            }
            btn.disabled = false;
            btn.innerHTML = originalHTML;
            alert(errorMessage);
        });
    });

    // Funciones de dibujo
    function getEventPosition(e) {
        const rect = canvas.getBoundingClientRect();
        return e.touches ? {
            x: e.touches[0].clientX - rect.left,
            y: e.touches[0].clientY - rect.top
        } : {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }

    function iniciarDibujo(e) {
        dibujando = true;
        const pos = getEventPosition(e);
        [lastX, lastY] = [pos.x, pos.y];
        ctx.beginPath();
    }

    function dibujar(e) {
        if (!dibujando) return;
        e.preventDefault();
        const pos = getEventPosition(e);
        ctx.lineWidth = 2;
        ctx.lineCap = 'round';
        ctx.strokeStyle = '#000';
        ctx.lineTo(pos.x, pos.y);
        ctx.stroke();
        [lastX, lastY] = [pos.x, pos.y];
        document.getElementById('firmaInput').value = canvas.toDataURL();
    }

    function terminarDibujo() {
        dibujando = false;
    }

    function limpiarFirma() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        document.getElementById('firmaInput').value = '';
    }

    // Función para obtener el token CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});