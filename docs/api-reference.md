# 📖 API Reference

Documentation complète de l'API REST du système Invoice ML.

**Base URL:** `http://localhost:8000`

**Format:** JSON

**Version:** 1.0.0

---

## 🔑 Authentication

Actuellement, l'API ne nécessite pas d'authentification en mode développement.

Pour la production, il est recommandé d'ajouter:
- API Key dans les headers
- OAuth 2.0
- JWT tokens

---

## 📡 Endpoints

### 1. Root

Informations sur l'API.

```http
GET /
```

#### Response

```json
{
  "message": "Invoice ML System API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

### 2. Health Check

Vérifier l'état de l'API et du modèle.

```http
GET /health
```

#### Response

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "model_loaded": true,
  "model_version": "invoice_model_20240115_143022",
  "uptime_seconds": 3600.5
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | État de l'API ("healthy" ou "unhealthy") |
| `version` | string | Version de l'API |
| `model_loaded` | boolean | Le modèle est-il chargé ? |
| `model_version` | string \| null | Version du modèle chargé |
| `uptime_seconds` | float | Temps de fonctionnement en secondes |

---

### 3. Statistics

Récupérer les statistiques d'utilisation.

```http
GET /stats
```

#### Response

```json
{
  "total_extractions": 1250,
  "average_confidence": 0.87,
  "extractions_last_24h": 45,
  "model_version": "invoice_model_20240115",
  "success_rate": 0.95
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `total_extractions` | integer | Nombre total d'extractions |
| `average_confidence` | float | Confiance moyenne (0-1) |
| `extractions_last_24h` | integer | Extractions dans les dernières 24h |
| `model_version` | string | Version du modèle actuel |
| `success_rate` | float | Taux de succès (0-1) |

---

### 4. Extract Invoice

Extraire les données d'une facture.

```http
POST /extract
```

#### Request

**Content-Type:** `multipart/form-data`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Yes | Fichier PDF ou image (JPG, PNG) |

#### Example (curl)

```bash
curl -X POST "http://localhost:8000/extract" \
  -F "file=@facture.pdf"
```

#### Example (Python)

```python
import requests

url = "http://localhost:8000/extract"
files = {'file': open('facture.pdf', 'rb')}
response = requests.post(url, files=files)
data = response.json()
```

#### Example (JavaScript)

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/extract', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

#### Success Response (200 OK)

```json
{
  "success": true,
  "data": {
    "filename": "facture_001.pdf",
    "extracted_at": "2024-01-15T10:30:00.123456",
    "fields": [
      {
        "label": "numero_facture",
        "value": "[À extraire avec OCR]",
        "confidence": 0.95,
        "bbox": {
          "x": 0.1,
          "y": 0.05,
          "width": 0.2,
          "height": 0.03
        }
      },
      {
        "label": "date_facture",
        "value": "[À extraire avec OCR]",
        "confidence": 0.92,
        "bbox": {
          "x": 0.7,
          "y": 0.05,
          "width": 0.15,
          "height": 0.03
        }
      },
      {
        "label": "montant_ttc",
        "value": "[À extraire avec OCR]",
        "confidence": 0.89,
        "bbox": {
          "x": 0.7,
          "y": 0.8,
          "width": 0.2,
          "height": 0.04
        }
      }
    ],
    "overall_confidence": 0.87,
    "needs_review": false,
    "model_version": "invoice_model_20240115"
  },
  "message": "Extraction réussie"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Statut de l'extraction |
| `data` | object | Données extraites (si success=true) |
| `data.filename` | string | Nom du fichier traité |
| `data.extracted_at` | string | Date/heure de l'extraction (ISO 8601) |
| `data.fields` | array | Liste des champs extraits |
| `data.fields[].label` | string | Type de champ |
| `data.fields[].value` | string | Valeur extraite |
| `data.fields[].confidence` | float | Confiance (0-1) |
| `data.fields[].bbox` | object | Coordonnées de la bounding box |
| `data.overall_confidence` | float | Confiance moyenne |
| `data.needs_review` | boolean | Nécessite une validation humaine |
| `data.model_version` | string | Version du modèle utilisé |
| `message` | string | Message descriptif |

#### Error Response (400 Bad Request)

```json
{
  "success": false,
  "error": "Invalid file type",
  "message": "Type de fichier non supporté. Utilisez: .pdf, .jpg, .jpeg, .png"
}
```

#### Error Response (503 Service Unavailable)

```json
{
  "success": false,
  "error": "Model not loaded",
  "message": "Le modèle n'est pas chargé. Entraînez d'abord un modèle."
}
```

---

### 5. Reload Model

Recharger le modèle (après réentraînement).

```http
POST /reload-model
```

#### Request (optional)

**Content-Type:** `application/json`

```json
{
  "model_path": "data/models/invoice_model_20240116.pt"
}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model_path` | string | No | Chemin vers un modèle spécifique |

Si `model_path` n'est pas fourni, le dernier modèle sera chargé automatiquement.

#### Success Response (200 OK)

```json
{
  "success": true,
  "message": "Modèle rechargé avec succès",
  "model_version": "invoice_model_20240116"
}
```

#### Error Response (500 Internal Server Error)

```json
{
  "detail": "Erreur lors du chargement du modèle: [message d'erreur]"
}
```

---

## 📦 Data Models

### BoundingBox

Coordonnées normalisées d'une bounding box (0-1).

```json
{
  "x": 0.1,
  "y": 0.05,
  "width": 0.2,
  "height": 0.03
}
```

| Field | Type | Description |
|-------|------|-------------|
| `x` | float | Position X (pourcentage, 0-1) |
| `y` | float | Position Y (pourcentage, 0-1) |
| `width` | float | Largeur (pourcentage, 0-1) |
| `height` | float | Hauteur (pourcentage, 0-1) |

### ExtractedField

Un champ extrait d'une facture.

```json
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
}
```

| Field | Type | Description |
|-------|------|-------------|
| `label` | string | Type de champ |
| `value` | string | Valeur extraite |
| `confidence` | float | Confiance du modèle (0-1) |
| `bbox` | BoundingBox \| null | Position du champ |

### Labels disponibles

| Label | Description |
|-------|-------------|
| `numero_facture` | Numéro de facture |
| `date_facture` | Date d'émission |
| `montant_ht` | Montant hors taxes |
| `montant_tva` | Montant de la TVA |
| `montant_ttc` | Montant total TTC |
| `nom_fournisseur` | Nom du fournisseur |
| `adresse_fournisseur` | Adresse complète |
| `siret_fournisseur` | Numéro SIRET |
| `ligne_produit` | Ligne de produit/service |

---

## 🔧 Configuration

L'API utilise `config/settings.yaml` pour la configuration:

```yaml
api:
  host: "0.0.0.0"
  port: 8000
  reload: true

  confidence_threshold: 0.85

  feedback_loop:
    enabled: true
    auto_send_to_label_studio: true
```

---

## ⚡ Rate Limits

Actuellement, aucune limite de taux n'est appliquée.

Pour la production, il est recommandé d'implémenter:
- 60 requêtes/minute par IP
- 1000 requêtes/heure par API key

---

## 📊 HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success - Requête réussie |
| 400 | Bad Request - Paramètres invalides |
| 403 | Forbidden - Accès refusé |
| 404 | Not Found - Endpoint non trouvé |
| 500 | Internal Server Error - Erreur serveur |
| 503 | Service Unavailable - Modèle non chargé |

---

## 🐛 Error Handling

Toutes les erreurs retournent un objet JSON:

```json
{
  "success": false,
  "error": "error_code",
  "message": "Description détaillée de l'erreur"
}
```

---

## 🔒 Best Practices

### Production

1. **Utiliser HTTPS**
2. **Ajouter une authentification** (API Key, OAuth)
3. **Implémenter le rate limiting**
4. **Logger toutes les requêtes**
5. **Surveiller les performances**

### Développement

1. **Utiliser /docs** pour tester les endpoints
2. **Vérifier /health** avant chaque session
3. **Surveiller /stats** pour les métriques

---

## 📝 Examples

### Workflow complet

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# 1. Vérifier l'état de l'API
health = requests.get(f"{BASE_URL}/health").json()
if not health['model_loaded']:
    print("Modèle non chargé !")
    exit(1)

# 2. Extraire une facture
with open('facture.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post(f"{BASE_URL}/extract", files=files)
    data = response.json()

# 3. Traiter les résultats
if data['success']:
    extraction = data['data']

    if extraction['needs_review']:
        print("⚠️ Confiance faible, nécessite une revue")

    # Extraire les champs
    for field in extraction['fields']:
        print(f"{field['label']}: {field['value']} ({field['confidence']:.2%})")
else:
    print(f"Erreur: {data['message']}")

# 4. Consulter les statistiques
stats = requests.get(f"{BASE_URL}/stats").json()
print(f"Total extractions: {stats['total_extractions']}")
```

---

## 🆘 Support

- Documentation complète: [/docs](http://localhost:8000/docs)
- ReDoc: [/redoc](http://localhost:8000/redoc)
- Issues: GitHub Issues
- Email: support@votredomaine.com

---

**Version de l'API:** 1.0.0

**Dernière mise à jour:** 2024-01-15
