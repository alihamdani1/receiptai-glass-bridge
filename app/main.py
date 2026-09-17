"""
ReceiptAI Glass — pont OCR démo rapide (docs/07, chemin indépendant de l'Étape 6 parkée).

    scan lunettes -> POST /scan -> enregistrement local -> OCR (Mistral OCR)
                                                          -> normalisation (LLM, structure fixe)
                                                          -> e-mail (SendGrid) -> ReceiptAI

ReceiptAI n'ingère aujourd'hui que du texte par e-mail (docs/02 §C.0) — ce backend imite ce
qu'un humain enverrait, à partir du texte extrait du bordereau scanné. La normalisation
reformate le texte OCR brut (souvent désordonné) en structure fixe avant l'envoi — un texte
source propre donne une extraction bien plus fiable côté ReceiptAI (lui-même un LLM).

OCR, normalisation et e-mail sont **best-effort** : si une variable d'environnement requise
manque, ou si un appel échoue, `/scan` répond quand même `200` (le scan est bien reçu) avec le
détail de ce qui a marché ou pas dans la réponse — utile pour itérer étape par étape. Si la
normalisation échoue, l'e-mail part quand même avec le texte OCR brut (repli, jamais bloquant).

Lancer en local :
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Tester :
    curl -F "image=@test.jpg" http://localhost:8000/scan
"""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from app.config import UPLOAD_DIR
from app.email_sender import EmailError, send_scan_email
from app.normalize import NormalizeError, normalize
from app.ocr import OcrError, extract_text

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("receiptai-glass-bridge")

app = FastAPI(title="ReceiptAI Glass Bridge", version="0.2.0")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/health")
def health() -> dict:
    """Sanity check — sert aussi à réveiller le service (tier gratuit Render : idle -> ~30-50 s)."""
    return {"status": "ok"}


@app.post("/scan")
async def receive_scan(image: UploadFile = File(...)) -> JSONResponse:
    scan_id = f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    ext = ".jpg"
    if image.filename and "." in image.filename:
        ext = "." + image.filename.rsplit(".", 1)[-1].lower()
    dest = UPLOAD_DIR / f"{scan_id}{ext}"

    contents = await image.read()
    dest.write_bytes(contents)
    logger.info("scan reçu: filename=%s bytes=%d -> %s", image.filename, len(contents), dest)

    result: dict = {"status": "received", "scan_id": scan_id, "bytes": len(contents)}

    ocr_text: str | None = None
    try:
        ocr_text = extract_text(contents, filename=dest.name)
        result["ocr"] = {"status": "ok", "chars": len(ocr_text), "preview": ocr_text[:200]}
        logger.info("scan %s: OCR ok, %d caractères", scan_id, len(ocr_text))
    except OcrError as e:
        result["ocr"] = {"status": "error", "detail": str(e)}
        logger.warning("scan %s: OCR échoué: %s", scan_id, e)

    email_text = ocr_text
    if ocr_text:
        try:
            structured = normalize(ocr_text)
            email_text = f"{structured}\n\n---\nTexte brut OCR (référence) :\n{ocr_text}"
            result["normalize"] = {"status": "ok"}
            logger.info("scan %s: normalisation ok", scan_id)
        except NormalizeError as e:
            result["normalize"] = {"status": "error", "detail": str(e)}
            logger.warning("scan %s: normalisation échouée, envoi du texte brut: %s", scan_id, e)

    if email_text:
        try:
            send_scan_email(email_text)
            result["email"] = {"status": "sent"}
            logger.info("scan %s: e-mail envoyé", scan_id)
        except EmailError as e:
            result["email"] = {"status": "error", "detail": str(e)}
            logger.warning("scan %s: e-mail échoué: %s", scan_id, e)
    else:
        result["email"] = {"status": "skipped", "detail": "pas de texte OCR"}

    return JSONResponse(status_code=200, content=result)
