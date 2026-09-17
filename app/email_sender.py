"""
Composition + envoi de l'e-mail vers ReceiptAI (docs/07 Étape 4-5).

ReceiptAI n'ingère aujourd'hui que du texte par e-mail (docs/02 §C.0) — ce module imite ce
qu'un humain enverrait : un e-mail décrivant ce qui a été reçu, à partir du texte OCR.
"""

import logging
from datetime import datetime, timezone

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Bcc, Content, Email, Mail, To

from app.config import DEBUG_BCC_EMAIL, RECEIPTAI_EMAIL, SENDER_EMAIL, SENDGRID_API_KEY

logger = logging.getLogger("receiptai-glass-bridge")


class EmailError(Exception):
    pass


def _compose_body(ocr_text: str) -> str:
    return (
        "Bonjour,<br><br>"
        "Voici le contenu du bon de livraison scanné (capture assistée par lunettes "
        "ReceiptAI Glass) :<br><br>"
        f"<pre style=\"white-space:pre-wrap;font-family:inherit\">{ocr_text}</pre><br>"
        "Merci de traiter cette réception.<br>"
    )


def send_scan_email(ocr_text: str) -> None:
    if not SENDGRID_API_KEY:
        raise EmailError("SENDGRID_API_KEY absente (variable d'environnement Render)")
    if not SENDER_EMAIL:
        raise EmailError("SENDER_EMAIL absente")
    if not RECEIPTAI_EMAIL:
        raise EmailError("RECEIPTAI_EMAIL absente")

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    message = Mail(
        from_email=Email(SENDER_EMAIL),
        to_emails=To(RECEIPTAI_EMAIL),
        subject=f"Bon de livraison scanné — {ts}",
        html_content=Content("text/html", _compose_body(ocr_text)),
    )
    if DEBUG_BCC_EMAIL:
        message.add_bcc(Bcc(DEBUG_BCC_EMAIL))

    try:
        response = SendGridAPIClient(SENDGRID_API_KEY).send(message)
    except Exception as e:
        raise EmailError(str(e)) from e

    if response.status_code >= 300:
        raise EmailError(f"SendGrid a répondu {response.status_code}")

    logger.info("e-mail envoyé vers %s (bcc=%s), status=%d", RECEIPTAI_EMAIL, DEBUG_BCC_EMAIL or "-", response.status_code)
