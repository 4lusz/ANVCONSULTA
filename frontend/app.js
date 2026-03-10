const API = "/admin";
let CLIENTE_ATUAL = null;
let KEYWORD_EDITANDO = null;

function authFetch(url, options = {}) {
  return fetch(url, {
    ...options,
    credentials: "include",
    headers: {
      ...(options.headers || {})
    }
  });
}

function formatDate(value) {
  if (!value) return "--";
  try {
    return new Date(value).toLocaleString("pt-BR");
  } catch {
    return value;
  }
}

function setText(id, text, className = null) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerText = text;
  if (className) el.className = className;
}

async function checkAuth() {
  const res = await fetch("/admin/me", {
    credentials: "include"
  });

  if (!res.ok) {
    window.location.href = "/admin-ui/login.html";
  }
}

/* ================= STATUS ================= */

async function loadStatus() {
  const res = await authFetch(`${API}/status`);
  const s = await res.json();

  setText("status-running", s.running ? "ATIVO" : "PARADO");
  setText("status-cycle", formatDate(s.last_cycle_start));
  setText("status-success", formatDate(s.last_success));
  setText("status-retry", s.retry_count ?? 0);

  const errorEl = document.getElementById("status-error");
  if (s.last_error) {
    errorEl.innerText = s.last_error;
    errorEl.className = "error";
  } else {
    errorEl.innerText = "Nenhum";
    errorEl.className = "placeholder";
  }
}

async function loadLoopInterval() {
  const res = await authFetch(`${API}/status`);
  const s = await res.json();
  const minutos = Math.round((s.loop_interval ?? 900) / 60);
  setText("loop-atual", minutos);
}

/* ================= MONITOR ================= */

async function start() {
  await authFetch(`${API}/start`);
  setTimeout(loadStatus, 500);
}

async function stop() {
  await authFetch(`${API}/stop`);
  setTimeout(loadStatus, 500);
}

/* ================= CLIENTES ================= */

async function loadClientes() {
  const res = await authFetch(`${API}/clientes`);
  const clientes = await res.json();

  const list = document.getElementById("cliente-list");
  list.innerHTML = "";

  clientes.forEach(c => {
    const li = document.createElement("li");
    li.className = "cliente-item" + (c.id === CLIENTE_ATUAL ? " selecionado" : "");

    li.innerHTML = `
      <div>
        <div class="cliente-nome ${c.ativo ? "" : "cliente-inativo"}">${c.nome}</div>
        <div class="placeholder">${c.email || ""}</div>
      </div>
      <div>
        <button onclick="selectCliente(${c.id}, '${c.nome}')">Selecionar</button>
        <button onclick="toggleCliente(${c.id}, ${!c.ativo})">
          ${c.ativo ? "Desativar" : "Ativar"}
        </button>
        <button onclick="removeCliente(${c.id})">❌</button>
      </div>
    `;

    list.appendChild(li);
  });
}

async function criarCliente() {
  const nome = document.getElementById("clienteNome").value;
  const email = document.getElementById("clienteEmail").value;
  const senha = document.getElementById("clienteSenha").value;

  const res = await authFetch(`${API}/clientes`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nome, email, senha })
  });

  if (res.ok) {
    loadClientes();
    document.getElementById("clienteNome").value = "";
    document.getElementById("clienteEmail").value = "";
    document.getElementById("clienteSenha").value = "";
  }
}

async function toggleCliente(id, ativo) {
  await authFetch(`${API}/clientes/${id}/toggle?ativo=${ativo}`, { method: "POST" });
  loadClientes();
}

async function removeCliente(id) {
  await authFetch(`${API}/clientes/${id}`, { method: "DELETE" });
  if (CLIENTE_ATUAL === id) clearClienteSelecionado();
  loadClientes();
}

/* ================= CLIENTE SELECIONADO ================= */

function selectCliente(id, nome) {
  CLIENTE_ATUAL = id;
  KEYWORD_EDITANDO = null;

  document.getElementById("cliente-selecionado").innerText = nome;
  document.getElementById("email-input").disabled = false;
  document.getElementById("btn-add-email").disabled = false;
  document.getElementById("email-hint").style.display = "none";
  document.getElementById("btn-keyword").innerText = "Adicionar";

  loadClientes();
  loadEmails();
  loadKeywords();
}

function clearClienteSelecionado() {
  CLIENTE_ATUAL = null;
  KEYWORD_EDITANDO = null;

  document.getElementById("cliente-selecionado").innerText = "Nenhum";
  document.getElementById("email-input").disabled = true;
  document.getElementById("btn-add-email").disabled = true;
  document.getElementById("email-list").innerHTML = "";
  document.getElementById("keyword-list").innerHTML = "";
  document.getElementById("email-hint").style.display = "block";
  document.getElementById("btn-keyword").innerText = "Adicionar";
}

/* ================= EMAILS ================= */

async function loadEmails() {
  if (!CLIENTE_ATUAL) return;

  const res = await authFetch(`${API}/emails?cliente_id=${CLIENTE_ATUAL}`);
  const emails = await res.json();

  const list = document.getElementById("email-list");
  list.innerHTML = "";

  if (!emails.length) {
    list.innerHTML = "<li class='placeholder'>Nenhum email cadastrado</li>";
    return;
  }

  emails.forEach(e => {
    const li = document.createElement("li");
    li.innerHTML = `
      <span>${e.email} ${e.ativo ? "" : "(inativo)"}</span>
      <button onclick="toggleEmail(${e.id}, ${!e.ativo})">
        ${e.ativo ? "Desativar" : "Ativar"}
      </button>
      <button onclick="removeEmail(${e.id})">❌</button>
    `;
    list.appendChild(li);
  });
}

async function addEmail() {
  if (!CLIENTE_ATUAL) return;

  const email = document.getElementById("email-input").value.trim();
  if (!email) return;

  await authFetch(`${API}/emails?cliente_id=${CLIENTE_ATUAL}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email })
  });

  document.getElementById("email-input").value = "";
  loadEmails();
}

async function toggleEmail(id, ativo) {
  await authFetch(`${API}/emails/${id}/toggle?ativo=${ativo}`, { method: "POST" });
  loadEmails();
}

async function removeEmail(id) {
  await authFetch(`${API}/emails/${id}`, { method: "DELETE" });
  loadEmails();
}

/* ================= KEYWORDS ================= */

async function loadKeywords() {
  if (!CLIENTE_ATUAL) return;

  const res = await authFetch(`${API}/keywords?cliente_id=${CLIENTE_ATUAL}`);
  const keywords = await res.json();

  const list = document.getElementById("keyword-list");
  list.innerHTML = "";

  if (!keywords.length) {
    list.innerHTML = "<li class='placeholder'>Nenhuma keyword cadastrada</li>";
    return;
  }

  keywords.forEach(k => {
    const li = document.createElement("li");
    li.className = "keyword-item";

    li.innerHTML = `
      <span class="keyword-text">
        ${k.expressao} (${k.operador}) ${k.hora_inicio} - ${k.hora_fim}
        ${k.ativo ? "" : "(inativo)"}
      </span>
      <div>
        <button onclick="toggleKeyword(${k.id}, ${!k.ativo})">
          ${k.ativo ? "Desativar" : "Ativar"}
        </button>
        <button onclick="removeKeyword(${k.id})">❌</button>
      </div>
    `;
    list.appendChild(li);
  });
}

async function salvarKeyword() {
  if (!CLIENTE_ATUAL) return;

  const expressao = document.getElementById("kw-expressao").value.trim();
  const operador = document.getElementById("kw-operador").value;
  const hora_inicio = document.getElementById("kw-hora-inicio").value;
  const hora_fim = document.getElementById("kw-hora-fim").value;

  if (!expressao) return;

  await authFetch(`${API}/keywords?cliente_id=${CLIENTE_ATUAL}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ expressao, operador, hora_inicio, hora_fim })
  });

  document.getElementById("kw-expressao").value = "";
  loadKeywords();
}

async function toggleKeyword(id, ativo) {
  await authFetch(`${API}/keywords/${id}/toggle?ativo=${ativo}`, { method: "POST" });
  loadKeywords();
}

async function removeKeyword(id) {
  await authFetch(`${API}/keywords/${id}`, { method: "DELETE" });
  loadKeywords();
}

/* ================= MANUTENÇÃO ================= */

async function loadMaintenanceStatus() {
  const res = await authFetch(`${API}/status`);
  const s = await res.json();

  const ativo = !!s.maintenance_mode;
  const statusEl = document.getElementById("maintenance-status");
  const btn = document.getElementById("btn-maintenance");

  statusEl.innerText = ativo ? "ATIVA" : "DESATIVADA";
  btn.innerText = ativo ? "Desativar manutenção" : "Ativar manutenção";
  btn.dataset.ativo = ativo ? "1" : "0";
}

async function toggleMaintenance() {
  const btn = document.getElementById("btn-maintenance");
  const ativoAtual = btn.dataset.ativo === "1";
  const novoValor = ativoAtual ? 0 : 1;

  await authFetch(`${API}/maintenance?ativo=${novoValor}`, { method: "POST" });
  loadMaintenanceStatus();
}

/* ================= INIT ================= */

document.addEventListener("DOMContentLoaded", async () => {
  await checkAuth();
  loadStatus();
  loadMaintenanceStatus();
  loadLoopInterval();
  loadClientes();
  clearClienteSelecionado();
  setInterval(loadStatus, 5000);
});
/* loop */
window.salvarLoop = async function () {
  const input = document.getElementById("loop-input");
  if (!input) {
    alert("Campo de loop não encontrado");
    return;
  }

  const minutos = parseInt(input.value);

  if (isNaN(minutos) || minutos <= 0) {
    alert("Informe um valor válido em minutos");
    return;
  }

  const segundos = minutos * 60;

  await authFetch(`${API}/loop-interval?segundos=${segundos}`, {
    method: "POST"
  });

  loadLoopInterval();
};

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("role");
  window.location.href = "login.html";
}
