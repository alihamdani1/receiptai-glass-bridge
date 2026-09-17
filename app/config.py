"""
Configuration centralisée du backend (docs/07 — pont OCR démo rapide).

Tout vient de variables d'environnement, chargées depuis un fichier `.env` local
(jamais commité — voir `.env.example`). Les valeurs vides sont normales tant que
l'étape correspondante (OCR = Étape 3, e-mail = Étape 4/5) n'est pas câblée.
"""

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # python-dotenv pas encore installé — les variables d'env réelles marchent quand même

BACKEND_DIR = Path(__file__).resolve().parent.parent

# --- Étape 1-2 : réception du scan ---
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(BACKEND_DIR / "data" / "uploads")))

# --- Étape 3 : OCR (Mistral OCR) ---
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")

# --- Étape 4-5 : e-mail (SendGrid) ---
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")  # expéditeur vérifié côté SendGrid
DEBUG_BCC_EMAIL = os.getenv("DEBUG_BCC_EMAIL", "")  # copie pour vérifier le format en debug
RECEIPTAI_EMAIL = os.getenv("RECEIPTAI_EMAIL", "")  # boîte ReceiptAI (test pour l'instant)
