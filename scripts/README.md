# 📜 Scripts d'automatisation

Ce dossier contient tous les scripts utilitaires pour gérer le système.

## 📝 Scripts disponibles

### 1. import_to_label_studio.py

**Fonction :** Importer vos factures dans Label Studio

**Usage :**
```bash
python scripts/import_to_label_studio.py
```

**Prérequis :**
- Label Studio lancé (docker-compose up -d)
- Factures dans `data/raw/invoices/`
- Configuration dans `config/settings.yaml`

**Ce qu'il fait :**
1. Scanne le dossier `data/raw/invoices/`
2. Trouve tous les PDF, JPG, PNG
3. Les convertit en base64
4. Les importe dans Label Studio
5. Évite les doublons

---

### 2. export_from_label_studio.py

**Fonction :** Exporter les annotations depuis Label Studio

**Usage :**
```bash
python scripts/export_from_label_studio.py
```

**Prérequis :**
- Au moins quelques factures annotées dans Label Studio

**Ce qu'il fait :**
1. Se connecte à Label Studio
2. Récupère toutes les tâches annotées
3. Génère des statistiques
4. Sauvegarde dans `data/exports/annotations_TIMESTAMP.json`

**Sortie :**
```
📊 STATISTIQUES
  Factures annotées : 127
  
  Annotations par type :
    • montant_ttc           : 127 occurrences
    • numero_facture        : 125 occurrences
    • date_facture          : 127 occurrences
    ...
```

---

### 3. prepare_dataset.py

**Fonction :** Préparer le dataset pour l'entraînement

**Usage :**
```bash
python scripts/prepare_dataset.py
python scripts/prepare_dataset.py --input exports/annotations_20240101.json
```

**Prérequis :**
- Avoir exporté les annotations (script 2)

**Ce qu'il fait :**
1. Charge les annotations exportées
2. Convertit au format YOLO
3. Split en train/val/test (80/10/10)
4. Génère le fichier data.yaml pour YOLO
5. Sauvegarde dans `data/processed/yolo_dataset/`

---

### 4. auto_retrain.py

**Fonction :** Réentraînement automatique du modèle

**Usage :**
```bash
python scripts/auto_retrain.py
python scripts/auto_retrain.py --dry-run  # Mode test
```

**Ce qu'il fait :**
1. Vérifie s'il y a assez de nouvelles annotations
2. Exporte depuis Label Studio
3. Prépare le dataset
4. Entraîne le modèle
5. Évalue les performances
6. Sauvegarde les informations d'entraînement

---

### 5. test_api.py

**Fonction :** Tester l'API avec des factures de test

**Usage :**
```bash
python scripts/test_api.py
python scripts/test_api.py --file data/raw/invoices/facture.pdf
python scripts/test_api.py --api http://192.168.1.100:8000
```

**Ce qu'il fait :**
1. Vérifie le health check de l'API
2. Récupère les statistiques
3. Teste l'extraction sur une facture
4. Affiche les résultats détaillés

---

### 6. setup_auto_retrain.py

**Fonction :** Configurer le réentraînement automatique planifié

**Usage :**
```bash
python scripts/setup_auto_retrain.py
```

**Ce qu'il fait :**
1. Génère les commandes pour cron (Linux/Mac)
2. Génère les commandes pour Task Scheduler (Windows)
3. Affiche les instructions de configuration

---

## 🔧 Ordre d'utilisation

```
1. import_to_label_studio.py    → Importer factures
2. [Annoter dans Label Studio]   → Travail manuel
3. export_from_label_studio.py  → Exporter annotations
4. prepare_dataset.py            → Préparer données
5. [Entraîner le modèle]         → training/train_yolo.py
6. test_api.py                   → Tester le résultat
7. auto_retrain.py               → Automatisation (optionnel)
```

---

## 🆘 En cas d'erreur

### Erreur de connexion Label Studio

```
❌ Erreur de connexion : ...
```

**Solutions :**
1. Vérifier que Label Studio est lancé : `docker ps`
2. Vérifier l'URL dans `config/settings.yaml`
3. Vérifier l'API key

### Aucune facture trouvée

```
⚠️  Aucune facture trouvée dans data/raw/invoices
```

**Solutions :**
1. Placez vos PDFs/images dans `data/raw/invoices/`
2. Vérifiez le chemin dans `config/settings.yaml`

### Module not found

```
ModuleNotFoundError: No module named 'xxx'
```

**Solution :**
```bash
# Vérifier que l'environnement virtuel est activé
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Réinstaller les dépendances
pip install -r requirements.txt
```

---

## 💡 Astuces

### Exécution automatique

Ajoutez au crontab pour exécution automatique :

```bash
# Vérifier nouvelles factures toutes les heures
0 * * * * cd /path/to/project && venv/bin/python scripts/import_to_label_studio.py

# Réentraîner tous les jours à 3h
0 3 * * * cd /path/to/project && venv/bin/python scripts/auto_retrain.py
```

### Logs

Rediriger les logs vers un fichier :

```bash
python scripts/import_to_label_studio.py >> logs/import.log 2>&1
```

---

**Besoin d'aide ?** Voir [docs/troubleshooting.md](../docs/troubleshooting.md)
