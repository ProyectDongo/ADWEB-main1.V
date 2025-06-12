
document.addEventListener('DOMContentLoaded', function() {
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');
    
    togglePassword.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        this.innerHTML = type === 'password' ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
    });
    
    // Mejora: Cambiar el color del icono al alternar
    togglePassword.addEventListener('click', function() {
        const eyeIcon = this.querySelector('i');
        if (passwordInput.getAttribute('type') === 'password') {
            eyeIcon.style.color = '';
        } else {
            eyeIcon.style.color = '#6366f1';
        }
    });
    
    // Efecto de enfoque mejorado para los campos
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(control => {
        control.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        control.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
});
