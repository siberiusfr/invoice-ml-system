# 🚀 Phase 3 : API & Production

Cette phase vous guide dans le déploiement de votre modèle en production via une API REST.

## 📋 Prérequis

- ✅ Modèle entraîné avec de bonnes performances (mAP > 0.6)
- ✅ Modèle sauvegardé dans `data/models/`

## 🎯 Objectif

Déployer une API REST permettant d'extraire automatiquement les données de factures.

---

## 1️⃣ Architecture de l'API

```
┌─────────────┐
│   Client    │
│ (Web/Mobile)│
└──────┬──────┘
       │ HTTP POST /extract
       │ (PDF/Image)
       ▼
┌─────────────────────┐
│    FastAPI App      │
│  (api/app.py)       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Invoice Extractor  │
│  (api/extractor.py) │
└──────┬──────────────┘
       │
       ├──► YOLO Model (détection)
       │
       ├──► OCR (extraction texte) [TODO]
       │
       └──► Label Studio (feedback)
              (si confiance faible)
```

---

## 2️⃣ Lancer l'API en local

### Méthode 1: Directement

```bash
python api/app.py
```

### Méthode 2: Avec uvicorn

```bash
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

**L'API est maintenant disponible sur:**
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 3️⃣ Tester l'API

### Via le navigateur (Swagger UI)

1. Ouvrir http://localhost:8000/docs
2. Cliquer sur `/extract` > Try it out
3. Uploader une facture
4. Cliquer sur Execute
5. Voir les résultats

### Via curl

```bash
curl -X POST "http://localhost:8000/extract" \
  -F "file=@data/raw/invoices/facture.pdf"
```

### Via Python

```python
import requests

url = "http://localhost:8000/extract"
files = {'file': open('facture.pdf', 'rb')}
response = requests.post(url, files=files)

data = response.json()
print(data)
```

### Via le script de test

```bash
python scripts/test_api.py --file data/raw/invoices/facture.pdf
```

---

## 4️⃣ Endpoints disponibles

### GET /

Informations sur l'API

**Réponse:**
```json
{
  "message": "Invoice ML System API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### GET /health

Vérifier l'état de l'API

**Réponse:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model_loaded": true,
  "model_version": "invoice_model_20240101",
  "uptime_seconds": 3600.5
}
```

### GET /stats

Statistiques d'utilisation

**Réponse:**
```json
{
  "total_extractions": 1250,
  "average_confidence": 0.87,
  "extractions_last_24h": 45,
  "model_version": "invoice_model_20240101",
  "success_rate": 0.95
}
```

### POST /extract

Extraire les données d'une facture

**Paramètres:**
- `file`: Fichier PDF ou image (multipart/form-data)

**Réponse:**
```json
{
  "success": true,
  "data": {
    "filename": "facture_001.pdf",
    "extracted_at": "2024-01-15T10:30:00",
    "fields": [
      {
        "label": "numero_facture",
        "value": "INV-2024-001",
        "confidence": 0.95,
        "bbox": {
          "x": 0.1,
          "y": 0.05,
          "width": 0.2,
          "height": 0.03
        }
      },
      {
        "label": "montant_ttc",
        "value": "1250.00 EUR",
        "confidence": 0.89,
        "bbox": {...}
      }
    ],
    "overall_confidence": 0.87,
    "needs_review": false,
    "model_version": "invoice_model_20240101"
  },
  "message": "Extraction réussie"
}
```

### POST /reload-model

Recharger le modèle (après réentraînement)

**Paramètres:**
- `model_path` (optionnel): Chemin vers un modèle spécifique

**Réponse:**
```json
{
  "success": true,
  "message": "Modèle rechargé avec succès",
  "model_version": "invoice_model_20240115"
}
```

---

## 5️⃣ Configuration de l'API

Éditez `config/settings.yaml`:

```yaml
api:
  host: "0.0.0.0"
  port: 8000
  reload: true  # Dev mode uniquement

  # Seuil de confiance
  confidence_threshold: 0.85

  # Feedback loop
  feedback_loop:
    enabled: true
    auto_send_to_label_studio: true
```

### Seuil de confiance

**confidence_threshold**: Si la confiance moyenne est inférieure à ce seuil:
- `needs_review = true` dans la réponse
- La facture peut être envoyée automatiquement vers Label Studio (si activé)

**Recommandations:**
- Production stricte: 0.9
- Production standard: 0.85
- Développement: 0.7

---

## 6️⃣ Boucle de feedback (Continuous Learning)

### Concept

```
1. API reçoit une facture
2. Extraction automatique
3. Si confiance < threshold
   └─► Envoyer vers Label Studio
       pour annotation humaine
4. Nouvelles annotations
   └─► Réentraînement automatique
```

### Configuration

```yaml
feedback_loop:
  enabled: true
  auto_send_to_label_studio: true
```

### Workflow

1. **Extraction avec faible confiance**
   - L'API détecte `confidence < 0.85`
   - Envoie automatiquement vers Label Studio
   - Retourne quand même les résultats au client

2. **Annotation humaine**
   - L'opérateur corrige/valide dans Label Studio
   - Les annotations sont sauvegardées

3. **Réentraînement automatique**
   - Cron job vérifie les nouvelles annotations
   - Si >= 50 nouvelles annotations: réentraînement
   - Le nouveau modèle est évalué
   - Si meilleur: déployé automatiquement

---

## 7️⃣ Monitoring

### Dashboard

Lancer le dashboard de monitoring:

```bash
python monitoring/dashboard.py
```

Ouvrir: http://localhost:8001/dashboard

**Affiche:**
- Nombre total d'extractions
- Confiance moyenne
- Nombre de factures annotées
- Derniers modèles entraînés

### Logs

Les logs sont sauvegardés dans:
- `logs/api.log` - Logs de l'API
- `logs/system.log` - Logs système

**Niveau de log** (dans `config/settings.yaml`):
```yaml
monitoring:
  log_level: "INFO"  # DEBUG, INFO, WARNING, ERROR
```

---

## 8️⃣ Déploiement en production

### Option A: Docker

Créer un `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Construire et lancer:

```bash
docker build -t invoice-api .
docker run -p 8000:8000 invoice-api
```

### Option B: Serveur Linux

**1. Préparer le serveur**

```bash
# Installer Python 3.9+
sudo apt update
sudo apt install python3.9 python3-pip

# Cloner le projet
git clone https://github.com/username/invoice-ml-system.git
cd invoice-ml-system

# Installer les dépendances
pip install -r requirements.txt
```

**2. Utiliser systemd**

Créer `/etc/systemd/system/invoice-api.service`:

```ini
[Unit]
Description=Invoice ML API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/invoice-ml-system
Environment="PATH=/var/www/invoice-ml-system/venv/bin"
ExecStart=/var/www/invoice-ml-system/venv/bin/uvicorn api.app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Activer et lancer:

```bash
sudo systemctl enable invoice-api
sudo systemctl start invoice-api
sudo systemctl status invoice-api
```

**3. Reverse proxy avec Nginx**

```nginx
server {
    listen 80;
    server_name api.votredomaine.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Option C: Cloud (Heroku, AWS, GCP)

**TODO:** Guides détaillés à venir

---

## 9️⃣ Sécurité

### API Key

Ajouter une authentification par API key:

```python
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

API_KEY = "votre-cle-secrete"
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key
```

### HTTPS

En production, utilisez toujours HTTPS:
- Certificat Let's Encrypt (gratuit)
- Nginx avec SSL
- Load balancer avec SSL termination

### Rate Limiting

Limiter le nombre de requêtes par client:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/extract")
@limiter.limit("10/minute")
async def extract_invoice(...):
    ...
```

---

## 🔟 Performance

### Optimisations

**1. Batch processing**

Si vous recevez beaucoup de factures:
- Implémenter un système de queue (Celery + Redis)
- Traiter par batch

**2. Cache**

Cacher les résultats pour les factures déjà traitées:
- Redis pour le cache
- Utiliser le hash MD5 du fichier comme clé

**3. GPU**

Pour de meilleures performances:
- Déployer sur un serveur avec GPU
- Utiliser ONNX pour l'inférence

---

## 📊 Métriques de production

Surveiller ces métriques:

| Métrique | Cible | Action si < cible |
|----------|-------|-------------------|
| Temps de réponse | < 2s | Optimiser modèle |
| Confiance moyenne | > 0.85 | Réentraîner |
| Taux de succès | > 95% | Vérifier erreurs |
| Uptime | > 99% | Améliorer infra |

---

## 🆘 Problèmes courants

### API ne démarre pas

```bash
# Vérifier que le port est libre
lsof -i :8000

# Tuer le processus si nécessaire
kill -9 <PID>
```

### Modèle non chargé

```bash
# Vérifier que le modèle existe
ls -la data/models/

# Spécifier le chemin manuellement
POST /reload-model
{
  "model_path": "data/models/invoice_model_20240101.pt"
}
```

### Performance lente

- Vérifier la charge CPU/GPU
- Réduire la taille du modèle
- Activer le cache
- Utiliser un GPU

---

## 📚 Intégrations

### Frontend web

```javascript
async function extractInvoice(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('http://localhost:8000/extract', {
    method: 'POST',
    body: formData
  });

  const data = await response.json();
  return data;
}
```

### Application mobile

Utilisez la même API REST depuis:
- React Native
- Flutter
- Native iOS/Android

### ERP/Comptabilité

Intégrez avec votre système existant:
- Webhook pour notification
- Export vers CSV/JSON
- Connexion directe à la BDD

---

## 🎉 Résumé

| Étape | Commande | Temps |
|-------|----------|-------|
| Lancer API | `python api/app.py` | 10 sec |
| Tester | `python scripts/test_api.py` | 30 sec |
| Dashboard | `python monitoring/dashboard.py` | 10 sec |
| Déployer | Selon la méthode | 30-60 min |

---

**L'API est maintenant en production ! 🚀**

Pour aller plus loin:
- Configurer le réentraînement automatique
- Ajouter des fonctionnalités (export PDF, webhooks, etc.)
- Intégrer avec votre système existant
