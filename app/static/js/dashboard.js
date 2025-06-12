function showFeedback(message, type = "success") {
  const feedback = document.getElementById("feedback-message");
  feedback.textContent = message;
  feedback.className = "feedback-message feedback-" + type;
  feedback.style.display = "block";
  feedback.style.opacity = "1";
  setTimeout(() => {
    feedback.style.opacity = "0";
    setTimeout(() => {
      feedback.style.display = "none";
    }, 400);
  }, 4000);
}

async function loadUserData() {
  try {
    const response = await fetch("/user/information", {
      credentials: "include",
    });
    if (!response.ok) {
      let msg = "Erro ao carregar dados do usuário";
      try {
        const err = await response.json();
        msg = err.detail || msg;
      } catch {}
      throw new Error(msg);
    }
    const data = await response.json();
    document.getElementById("user-name").textContent = data.name;
    document.getElementById("account-number").textContent = data.account_number;
    document.getElementById("user-type").textContent = data.user_type;
    document.getElementById("account-balance").textContent =
      data.balance.toLocaleString("pt-BR", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      });

    if (data.user_type && data.user_type.toLowerCase() === "vip") {
      document.getElementById("manager-visit-btn").style.display =
        "inline-block";
    } else {
      document.getElementById("manager-visit-btn").style.display = "none";
    }

    const statementBody = document.getElementById("statement-body");
    statementBody.innerHTML = "";
    data.statement.forEach((transaction) => {
      const row = document.createElement("tr");
      const dateCell = document.createElement("td");
      const date = new Date(transaction.timestamp);
      dateCell.textContent = date.toLocaleString("pt-BR");
      row.appendChild(dateCell);
      const descCell = document.createElement("td");
      descCell.textContent = transaction.description;
      row.appendChild(descCell);
      const valueCell = document.createElement("td");
      const valueDiv = document.createElement("div");
      valueDiv.className = "transaction-value";
      const transactionClass = `transaction-${transaction.type_transaction}`;
      valueDiv.classList.add(transactionClass);
      const valueSpan = document.createElement("span");
      const formattedValue = transaction.value.toLocaleString("pt-BR", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      });
      valueSpan.textContent = formattedValue;
      valueSpan.style.color = transaction.value >= 0 ? "green" : "red";
      valueDiv.innerHTML = "";
      valueDiv.appendChild(valueSpan);
      valueCell.appendChild(valueDiv);
      row.appendChild(valueCell);
      statementBody.appendChild(row);
    });
  } catch (error) {
    showFeedback(
      error.message ||
        "Erro ao carregar dados. Por favor, recarregue a página.",
      "error"
    );
  }
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add("show");
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove("show");
  }
}

async function submitForm(event, action) {
  event.preventDefault();
  let url, body;
  try {
    switch (action) {
      case "deposit":
        const depositAmount = parseFloat(
          document.getElementById("deposit-amount").value
        );
        if (isNaN(depositAmount) || depositAmount <= 0) {
          showFeedback(
            "Por favor, insira um valor válido para depósito",
            "error"
          );
          return;
        }
        url = "/user/deposit";
        body = JSON.stringify({ amount: depositAmount, type: "deposit" });
        break;
      case "withdrawal":
        const withdrawAmount = parseFloat(
          document.getElementById("withdraw-amount").value
        );
        if (isNaN(withdrawAmount) || withdrawAmount <= 0) {
          showFeedback("Por favor, insira um valor válido para saque", "error");
          return;
        }
        url = "/user/withdrawal";
        body = JSON.stringify({ amount: withdrawAmount, type: "withdrawal" });
        break;
      case "transfer":
        const transferAccount =
          document.getElementById("transfer-account").value;
        const transferAmount = parseFloat(
          document.getElementById("transfer-amount").value
        );
        if (!/^\d{5}$/.test(transferAccount)) {
          showFeedback(
            "O número da conta destino deve conter exatamente 5 dígitos.",
            "error"
          );
          return;
        }
        if (isNaN(transferAmount) || transferAmount <= 0) {
          showFeedback(
            "Por favor, insira um valor válido para transferência",
            "error"
          );
          return;
        }
        url = "/user/transfer";
        body = JSON.stringify({
          target_account_number: transferAccount,
          amount: transferAmount,
          type: "transfer",
        });
        break;
    }
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: body,
      credentials: "include",
    });
    let result;
    try {
      result = await response.json();
    } catch {
      result = {};
    }
    if (
      !response.ok ||
      result.status_code === 422 ||
      result.status_code === 403
    ) {
      let msg = result.detail || "Erro na operação";
      showFeedback(msg, "error");
      return;
    }
    showFeedback("Operação realizada com sucesso!", "success");
    closeModal(`${action}-modal`);
    event.target.reset();
    await loadUserData();
  } catch (error) {
    showFeedback(error.message || "Erro inesperado.", "error");
  }
}

async function requestManagerVisit() {
  try {
    const response = await fetch("/user/manager_visit", {
      method: "POST",
      credentials: "include",
    });
    let result;
    try {
      result = await response.json();
    } catch {
      result = {};
    }
    if (
      !response.ok ||
      result.status_code === 422 ||
      result.status_code === 403
    ) {
      let msg = result.detail || "Erro ao solicitar visita do gerente";
      showFeedback(msg, "error");
      closeModal("manager-visit-modal");
      return;
    }
    showFeedback(
      "Visita do gerente solicitada com sucesso! R$50,00 debitados.",
      "success"
    );
    closeModal("manager-visit-modal");
    await loadUserData();
  } catch (error) {
    showFeedback(error.message || "Erro inesperado.", "error");
    closeModal("manager-visit-modal");
  }
}

window.onclick = function (event) {
  if (
    event.target &&
    event.target.classList &&
    event.target.classList.contains("modal")
  ) {
    event.target.classList.remove("show");
  }
};
document.addEventListener("DOMContentLoaded", loadUserData);
