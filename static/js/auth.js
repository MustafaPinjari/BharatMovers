// Toggle password visibility
document.addEventListener('DOMContentLoaded', function() {
    const toggleButtons = document.querySelectorAll('.toggle-password');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const type = input.getAttribute('type');
            
            if (type === 'password') {
                input.setAttribute('type', 'text');
                this.classList.remove('fa-eye-slash');
                this.classList.add('fa-eye');
            } else {
                input.setAttribute('type', 'password');
                this.classList.remove('fa-eye');
                this.classList.add('fa-eye-slash');
            }
        });
    });

    // Add animation classes to form groups
    const formGroups = document.querySelectorAll('.form-group');
    formGroups.forEach((group, index) => {
        group.classList.add('animate__animated', 'animate__fadeInUp');
        group.style.animationDelay = `${index * 0.1}s`;
    });

    // Add loading animation to form submission
    const forms = document.querySelectorAll('.auth-form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const button = this.querySelector('.auth-btn');
            const originalText = button.textContent;
            
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            button.disabled = true;
            
            // Simulate form submission (replace with actual form submission)
            setTimeout(() => {
                button.innerHTML = '<i class="fas fa-check"></i> Success!';
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.disabled = false;
                }, 1500);
            }, 2000);
        });
    });
});