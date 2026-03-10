async function loginAdmin() {
  const email = document.getElementById("email").value.trim();
  const senha = document.getElementById("senha").value.trim();

  if (!email || !senha) {
    alert("Informe email e senha");
    return;
  }

  try {
    const res = await fetch("/admin-auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      credentials: "include",
      body: JSON.stringify({
        email: email,
        senha: senha
      })
    });

    if (!res.ok) {
      alert("Credenciais inválidas");
      return;
    }

    window.location.href = "/admin-ui/";
  } catch (err) {
    alert("Erro ao conectar com o servidor");
  }
}
