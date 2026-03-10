import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from backend.config.settings import (
    EMAIL_HOST,
    EMAIL_PORT,
    EMAIL_REMETENTE,
    EMAIL_SENHA,
    EMAIL_DESTINATARIOS,
    APP_NAME
)


def enviar_email_alerta(entidade, termos, trecho, url):
    """
    Envia um email de alerta quando uma entidade monitorada é encontrada
    """

    assunto = f" ALERTA {APP_NAME} — {entidade}"

    corpo = f"""
Entidade monitorada:
{entidade}

Termos encontrados:
{termos}

Resumo automatico (IA):
{trecho}

Link do ato oficial:
{url}

---
Sistema: {APP_NAME}
"""

    msg = MIMEMultipart()
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = ", ".join(EMAIL_DESTINATARIOS)
    msg["Subject"] = assunto

    msg.attach(MIMEText(corpo, "plain", "utf-8"))

    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_REMETENTE, EMAIL_SENHA)
            server.send_message(msg)

        print("[INFO] Email enviado com sucesso")

    except Exception as e:
        print(f"[WARNING] Falha ao enviar email: {e}")
