import unicodedata
import re
import hashlib
from datetime import datetime, time as dt_time

from backend.core.ia_resumo import gerar_resumo_ia
from backend.core.monitor_state import monitor_state
from backend.core.email_sender import enviar_email_alerta
from backend.core.database import (
    listar_clientes,
    listar_emails,
    listar_keywords,
    salvar_alerta_db,
    alerta_ja_enviado
)

def normalizar(texto: str) -> str:
    if not texto:
        return ""
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto


def dentro_do_horario(hora_inicio: str, hora_fim: str) -> bool:
    if not hora_inicio or not hora_fim:
        return True
    try:
        inicio = dt_time.fromisoformat(hora_inicio)
        fim = dt_time.fromisoformat(hora_fim)
        agora = datetime.now().time()
        return inicio <= agora <= fim
    except Exception:
        return True


def gerar_alert_hash(cliente_id: int, termos: str, trecho: str) -> str:
    base = f"{cliente_id}|{termos}|{trecho[:500]}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def extrair_linha_curta(texto: str, termo: str, limite: int = 120) -> str:
    texto_lower = texto.lower()
    termo_lower = termo.lower()

    idx = texto_lower.find(termo_lower)
    if idx == -1:
        return texto.strip()[:limite] + "..."

    inicio = max(0, idx - limite)
    fim = min(len(texto), idx + len(termo) + limite)

    linha = texto[inicio:fim]
    linha = linha.replace("\n", " ").replace("\r", " ").strip()

    if inicio > 0:
        linha = "..." + linha
    if fim < len(texto):
        linha = linha + "..."

    return linha


def verificar_alertas(texto: str, url_ato: str, pdf_path: str | None = None) -> int:
    import os
    from backend.core.pdf_highlighter import destacar_keywords_pdf

    print("\n[DEBUG] analyzer iniciado")
    print("[DEBUG] texto recebido len:", len(texto))

    total_alertas = 0
    texto_normalizado = normalizar(texto)

    clientes = listar_clientes()
    print("[DEBUG] clientes encontrados:", len(clientes))

    for cliente in clientes:
        if not cliente.get("ativo"):
            continue

        cliente_id = cliente["id"]
        cliente_nome = cliente["nome"]
        print(f"\n[DEBUG] processando cliente {cliente_id} - {cliente_nome}")

        emails_raw = listar_emails(cliente_id)
        emails = [
            e["email"].lower()
            for e in emails_raw
            if (e.get("ativo") in (True, 1, "true")) and e.get("email")
        ]

        print("[DEBUG] emails ativos:", emails)

        if not emails:
            continue

        keywords_raw = listar_keywords(cliente_id)
        print("[DEBUG] keywords:", keywords_raw)

        for kw in keywords_raw:
            print("[DEBUG] analisando keyword:", kw)

            ativo_kw = kw.get("ativo")
            if not (ativo_kw is True or ativo_kw == 1 or str(ativo_kw).lower() == "true"):
                continue

            if not dentro_do_horario(kw.get("hora_inicio"), kw.get("hora_fim")):
                print("[DEBUG] fora do horario, pulando")
                continue

            expressao_raw = (kw.get("expressao") or "").strip().lower()
            expressao_norm = normalizar(expressao_raw)

            if not expressao_norm:
                continue

            palavras = expressao_norm.split()
            encontrou = False

            if len(palavras) == 1 and len(palavras[0]) <= 5:
                padrao = rf"\b{re.escape(palavras[0])}\b"
                print("[DEBUG] regra palavra curta, padrao:", padrao)

                if re.search(padrao, texto_normalizado):
                    encontrou = True
            else:
                print("[DEBUG] regra expressao longa")
                if expressao_norm in texto_normalizado:
                    encontrou = True

            if not encontrou:
                print("[DEBUG] expressao nao encontrada, pulando")
                continue

            print("[DEBUG] expressao encontrada:", expressao_norm)

            trecho_curto = extrair_linha_curta(texto, expressao_raw)
            resumo_ia = gerar_resumo_ia(texto)
            trecho_final = resumo_ia if resumo_ia else trecho_curto

            alert_hash = gerar_alert_hash(cliente_id, expressao_norm, trecho_curto)

            if alerta_ja_enviado(cliente_id, alert_hash):
                print("[DEBUG] alerta ja enviado, pulando")
                continue

            pdf_final = pdf_path

            if pdf_path:
                try:
                    pdf_destacado = destacar_keywords_pdf(
                        pdf_path,
                        [expressao_raw],
                        suffix=alert_hash
                    )
                    if pdf_destacado and os.path.isfile(pdf_destacado):
                        pdf_final = pdf_destacado
                        print("[DEBUG] pdf destacado gerado")
                except Exception as e:
                    print("[WARN] erro ao gerar pdf destacado:", e)

            alerta = {
                "cliente_id": cliente_id,
                "cliente": cliente_nome,
                "emails": emails,
                "termos": expressao_norm,
                "trecho": trecho_final,
                "url": url_ato,
                "pdf_path": pdf_final,
                "alert_hash": alert_hash
            }

            print("[DEBUG] ALERTA PASSOU EM TODAS AS VALIDACOES")
            salvar_alerta_db(alerta)

            if not monitor_state.get("maintenance_mode"):
                enviar_email_alerta(alerta)

            total_alertas += 1
            print("[DEBUG] alerta gerado")

    print("\n[DEBUG] total de alertas:", total_alertas)
    print("[DEBUG] analyzer finalizado\n")

    return total_alertas
