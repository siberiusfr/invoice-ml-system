# 🧾 Invoice ML System - Système de Reconnaissance de Factures

Système complet d'extraction automatique de données de factures utilisant Machine Learning.

## 📋 Table des matières

- [Prérequis](#prérequis)
- [Installation rapide](#installation-rapide)
- [Phase 0 : Préparation](#phase-0--préparation)
- [Phase 1 : Labelling](#phase-1--labelling)
- [Phase 2 : Entraînement](#phase-2--entraînement)
- [Phase 3 : API Production](#phase-3--api-production)
- [FAQ](#faq)

## 🎯 Vue d'ensemble

Ce système vous permet de :
1. ✅ Annoter vos factures avec Label Studio (local)
2. ✅ Entraîner un modèle ML (YOLO ou LayoutLM)
3. ✅ Déployer une API REST pour extraction automatique
4. ✅ Améliorer continuellement le modèle

## 🔧 Prérequis

### Logiciels requis :

- **Python 3.9+** ([Télécharger](https://www.python.org/downloads/))
- **Docker Desktop** ([Télécharger](https://www.docker.com/products/docker-desktop/))
- **Git** ([Télécharger](https://git-scm.com/downloads))
- **Tesseract OCR** ([Guide d'installation](docs/tesseract-installation.md))
  - Windows: Télécharger depuis [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
  - macOS: `brew install tesseract tesseract-lang`
  - Linux: `sudo apt-get install tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng`
- **Éditeur de code** (VS Code recommandé)

### Vérifier l'installation :

```bash
# Vérifier Python
python --version
# Devrait afficher: Python 3.9.x ou supérieur

# Vérifier Docker
docker --version
# Devrait afficher: Docker version 20.x ou supérieur

# Vérifier Git
git --version
# Devrait afficher: git version 2.x

# Vérifier Tesseract
tesseract --version
# Devrait afficher: tesseract 5.x.x

# Vérifier toutes les dépendances automatiquement
python scripts/check_dependencies.py
```

## 🚀 Installation rapide

### 1. Cloner le repository

```bash
# Cloner le projet
git clone https://github.com/VOTRE-USERNAME/invoice-ml-system.git
cd invoice-ml-system

# Créer un environnement virtuel Python
python -m venv venv

# Activer l'environnement
# Sur Windows:
venv\Scripts\activate
# Sur Mac/Linux:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Lancer Label Studio (Docker)

```bash
# Démarrer Label Studio en local
docker-compose up -d

# Vérifier que ça fonctionne
# Ouvrir dans le navigateur: http://localhost:8080
```

### 3. Configuration initiale

```bash
# Copier le fichier de configuration exemple
cp config/settings.example.yaml config/settings.yaml

# Éditer avec vos paramètres (optionnel pour commencer)
```

## 📚 Phase 0 : Préparation

### ✅ Checklist

- [ ] Python, Docker et Git installés
- [ ] Repository cloné
- [ ] Environnement virtuel créé
- [ ] Label Studio lancé
- [ ] Compte Label Studio créé (http://localhost:8080)

### 🎬 Créer votre premier projet

1. Ouvrir http://localhost:8080
2. Créer un compte (email + mot de passe)
3. Créer un nouveau projet "Factures"
4. Utiliser le template fourni dans `label-studio/invoice-template.xml`

Voir le guide détaillé : [docs/phase0-setup.md](docs/phase0-setup.md)

## 📝 Phase 1 : Labelling

### 1. Préparer vos factures

```bash
# Placer vos factures PDF/images dans ce dossier
data/raw/invoices/
```

### 2. Importer dans Label Studio

```bash
# Script d'import automatique
python scripts/import_to_label_studio.py
```

### 3. Annoter vos factures

**Objectif :** Annoter 100-150 factures minimum

**Labels à utiliser :**
- `numero_facture` : Numéro de la facture
- `date_facture` : Date d'émission
- `montant_ht` : Montant hors taxes
- `montant_tva` : Montant de la TVA
- `montant_ttc` : Montant total TTC
- `nom_fournisseur` : Nom du fournisseur
- `adresse_fournisseur` : Adresse complète

**Temps estimé :** 15-20 heures pour 100 factures (10-15 min/facture)

Voir le guide détaillé : [docs/phase1-labelling.md](docs/phase1-labelling.md)

## 🤖 Phase 2 : Entraînement

### 1. Exporter les données

```bash
# Exporter depuis Label Studio
python scripts/export_from_label_studio.py

# Préparer le dataset
python scripts/prepare_dataset.py
```

### 2. Entraîner le modèle

**Option A : YOLO (Recommandé pour démarrer)**

```bash
# Entraînement local (si GPU disponible)
python training/train_yolo.py

# Ou sur Google Colab (GPU gratuit)
# Voir: notebooks/train_yolo_colab.ipynb
```

**Option B : LayoutLM (Plus avancé)**

```bash
python training/train_layoutlm.py
```

**Temps d'entraînement :**
- Avec GPU : 1-2 heures
- Sans GPU : 6-12 heures (pas recommandé)

### 3. Évaluer le modèle

```bash
python training/evaluate.py
```

Voir le guide détaillé : [docs/phase2-training.md](docs/phase2-training.md)

## 🚀 Phase 3 : API Production

### 1. Tester l'API en local

```bash
# Lancer l'API
python api/app.py

# L'API est disponible sur: http://localhost:8000
# Documentation: http://localhost:8000/docs
```

### 2. Tester l'extraction

```bash
# Test avec curl
curl -X POST "http://localhost:8000/extract" \
  -F "file=@test_invoice.pdf"

# Ou utiliser le script de test
python scripts/test_api.py
```

### 3. Intégration avec Label Studio (boucle de feedback)

```bash
# Activer l'envoi automatique vers Label Studio
# Éditer config/settings.yaml et définir:
# feedback_loop: enabled: true
```

Voir le guide détaillé : [docs/phase3-api.md](docs/phase3-api.md)

## 📊 Dashboard de monitoring

```bash
# Lancer le dashboard
python monitoring/dashboard.py

# Ouvrir: http://localhost:8001/dashboard
```

## 🔄 Réentraînement automatique

```bash
# Configuration du réentraînement automatique
python scripts/setup_auto_retrain.py

# Vérifier que tout fonctionne
python scripts/auto_retrain.py --dry-run
```

## 📖 Documentation complète

- [Guide complet d'installation](docs/installation-guide.md)
- [Bonnes pratiques de labelling](docs/labelling-best-practices.md)
- [Guide d'entraînement](docs/training-guide.md)
- [API Reference](docs/api-reference.md)
- [Troubleshooting](docs/troubleshooting.md)

## ❓ FAQ

**Q: Combien de factures dois-je annoter ?**
R: Minimum 100, idéalement 200-300 pour de bons résultats.

**Q: J'ai pas de GPU, je peux quand même entraîner ?**
R: Oui ! Utilisez Google Colab (gratuit) - voir notebooks/train_yolo_colab.ipynb

**Q: Combien de temps pour tout le projet ?**
R: Environ 3-4 semaines à temps partiel (10-15h/semaine)

**Q: Ça coûte combien ?**
R: Presque gratuit ! Juste du temps. Colab gratuit pour GPU.

**Q: Je peux annoter à plusieurs ?**
R: Oui ! Label Studio supporte le multi-utilisateur.

## 🆘 Besoin d'aide ?

- 📖 Documentation : [docs/](docs/)
- 🐛 Issues : [GitHub Issues](https://github.com/VOTRE-USERNAME/invoice-ml-system/issues)
- 💬 Discussions : [GitHub Discussions](https://github.com/VOTRE-USERNAME/invoice-ml-system/discussions)

## 📝 Licence

MIT License - Voir [LICENSE](LICENSE)

## 🙏 Remerciements

- [Label Studio](https://labelstud.io/) pour l'annotation
- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) pour la détection
- [FastAPI](https://fastapi.tiangolo.com/) pour l'API

---

**Fait avec ❤️ pour automatiser l'extraction de factures**
