
function togglePasswordVisibility() {
    const passwordInput = document.getElementById("inputPassword");
    const icon = document.getElementById("togglePasswordIcon");
    
    if (passwordInput.type === "password") {
    passwordInput.type = "text";
    icon.classList.remove("fa-eye-slash");
    icon.classList.add("fa-eye");
    } else {
    passwordInput.type = "password";
    icon.classList.remove("fa-eye");
    icon.classList.add("fa-eye-slash");
    }
}
