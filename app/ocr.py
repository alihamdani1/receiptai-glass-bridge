"""
OCR via Mistral OCR (docs/07 Étape 3).

Flux vérifié sur l'exemple officiel du SDK (mistralai/client-python,
examples/mistral/ocr/ocr_process_from_file.py) : upload du fichier, puis
`ocr.process` référence ce fichier par son `file_id` — pas d'envoi en base64 brut.
"""

import logging

from mistralai.client import Mistral

from app.config import MISTRAL_API_KEY

logger = logging.getLogger("receiptai-glass-bridge")


class OcrError(Exception):
    pass


def extract_text(image_bytes: bytes, filename: str = "scan.jpg") -> str:
    """Envoie l'image à Mistral OCR, renvoie le texte extrait (markdown, pages concaténées)."""
    if not MISTRAL_API_KEY:
        raise OcrError("MISTRAL_API_KEY absente (variable d'environnement Render)")

    try:
        with Mistral(api_key=MISTRAL_API_KEY) as client:
            uploaded = client.files.upload(
                file={"file_name": filename, "content": image_bytes},
                purpose="ocr",
            )
            try:
                response = client.ocr.process(
                    document={"type": "file", "file_id": uploaded.id},
                    model="mistral-ocr-latest",
                )
            finally:
                try:
                    client.files.delete(file_id=uploaded.id)  # ne garde pas le fichier côté Mistral
                except Exception:
                    logger.warning("suppression fichier Mistral échouée (non bloquant)", exc_info=True)
    except OcrError:
        raise
    except Exception as e:
        raise OcrError(str(e)) from e

    pages = getattr(response, "pages", None) or []
    text = "\n\n".join((p.markdown or "").strip() for p in pages).strip()
    if not text:
        raise OcrError("aucun texte extrait")
    return text
