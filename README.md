# ReceiptAI Glass — pont OCR (démo rapide)

Backend indépendant de l'Étape 6 (parkée, en attente du contrat API ReceiptAI). Chemin
court pour la démo : lunettes → scan confirmé → ce backend → OCR (Mistral OCR) → e-mail
vers ReceiptAI, exactement dans la forme qu'un humain enverrait aujourd'hui (ReceiptAI ne
sait ingérer que du texte par e-mail — voir `docs/02_Informations-a-collecter.md` §C).

Hébergement prévu pour la démo : **laptop local + hotspot** (évite toute dépendance au
réseau EPSA / aux blocages IT rencontrés sur ce projet).

## Étapes (docs/07)

1. ✅ `POST /scan` reçoit l'image, l'enregistre, répond `200` — valide le trajet réseau
   lunettes → backend avant d'ajouter de la logique.
2. ⬜ Client upload Android (`:network`) câblé sur `confirmScan()`.
3. ⬜ OCR (Mistral OCR) sur l'image reçue, texte loggé.
4. ⬜ Composition + envoi d'un e-mail vers une boîte de test (SendGrid, avec BCC vers une
   boîte réelle pour vérifier le format en debug).
5. ⬜ Bascule de l'adresse cible vers la boîte ReceiptAI (test).

## Setup

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash ; .venv\Scripts\activate.bat en cmd
pip install -r requirements.txt
cp .env.example .env            # puis remplir .env (jamais commité)
```

## Lancer en local

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Le `--host 0.0.0.0` est nécessaire pour que les lunettes (sur le même hotspot) puissent
joindre le laptop par son IP locale — pas seulement `127.0.0.1`.

## Tester

```bash
curl http://localhost:8000/health
curl -F "image=@test.jpg" http://localhost:8000/scan
```

Depuis un autre appareil sur le même réseau : remplacer `localhost` par l'IP locale du
laptop (`ipconfig` / `ifconfig` → adresse Wi-Fi, ex. `192.168.x.x`).

Swagger interactif : http://localhost:8000/docs
