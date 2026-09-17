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


def _env(name: str, default: str = "") -> str:
    """Comme `os.getenv`, mais `.strip()` la valeur — un espace/retour à la ligne collé par
    inadvertance dans un champ de variable d'environnement (Render, `.env`...) rend sinon une
    clé API "invalide" alors que la valeur copiée était correcte."""
    return os.getenv(name, default).strip()


# --- Étape 1-2 : réception du scan ---
UPLOAD_DIR = Path(_env("UPLOAD_DIR", str(BACKEND_DIR / "data" / "uploads")))

# --- Étape 3 : OCR (Mistral OCR) ---
MISTRAL_API_KEY = _env("MISTRAL_API_KEY")

# --- Étape 3bis : normalisation du texte OCR (GPT-4o via Azure OpenAI — ressource
# d'entreprise existante, pas api.openai.com — distinct de l'OCR) ---
OPENAI_API_KEY = _env("OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = _env("AZURE_OPENAI_ENDPOINT", "https://chatbot-procurement.openai.azure.com")
AZURE_OPENAI_API_VERSION = _env("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
AZURE_OPENAI_DEPLOYMENT = _env("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

# --- Étape 4-5 : e-mail (SendGrid) ---
SENDGRID_API_KEY = _env("SENDGRID_API_KEY")
SENDER_EMAIL = _env("SENDER_EMAIL")  # expéditeur vérifié côté SendGrid
DEBUG_BCC_EMAIL = _env("DEBUG_BCC_EMAIL")  # copie pour vérifier le format en debug
RECEIPTAI_EMAIL = _env("RECEIPTAI_EMAIL")  # boîte ReceiptAI (test pour l'instant)
