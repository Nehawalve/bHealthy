console.log("Script loaded successfully");


document.addEventListener("DOMContentLoaded", function() {
  console.log("DOM fully loaded, initializing toggle password functionality.");
  // Form validation (if needed)
  const forms = document.querySelectorAll('.needs-validation');
  forms.forEach(function(form) {
    form.addEventListener('submit', function(event) {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add('was-validated');
    }, false);
  });

  // Toggle password visibility functionality
  const togglePasswordButtons = document.querySelectorAll('.toggle-password');
  console.log("Found", togglePasswordButtons.length, "toggle password buttons.");
  
  togglePasswordButtons.forEach(function(button) {
    button.addEventListener('click', function() {
      console.log("Toggle button clicked.");
      // Find the closest parent container with class "position-relative"
      const container = button.closest('.position-relative');
      console.log("Container:", container);
      if (!container) return;
      // Find the input within that container
      const input = container.querySelector('input');
      console.log("Password input found:", input);
      if (!input) return;
      if (input.type === "password") {
        input.type = "text";
        button.innerHTML = '<i class="bi bi-eye-slash"></i>';
      } else {
        input.type = "password";
        button.innerHTML = '<i class="bi bi-eye"></i>';
      }
    });
  });
});
