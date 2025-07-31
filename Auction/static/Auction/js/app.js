
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
    const passDiv = document.getElementById(divID);
    passDiv.classList.add('highlight-border');
}
function handleBlur(element,divID){
    const passDiv = document.getElementById(divID);
    passDiv.classList.remove('highlight-border');
}


function switchRegisterType(type) {
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
function switchLoginType(type) {
  if (type === 'bidder') {        
    document.getElementById('LoginUserType').value = "Bidder";
    document.getElementById('LoginUsername').placeholder = "Citizenship Number";
  } else {
    document.getElementById('LoginUserType').value = "Organization";
    document.getElementById('LoginUsername').placeholder = "Registration Number";
  }
  document.getElementById('LoginPassword').value = "";
  document.getElementById('LoginUsername').value = "";
}
function updateEndTimeMin(startID, endID, minGap) {
    const value = new Date(document.getElementById(startID).value); 
    value.setMinutes(value.getMinutes() + minGap);
    value.setMinutes(value.getMinutes() - value.getTimezoneOffset());
    document.getElementById(endID).min = value.toISOString().slice(0,16);
    if (document.getElementById(endID).value && new Date(document.getElementById(endID).value) < new Date(document.getElementById(endID).min)) {
      document.getElementById(endID).value = '';
    }
}

document.addEventListener('DOMContentLoaded', function () {
  const alerts = document.querySelectorAll('.alert-dismissible');

  alerts.forEach(function(alert) {
    setTimeout(function () {
      const alertInstance = bootstrap.Alert.getOrCreateInstance(alert);
      alertInstance.close();
    }, 1500);
  });
});