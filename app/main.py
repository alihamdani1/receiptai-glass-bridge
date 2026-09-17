"""
ReceiptAI Glass — pont OCR démo rapide (docs/07, chemin indépendant de l'Étape 6 parkée).

Étape 1 (celle-ci) : reçoit le scan des lunettes, l'enregistre sur disque, répond 200.
Pas d'OCR ni d'e-mail encore — on valide d'abord le trajet réseau lunettes -> backend,
le maillon le plus incertain (Wi-Fi des lunettes), avant d'ajouter de la logique dessus.

Lancer en local :
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Tester :
    curl -F "image=@test.jpg" http://<ip-laptop>:8000/scan
"""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from app.config import UPLOAD_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("receiptai-glass-bridge")

app = FastAPI(title="ReceiptAI Glass Bridge", version="0.1.0")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/health")
def health() -> dict:
    """Sanity check — sert aussi à valider la connectivité lunettes/laptop avant tout upload."""
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

    return JSONResponse(
        status_code=200,
        content={"status": "received", "scan_id": scan_id, "bytes": len(contents)},
    )
