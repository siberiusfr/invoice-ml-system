# 🚀 Quick Start - Démarrage en 10 minutes

Pour les impatients ! Guide minimaliste pour démarrer rapidement.

## ⚡ Installation Express

```bash
# 1. Cloner
git clone https://github.com/VOTRE-USERNAME/invoice-ml-system.git
cd invoice-ml-system

# 2. Python
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Label Studio
docker-compose up -d

# 4. Configuration
cp config/settings.example.yaml config/settings.yaml
# Éditer settings.yaml avec votre API key

# 5. Importer vos factures
# Copier vos PDFs dans data/raw/invoices/
python scripts/import_to_label_studio.py
```

## 📝 Annotation

1. Ouvrir http://localhost:8080
2. Se connecter
3. Annoter 100-150 factures (15-20h)

## 🤖 Entraînement

```bash
# Exporter les données
python scripts/export_from_label_studio.py

# Préparer le dataset
python scripts/prepare_dataset.py

# Entraîner (avec GPU recommandé)
python training/train_yolo.py
```

## 🚀 API

```bash
# Lancer l'API
python api/app.py

# Tester
curl -X POST "http://localhost:8000/extract" \
  -F "file=@test.pdf"
```

## 📚 Documentation complète

→ [README.md](README.md) pour le guide complet

---

**Temps total estimé : 3-4 semaines (temps partiel)**

**Besoin d'aide ?** Voir [docs/troubleshooting.md](docs/troubleshooting.md)
