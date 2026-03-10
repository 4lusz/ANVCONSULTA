import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import make_msgid

from backend.config.settings import EMAIL_CONFIG
from backend.core.pdf_highlighter import destacar_keywords_pdf


def enviar_email_alerta(alerta: dict):
    emails = alerta.get("emails")

    if not emails or not isinstance(emails, list):
        print("[WARN] Alerta sem emails válidos, envio ignorado")
        return

    assunto = (
        f"[ANVISA-MONITOR]"
        f"[{alerta.get('cliente')}]"
        f"[{alerta.get('url', '')[-6:]}]"
        f" {alerta.get('termos')}"
    )

    linha = alerta.get("linha") or alerta.get("trecho", "")

    corpo = f"""
🔔 ALERTA ANVISA-MONITOR

Cliente:
{alerta.get('cliente')}

Keyword encontrada:
{alerta.get('termos')}

Resumo ia:
{linha}

Ato oficial:
{alerta.get('url')}
"""

    pdf_original = alerta.get("pdf_path")
    termos_lista = alerta.get("termos_lista") or []

    pdf_para_anexar = pdf_original

    # 🖍️ GERAR PDF DESTACADO (SE TIVER TERMOS)
    if pdf_original and os.path.isfile(pdf_original) and termos_lista:
        try:
            pdf_highlight = destacar_keywords_pdf(
                pdf_original,
                termos_lista
            )
            if pdf_highlight and os.path.isfile(pdf_highlight):
                pdf_para_anexar = pdf_highlight
                print(f"[HIGHLIGHT] PDF destacado gerado: {pdf_highlight}")
        except Exception as e:
            print("[WARN] Falha ao gerar PDF destacado")
            print(e)

    try:
        with smtplib.SMTP(
            EMAIL_CONFIG["smtp_server"],
            EMAIL_CONFIG["smtp_port"]
        ) as server:
            server.starttls()
            server.login(
                EMAIL_CONFIG["username"],
                EMAIL_CONFIG["password"]
            )

            for email_destino in emails:
                msg = MIMEMultipart()
                msg["From"] = EMAIL_CONFIG["from_email"]
                msg["To"] = email_destino
                msg["Subject"] = assunto

                msg["Message-ID"] = make_msgid()
                msg["X-ANVISA-Cliente"] = alerta.get("cliente", "unknown")
                msg["X-ANVISA-Ato"] = alerta.get("url", "")

                msg.attach(MIMEText(corpo, "plain", "utf-8"))

                # 📎 ANEXO PDF (DESTACADO OU ORIGINAL)
                if pdf_para_anexar and os.path.isfile(pdf_para_anexar):
                    try:
                        with open(pdf_para_anexar, "rb") as f:
                            anexo = MIMEApplication(f.read(), _subtype="pdf")
                            nome_pdf = os.path.basename(pdf_para_anexar)
                            anexo.add_header(
                                "Content-Disposition",
                                "attachment",
                                filename=nome_pdf
                            )
                            msg.attach(anexo)
                            print(f"[ATTACH] PDF anexado: {nome_pdf}")
                    except Exception as e:
                        print("[WARN] Falha ao anexar PDF")
                        print(e)

                server.send_message(msg)
                print(f"[INFO] Email enviado para {email_destino}")

    except Exception as e:
        print("[ERRO] Falha ao enviar email")
        print(e)
