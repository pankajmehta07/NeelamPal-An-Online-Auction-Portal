
function togglePasswordVisibility(inputId, iconId) {
    const passwordInput = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    
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

function handleFocus(element,divID){
    console.log(divID);
    const passDiv = document.getElementById(divID);
    passDiv.classList.add('highlight-border');
}
function handleBlur(element,divID){
    console.log(divID);
    const passDiv = document.getElementById(divID);
    passDiv.classList.remove('highlight-border');
}


function switchType(type) {
    if (type === 'bidder') {        
      document.getElementById('usernameInputLabel').innerText = "Citizenship No";
      document.getElementById('userType').value = "Bidder";
      document.getElementById('usernameInput').placeholder = "Enter citizenship number (username)";
      document.getElementById('nameInput').placeholder = "Enter full name";
      document.getElementById('usernameInput').value = "";
      document.getElementById('nameInput').value = "";
      document.getElementById('contactInput').value = "";
      document.getElementById('addressInput').value = "";
      document.getElementById('registerPassword').value = "";
    } else {
        document.getElementById('usernameInputLabel').innerText = "Registration No";
      document.getElementById('userType').value = "Organization";
      document.getElementById('usernameInput').value = "";
      document.getElementById('nameInput').value = "";
      document.getElementById('contactInput').value = "";
      document.getElementById('addressInput').value = "";
      document.getElementById('registerPassword').value = "";
        document.getElementById('usernameInput').placeholder = "Enter registration number (username)";
        document.getElementById('nameInput').placeholder = "Enter oraganization name";
    }
  }
