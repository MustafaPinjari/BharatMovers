document.addEventListener('DOMContentLoaded', function() {
    // Password visibility toggle
    const toggleButtons = document.querySelectorAll('.toggle-password');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            if (input.type === 'password') {
                input.type = 'text';
                this.classList.remove('fa-eye-slash');
                this.classList.add('fa-eye');
            } else {
                input.type = 'password';
                this.classList.remove('fa-eye');
                this.classList.add('fa-eye-slash');
            }
        });
    });

    // Form validation
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm-password').value;
            const phone = document.getElementById('phone').value;

            // Password validation
            if (password.length < 8) {
                e.preventDefault();
                showError('Password must be at least 8 characters long');
                return;
            }

            if (!/[A-Z]/.test(password)) {
                e.preventDefault();
                showError('Password must contain at least one uppercase letter');
                return;
            }

            if (!/[0-9]/.test(password)) {
                e.preventDefault();
                showError('Password must contain at least one number');
                return;
            }

            if (password !== confirmPassword) {
                e.preventDefault();
                showError('Passwords do not match');
                return;
            }

            // Phone validation
            if (!/^\d{10}$/.test(phone)) {
                e.preventDefault();
                showError('Please enter a valid 10-digit phone number');
                return;
            }
        });
    }

    // Login form validation
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            if (!email || !password) {
                e.preventDefault();
                showError('Please fill in all fields');
                return;
            }

            // Email validation
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                e.preventDefault();
                showError('Please enter a valid email address');
                return;
            }
        });
    }

    // Error message display
    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show';
        errorDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        const form = document.querySelector('.auth-form');
        form.insertBefore(errorDiv, form.firstChild);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(errorDiv);
            bsAlert.close();
        }, 5000);
    }
});