const API = "/api/client";
const token = localStorage.getItem("token");

if (!token) {
  window.location.href = "login.html";
}

function headers() {
  return {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + token
  };
}

/* ================= ME ================= */

async function loadMe() {
  try {
    const res = await fetch(`${API}/me`, { headers: headers() });
    if (!res.ok) return;

    const me = await res.json();
    document.getElementById("cliente-logado").innerText = me.nome;
  } catch (e) {
    console.error("Erro ao carregar cliente logado", e);
  }
}

/* ================= EMAILS ================= */

async function loadEmails() {
  const res = await fetch(`${API}/emails`, { headers: headers() });
  const emails = await res.json();

  let html = `
    <h3>Emails cadastrados</h3>
    <input id="novoEmail" placeholder="novo@email.com">
    <button onclick="addEmail()">Adicionar</button>
  `;

  emails.forEach(e => {
    html += `
      <div class="email-row">
        <div class="email-info">
          <span class="email">${e.email}</span>
          <span class="status">${e.ativo ? "Ativo" : "Inativo"}</span>
        </div>

        <div class="actions">
          <button onclick="toggleEmail(${e.id}, ${!e.ativo})">
            ${e.ativo ? "Desativar" : "Ativar"}
          </button>
          <button onclick="removeEmail(${e.id})">Remover</button>
        </div>
      </div>
    `;
  });

  document.getElementById("content").innerHTML = html;
}

async function addEmail() {
  const email = document.getElementById("novoEmail").value;
  await fetch(`${API}/emails?email=${encodeURIComponent(email)}`, {
    method: "POST",
    headers: headers()
  });
  loadEmails();
}

async function toggleEmail(id, ativo) {
  await fetch(`${API}/emails/${id}/toggle?ativo=${ativo}`, {
    method: "POST",
    headers: headers()
  });
  loadEmails();
}

async function removeEmail(id) {
  await fetch(`${API}/emails/${id}`, {
    method: "DELETE",
    headers: headers()
  });
  loadEmails();
}

/* ================= KEYWORDS ================= */

async function loadKeywords() {
  const res = await fetch(`${API}/keywords`, { headers: headers() });
  const keywords = await res.json();

  let html = `
    <h3>Keywords</h3>

    <div class="form-row">
      <input id="kwExpressao" placeholder="Ex: una medic ltda">
      <input id="kwInicio" type="time">
      <input id="kwFim" type="time">
      <button onclick="addKeyword()">Adicionar</button>
    </div>

    <small>
      Use expressões completas, exatamente como aparecem no Diário Oficial.
    </small>
  `;

  keywords.forEach(k => {
    html += `
      <div class="email-row">
        <div class="email-info">
          <div>
            <strong>${k.expressao}</strong><br>
            <span class="status">
              Horário: ${k.hora_inicio || "--"} - ${k.hora_fim || "--"}
            </span>
          </div>
        </div>

        <div class="actions">
          <button onclick="removeKeyword(${k.id})">Remover</button>
        </div>
      </div>
    `;
  });

  document.getElementById("content").innerHTML = html;
}

async function addKeyword() {
  const expressao = document.getElementById("kwExpressao").value.trim();
  const hora_inicio = document.getElementById("kwInicio").value;
  const hora_fim = document.getElementById("kwFim").value;

  if (!expressao) {
    alert("Informe a expressão");
    return;
  }

  await fetch(`${API}/keywords`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({
      expressao,
      operador: "OR", // valor fixo, legado
      hora_inicio,
      hora_fim
    })
  });

  loadKeywords();
}

async function removeKeyword(id) {
  await fetch(`${API}/keywords/${id}`, {
    method: "DELETE",
    headers: headers()
  });
  loadKeywords();
}

/* ================= ALERTAS ================= */

async function loadAlerts() {
  const res = await fetch(`${API}/alerts`, { headers: headers() });
  const alerts = await res.json();

  let html = `<h3>Alertas recentes</h3>`;

  if (!alerts.length) {
    html += `<div class="placeholder">Nenhum alerta encontrado</div>`;
    document.getElementById("content").innerHTML = html;
    return;
  }

  alerts.forEach(a => {
    const data = a.created_at
      ? new Date(a.created_at).toLocaleString("pt-BR")
      : "--";

    html += `
      <div class="alert-card">
        <div class="alert-termos">${a.termos}</div>
        <div class="alert-data">${data}</div>

        <div class="alert-trecho">
          ${a.linha}
        </div>

        <a class="alert-link" href="${a.url}" target="_blank">
          Ver ato oficial
        </a>

        <button class="btn-pdf" onclick="abrirPdf(${a.id})">
          Abrir PDF destacado
        </button>
      </div>
    `;
  });

  document.getElementById("content").innerHTML = html;
}

/* ================= MENU ================= */

function selectTab(button) {
  document.querySelectorAll(".menu button").forEach(b =>
    b.classList.remove("active")
  );
  button.classList.add("active");

  const tab = button.dataset.tab;
  document.getElementById("content").innerHTML = "";

  if (tab === "emails") loadEmails();
  if (tab === "keywords") loadKeywords();
  if (tab === "alertas") loadAlerts();
}

/* ================= PDF ================= */

async function abrirPdf(alertId) {
  const res = await fetch(`${API}/alerts/${alertId}/pdf`, {
    headers: headers()
  });

  if (!res.ok) {
    alert("Erro ao abrir PDF");
    return;
  }

  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  window.open(url, "_blank");
}

/* ================= INIT ================= */

document.addEventListener("DOMContentLoaded", () => {
  loadMe();
});

