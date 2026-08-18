# core/email.py - Service d'envoi d'emails
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from typing import Optional
from config import settings


# ---------- Configuration SMTP ----------
mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_host,
    MAIL_STARTTLS=settings.mail_tls,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


# ---------- Fonction d'envoi ----------
async def send_email(
    to_email: EmailStr,
    subject: str,
    html_content: str,
) -> bool:
    """Envoie un email via SMTP."""
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[to_email],
            body=html_content,
            subtype="html",
        )
        fm = FastMail(mail_config)
        await fm.send_message(message)
        return True
    except Exception as e:
        print(f"❌ Erreur email : {str(e)}")
        return False


# ---------- Email d'activation ----------
def build_activation_email(nom: str, prenom: str, token: str) -> str:
    """Construit le HTML de l'email d'activation."""
    link = f"http://localhost:8000/auth/activate/{token}"

    return f"""
    <h2>Bonjour {prenom} {nom},</h2>
    <p>Votre compte a été créé.</p>
    <p>Cliquez ici pour activer votre compte :</p>
    <a href="{link}" style="background:#4CAF50;color:white;padding:10px 20px;text-decoration:none;border-radius:4px;">
        Activer mon compte
    </a>
    <p>Lien valable 24h.</p>
    """