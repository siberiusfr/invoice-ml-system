# 🔧 Troubleshooting - Résolution de problèmes

Guide des problèmes courants et leurs solutions.

---

## 🐳 Problèmes Docker

### Docker ne démarre pas

**Symptôme :**
```
Cannot connect to the Docker daemon
```

**Solutions :**
1. Ouvrir Docker Desktop
2. Attendre que le statut soit "Running" (icône verte)
3. Sur Mac : vérifier dans Préférences > Ressources
4. Sur Linux : `sudo systemctl start docker`

---

### Port 8080 déjà utilisé

**Symptôme :**
```
Error: port is already allocated
```

**Solution 1 : Changer le port**
Éditer `docker-compose.yml` :
```yaml
ports:
  - "8081:8080"  # Utiliser 8081 au lieu de 8080
```

**Solution 2 : Libérer le port**
```bash
# Trouver ce qui utilise le port
# Mac/Linux:
lsof -i :8080

# Windows:
netstat -ano | findstr :8080

# Arrêter le processus trouvé
```

---

### Label Studio ne démarre pas

**Vérifications :**
```bash
# 1. Vérifier les logs
docker-compose logs label-studio

# 2. Redémarrer proprement
docker-compose down
docker-compose up -d

# 3. Vérifier l'état
docker ps
```

---

## 🐍 Problèmes Python

### Module not found

**Symptôme :**
```
ModuleNotFoundError: No module named 'xxx'
```

**Solutions :**
```bash
# 1. Vérifier que l'environnement est activé
# Vous devez voir (venv) au début de votre terminal

# 2. Activer l'environnement
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# 3. Réinstaller les dépendances
pip install -r requirements.txt

# 4. Si ça ne marche toujours pas
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

### Python command not found

**Symptôme :**
```
python: command not found
```

**Solutions :**

**Windows :**
- Réinstaller Python en cochant "Add to PATH"
- Ou utiliser `py` au lieu de `python`

**Mac :**
```bash
# Utiliser python3
python3 --version

# Créer un alias (optionnel)
echo "alias python=python3" >> ~/.zshrc
source ~/.zshrc
```

**Linux :**
```bash
sudo apt install python3 python3-pip
```

---

### Permission denied

**Symptôme :**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions :**
```bash
# 1. Vérifier les permissions du dossier
ls -la

# 2. Changer les permissions
chmod -R 755 data/

# 3. Sur Windows, exécuter le terminal en admin
```

---

## 📊 Problèmes Label Studio

### Cannot connect to Label Studio

**Symptôme :**
```
❌ Erreur de connexion : ...
```

**Checklist :**
1. ✅ Label Studio est lancé ? → `docker ps`
2. ✅ Accessible dans le navigateur ? → http://localhost:8080
3. ✅ API key correcte dans `config/settings.yaml` ?
4. ✅ Project ID correct ?

**Récupérer l'API key :**
1. Se connecter à Label Studio
2. Cliquer sur votre nom (en haut à droite)
3. "Account Settings"
4. Onglet "Access Token"
5. Copier le token

---

### Factures ne s'affichent pas

**Symptôme :**
Factures importées mais images ne s'affichent pas

**Solutions :**
1. Vérifier le format (PDF, JPG, PNG supportés)
2. Vérifier la taille (< 10 MB recommandé)
3. Regarder les logs Docker : `docker-compose logs -f`

---

### Import échoue

**Symptôme :**
```
❌ Erreur d'import : ...
```

**Solutions :**
```bash
# 1. Vérifier que les factures existent
ls -la data/raw/invoices/

# 2. Vérifier les permissions
chmod -R 755 data/raw/invoices/

# 3. Tester avec une seule facture
# Déplacer toutes les factures sauf une
# Réessayer l'import
```

---

## 🤖 Problèmes d'entraînement

### CUDA not available

**Symptôme :**
```
CUDA not available, training on CPU
```

**C'est normal si vous n'avez pas de GPU NVIDIA**

**Solutions :**
1. **Utiliser Google Colab** (GPU gratuit)
   - Voir `notebooks/train_yolo_colab.ipynb`
2. Entraîner sur CPU (très lent mais fonctionne)
3. Utiliser un service cloud avec GPU

---

### Out of memory

**Symptôme :**
```
RuntimeError: CUDA out of memory
```

**Solutions :**
```python
# Dans votre script d'entraînement, réduire :
batch_size = 4  # Au lieu de 16
img_size = 416  # Au lieu de 640
```

---

### Training takes forever

**Normal sur CPU !**

**Temps estimés :**
- GPU (RTX 3060) : 1-2 heures
- CPU : 8-24 heures

**Solutions :**
1. Utiliser Google Colab (recommandé)
2. Réduire le nombre d'epochs (50 au lieu de 100)
3. Utiliser un modèle plus petit (yolov8n au lieu de yolov8m)

---

## 🌐 Problèmes API

### API doesn't start

**Symptôme :**
```
Address already in use
```

**Solution :**
Changer le port dans `config/settings.yaml` :
```yaml
api:
  port: 8001  # Au lieu de 8000
```

---

### Model not found

**Symptôme :**
```
FileNotFoundError: model file not found
```

**Solution :**
```bash
# Vérifier que le modèle existe
ls -la data/models/production/

# Si absent, entraîner d'abord le modèle
python training/train_yolo.py
```

---

## 💾 Problèmes de données

### Annotations perdues

**Prévention :**
```bash
# Sauvegarder régulièrement
python scripts/export_from_label_studio.py

# Backups automatiques
cp -r data/label-studio data/label-studio.backup
```

**Restauration :**
```bash
# Si backup existe
docker-compose down
rm -rf data/label-studio
cp -r data/label-studio.backup data/label-studio
docker-compose up -d
```

---

### Export failed

**Symptôme :**
```
❌ Erreur d'export : ...
```

**Solutions :**
1. Vérifier la connexion Label Studio
2. Vérifier que vous avez des annotations complètes
3. Exporter manuellement depuis Label Studio :
   - Projet > Export > JSON

---

## 🔍 Diagnostic général

### Script de diagnostic

Créez un fichier `diagnose.py` :

```python
#!/usr/bin/env python3
import sys
import subprocess

def check_command(cmd, name):
    try:
        result = subprocess.run([cmd, '--version'], 
                               capture_output=True, text=True)
        print(f"✅ {name}: OK")
        return True
    except:
        print(f"❌ {name}: NOT FOUND")
        return False

print("🔍 Diagnostic du système\n")
print("=" * 50)

check_command('python', 'Python')
check_command('docker', 'Docker')
check_command('git', 'Git')

print("\n📦 Modules Python:")
modules = ['torch', 'cv2', 'fastapi', 'label_studio_sdk']
for module in modules:
    try:
        __import__(module)
        print(f"  ✅ {module}")
    except:
        print(f"  ❌ {module}")

print("\n🐳 Docker:")
try:
    result = subprocess.run(['docker', 'ps'], 
                           capture_output=True, text=True)
    if 'label-studio' in result.stdout:
        print("  ✅ Label Studio running")
    else:
        print("  ⚠️  Label Studio not running")
except:
    print("  ❌ Cannot connect to Docker")

print("\n" + "=" * 50)
```

Exécuter :
```bash
python diagnose.py
```

---

## 🆘 Toujours bloqué ?

### Récupérer les logs

```bash
# Logs Docker
docker-compose logs > logs/docker.log

# Logs Python (si configuré)
cat logs/system.log

# Envoyer ces fichiers avec votre question
```

### Où demander de l'aide

1. **GitHub Issues** : Pour les bugs
2. **GitHub Discussions** : Pour les questions
3. **Documentation** : Relire les guides

### Informations à fournir

Quand vous demandez de l'aide, incluez :
- Système d'exploitation (Windows 10, macOS 14, Ubuntu 22.04)
- Version Python : `python --version`
- Logs d'erreur complets
- Ce que vous avez déjà essayé

---

## 🔄 Réinitialisation complète

**En dernier recours :**

```bash
# ⚠️ ATTENTION : Supprime TOUTES les données !

# 1. Arrêter tout
docker-compose down -v

# 2. Supprimer les données
rm -rf data/label-studio/*
rm -rf data/processed/*
rm -rf data/models/*

# 3. Réinstaller
pip install -r requirements.txt --force-reinstall

# 4. Redémarrer
docker-compose up -d
```

---

**La plupart des problèmes ont une solution simple ! Ne désespérez pas 💪**
