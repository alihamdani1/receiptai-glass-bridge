"""
Normalisation du texte OCR (docs/07) — second appel LLM, avec un vrai prompt système cette fois
(contrairement à `ocr.process` — Mistral OCR — qui ne fait que transcrire, sans instruction
possible). Reformate le texte OCR brut en structure fixe, plus fiable à parser pour
l'extracteur texte de ReceiptAI (lui-même un LLM — un texte source propre et structuré en
entrée donne une extraction bien plus fiable en sortie côté ReceiptAI).

Fournisseur choisi par l'utilisateur : **OpenAI GPT-4o**, distinct de l'OCR (Mistral) — clé
séparée (`OPENAI_API_KEY`), voir `.env.example`.
"""

import logging

from openai import OpenAI

from app.config import OPENAI_API_KEY

logger = logging.getLogger("receiptai-glass-bridge")

SYSTEM_PROMPT = """Tu reformates le texte brut extrait par OCR d'un bon de livraison en une \
structure fixe, en français, sans rien inventer et sans commenter. Si une information est \
absente, écris "non identifié". Réponds uniquement avec ce format, rien d'autre :

Bon de livraison — <fournisseur ou "non identifié">
Référence commande : <numéro ou "non identifié">
Date : <date ou "non identifié">

Articles reçus :
- <désignation> — quantité : <n>
(une ligne par article distinct identifiable ; si aucun n'est identifiable, une seule ligne \
"- non identifié")"""


class NormalizeError(Exception):
    pass


def normalize(raw_ocr_text: str) -> str:
    """Reformate [raw_ocr_text] selon SYSTEM_PROMPT (GPT-4o). Lève NormalizeError si indisponible."""
    if not OPENAI_API_KEY:
        raise NormalizeError("OPENAI_API_KEY absente")

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": raw_ocr_text},
        ],
        temperature=0.0,
    )

    content = (response.choices[0].message.content or "").strip()
    if not content:
        raise NormalizeError("réponse vide")
    return content
