async function login() {
  const email = document.getElementById("email").value;
  const senha = document.getElementById("senha").value;

  if (!email || !senha) {
    alert("Informe email e senha");
    return;
  }

  const res = await fetch("/api/client/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ email, senha })
  });

  if (!res.ok) {
    alert("Email ou senha inválidos");
    return;
  }

  const data = await res.json();
  localStorage.setItem("token", data.access_token);

  window.location.href = "/client/dashboard.html";
}

