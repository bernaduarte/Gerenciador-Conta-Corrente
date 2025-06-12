const form = document.getElementById("loginForm");
const accountInput = document.getElementById("account_number");
const passwordInput = document.getElementById("password");
const submitBtn = document.getElementById("submitBtn");
const responseMessage = document.getElementById("responseMessage");

const accountError = document.getElementById("accountError");
const passwordError = document.getElementById("passwordError");

accountInput.addEventListener("input", validateAccount);
passwordInput.addEventListener("input", validatePassword);

function validateAccount() {
  const accountValue = accountInput.value.trim();
  if (!/^\d{5}$/.test(accountValue)) {
    accountError.style.display = "block";
    return false;
  } else {
    accountError.style.display = "none";
    return true;
  }
}

function validatePassword() {
  const passwordValue = passwordInput.value;
  if (passwordValue.length !== 4) {
    passwordError.style.display = "block";
    return false;
  } else {
    passwordError.style.display = "none";
    return true;
  }
}

form.addEventListener("submit", async function (event) {
  event.preventDefault();

  const isAccountValid = validateAccount();
  const isPasswordValid = validatePassword();

  if (!isAccountValid || !isPasswordValid) {
    return;
  }

  const account_number = accountInput.value.trim();
  const password = passwordInput.value;

  submitBtn.disabled = true;
  submitBtn.innerHTML = '<div class="loading"></div> Processando...';
  responseMessage.textContent = "";
  responseMessage.className = "";

  try {
    const response = await fetch("/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ account_number, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Erro no login");
    }
    responseMessage.textContent = data.message || "Login bem-sucedido!";
    responseMessage.className = "success-message";

    window.location.href = "/dashboard";
  } catch (error) {
    responseMessage.textContent = error.message || "Erro ao tentar fazer login";
    responseMessage.className = "error-message";
    responseMessage.style.display = "block";
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Entrar";
  }
});
