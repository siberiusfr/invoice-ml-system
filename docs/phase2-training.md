# 🤖 Phase 2 : Entraînement du Modèle

Cette phase vous guide dans l'entraînement d'un modèle de détection pour vos factures.

## 📋 Prérequis

- ✅ Au moins 100 factures annotées (150-200 recommandé)
- ✅ Annotations exportées depuis Label Studio
- ✅ Dataset préparé au format YOLO

## 🎯 Objectif

Entraîner un modèle capable de détecter et localiser automatiquement les champs importants de vos factures.

---

## 1️⃣ Préparation du Dataset

### Exporter les annotations

```bash
python scripts/export_from_label_studio.py
```

**Vérifications:**
- Nombre d'annotations suffisant (≥ 100)
- Toutes les classes sont représentées
- Annotations de qualité

### Préparer le dataset YOLO

```bash
python scripts/prepare_dataset.py
```

**Ce script génère:**
- `data/processed/yolo_dataset/train/` - Images et labels d'entraînement
- `data/processed/yolo_dataset/val/` - Images et labels de validation
- `data/processed/yolo_dataset/test/` - Images et labels de test
- `data/processed/yolo_dataset/data.yaml` - Configuration YOLO

---

## 2️⃣ Choisir votre méthode d'entraînement

### Option A: Local (avec GPU) 🖥️

**Avantages:**
- Contrôle total
- Pas de limite de temps
- Données privées

**Inconvénients:**
- Nécessite un GPU NVIDIA
- Configuration plus complexe

**Prérequis:**
- CUDA et cuDNN installés
- GPU NVIDIA (RTX 2060 ou supérieur recommandé)
- Au moins 8 GB de VRAM

```bash
# Vérifier le GPU
python -c "import torch; print(torch.cuda.is_available())"

# Lancer l'entraînement
python training/train_yolo.py
```

### Option B: Google Colab (Recommandé) ☁️

**Avantages:**
- GPU gratuit (T4)
- Aucune installation requise
- Facile à utiliser

**Inconvénients:**
- Limite de 12h par session
- Nécessite upload du dataset

**Étapes:**

1. Zipper votre dataset:
```bash
cd data/processed
zip -r yolo_dataset.zip yolo_dataset/
```

2. Ouvrir le notebook Colab:
   - Aller dans `notebooks/train_yolo_colab.ipynb`
   - Ouvrir dans Google Colab
   - Activer le GPU (Runtime > Change runtime type > GPU)

3. Suivre les instructions du notebook

---

## 3️⃣ Paramètres d'entraînement

### Modèles YOLO disponibles

| Modèle | Taille | Vitesse | Précision | Usage |
|--------|--------|---------|-----------|-------|
| YOLOv8n | 3 MB | ⚡⚡⚡ | ⭐⭐ | Démarrage rapide |
| YOLOv8s | 11 MB | ⚡⚡ | ⭐⭐⭐ | **Recommandé** |
| YOLOv8m | 25 MB | ⚡ | ⭐⭐⭐⭐ | Meilleure précision |
| YOLOv8l | 43 MB | ⚡ | ⭐⭐⭐⭐⭐ | Production |

### Configuration recommandée

**Pour démarrer (dataset < 100 images):**
```bash
python training/train_yolo.py --model yolov8n.pt --epochs 100
```

**Configuration standard (100-200 images):**
```bash
python training/train_yolo.py --model yolov8s.pt --epochs 150
```

**Production (200+ images):**
```bash
python training/train_yolo.py --model yolov8m.pt --epochs 200
```

### Ajuster les paramètres

Éditez `config/settings.yaml`:

```yaml
training:
  yolo:
    model: "yolov8s.pt"
    epochs: 150
    batch_size: 16
    img_size: 640
    patience: 20  # Early stopping
```

---

## 4️⃣ Lancer l'entraînement

### Entraînement local

```bash
python training/train_yolo.py
```

**Monitoring:**
- Les métriques s'affichent en temps réel
- Les graphiques sont sauvegardés dans `data/models/`
- Le meilleur modèle est sauvegardé automatiquement

**Temps estimé:**
- Avec GPU (RTX 3060): 30-60 minutes
- Avec GPU (T4 Colab): 45-90 minutes
- Sans GPU (CPU): ❌ Non recommandé (6-12 heures)

### Surveiller l'entraînement

Indicateurs à surveiller:
- **Loss** (train/val): Doit diminuer progressivement
- **mAP**: Doit augmenter
- **Overfitting**: Si val loss augmente alors que train loss diminue

---

## 5️⃣ Évaluation du modèle

```bash
python training/evaluate.py
```

### Métriques importantes

#### Precision
Pourcentage de détections correctes parmi toutes les détections.

**Interprétation:**
- 0.8-1.0: ✅ Excellent
- 0.6-0.8: ⚠️ Correct
- < 0.6: ❌ Insuffisant

#### Recall
Pourcentage d'objets correctement détectés.

**Interprétation:**
- 0.8-1.0: ✅ Excellent
- 0.6-0.8: ⚠️ Correct
- < 0.6: ❌ Insuffisant

#### mAP@0.5
Métrique principale pour la détection d'objets.

**Interprétation:**
- 0.8-1.0: ✅ Production ready
- 0.6-0.8: ⚠️ Utilisable mais améliorable
- < 0.6: ❌ Besoin de plus de données

---

## 6️⃣ Améliorer les performances

### Si les résultats ne sont pas bons (mAP < 0.6)

**1. Plus de données**
- Annotez 50-100 factures supplémentaires
- Assurez-vous de la diversité (différents fournisseurs, formats)

**2. Qualité des annotations**
- Vérifiez que les bounding boxes sont précises
- Pas d'annotations manquantes
- Labels cohérents

**3. Augmenter les epochs**
```bash
python training/train_yolo.py --epochs 200
```

**4. Essayer un modèle plus grand**
```bash
python training/train_yolo.py --model yolov8m.pt
```

**5. Data augmentation**
Le modèle applique automatiquement:
- Rotation
- Flip
- Changement de luminosité
- Zoom

---

## 7️⃣ Sauvegarder le modèle

Le modèle est automatiquement sauvegardé dans:
```
data/models/invoice_model_YYYYMMDD_HHMMSS.pt
```

### Utiliser le modèle

```python
from ultralytics import YOLO

# Charger le modèle
model = YOLO('data/models/invoice_model_20240101_120000.pt')

# Faire une prédiction
results = model('facture.pdf')
```

---

## 8️⃣ Prochaines étapes

Une fois le modèle entraîné avec de bonnes performances (mAP > 0.6):

1. **Tester l'API**
```bash
python api/app.py
python scripts/test_api.py
```

2. **Déployer en production**
Voir: [docs/phase3-api.md](phase3-api.md)

3. **Configurer le réentraînement automatique**
```bash
python scripts/setup_auto_retrain.py
```

---

## 🆘 Problèmes courants

### Erreur: CUDA out of memory

**Solution:**
- Réduire le batch size: `--batch 8`
- Utiliser un modèle plus petit: `--model yolov8n.pt`
- Réduire la taille des images: `--imgsz 512`

### Loss ne diminue pas

**Causes possibles:**
- Données insuffisantes
- Annotations de mauvaise qualité
- Learning rate trop élevé

**Solutions:**
- Vérifier les annotations
- Annoter plus de factures
- Réduire le learning rate dans `config/settings.yaml`

### Overfitting

**Symptômes:**
- Train loss diminue mais val loss augmente
- mAP sur train élevé mais faible sur val

**Solutions:**
- Plus de données
- Augmenter la data augmentation
- Early stopping (déjà activé)

---

## 📊 Résumé

| Étape | Commande | Temps |
|-------|----------|-------|
| Export annotations | `python scripts/export_from_label_studio.py` | 1 min |
| Préparer dataset | `python scripts/prepare_dataset.py` | 2-5 min |
| Entraîner (GPU) | `python training/train_yolo.py` | 30-90 min |
| Évaluer | `python training/evaluate.py` | 2-5 min |

**Total: 1-2 heures**

---

**Prochain guide:** [Phase 3 - API & Production](phase3-api.md)
