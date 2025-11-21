# 📘 Phase 0 : Setup & Préparation

Ce guide vous accompagne pas-à-pas pour installer et configurer tout le système.

## ⏱️ Temps estimé : 1-2 heures

---

## 🎯 Objectifs de cette phase

- ✅ Installer tous les prérequis
- ✅ Cloner et configurer le projet
- ✅ Lancer Label Studio en local
- ✅ Créer votre premier projet d'annotation

---

## 📋 Étape 1 : Vérifier les prérequis

### 1.1 Installer Python 3.9+

**Windows :**
1. Télécharger depuis https://www.python.org/downloads/
2. ⚠️ **IMPORTANT** : Cocher "Add Python to PATH" lors de l'installation
3. Redémarrer le terminal
4. Vérifier : `python --version`

**Mac :**
```bash
# Installer Homebrew si pas déjà fait
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Installer Python
brew install python@3.11

# Vérifier
python3 --version
```

**Linux (Ubuntu/Debian) :**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 --version
```

### 1.2 Installer Docker Desktop

**Télécharger et installer :**
- Windows/Mac : https://www.docker.com/products/docker-desktop/
- Linux : https://docs.docker.com/engine/install/

**Vérifier l'installation :**
```bash
docker --version
docker-compose --version
```

**Démarrer Docker Desktop**
- Ouvrir l'application Docker Desktop
- Attendre que le statut soit "Running" (icône verte)

### 1.3 Installer Git

**Windows :**
- Télécharger : https://git-scm.com/download/win
- Installer avec les options par défaut

**Mac :**
```bash
brew install git
```

**Linux :**
```bash
sudo apt install git
```

**Vérifier :**
```bash
git --version
```

### 1.4 Installer un éditeur de code (optionnel mais recommandé)

**VS Code (recommandé) :**
- Télécharger : https://code.visualstudio.com/
- Extensions utiles :
  - Python
  - YAML
  - Docker

---

## 📥 Étape 2 : Cloner le projet

### 2.1 Créer un dossier de travail

```bash
# Créer un dossier pour vos projets
mkdir -p ~/projets
cd ~/projets
```

### 2.2 Cloner le repository

```bash
# Cloner depuis GitHub
git clone https://github.com/VOTRE-USERNAME/invoice-ml-system.git

# Entrer dans le dossier
cd invoice-ml-system

# Vérifier que tout est là
ls -la
```

Vous devriez voir :
```
api/
config/
data/
docs/
label-studio/
scripts/
training/
docker-compose.yml
README.md
requirements.txt
```

---

## 🐍 Étape 3 : Configurer l'environnement Python

### 3.1 Créer un environnement virtuel

**Pourquoi ?** Pour isoler les dépendances de ce projet.

```bash
# Créer l'environnement
python -m venv venv

# OU sur Mac/Linux si 'python' ne fonctionne pas :
python3 -m venv venv
```

### 3.2 Activer l'environnement

**Windows (PowerShell) :**
```powershell
venv\Scripts\Activate.ps1

# Si erreur de politique d'exécution :
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Windows (CMD) :**
```cmd
venv\Scripts\activate.bat
```

**Mac/Linux :**
```bash
source venv/bin/activate
```

**✅ Vérification :**
Vous devriez voir `(venv)` au début de votre ligne de commande :
```
(venv) C:\projets\invoice-ml-system>
```

### 3.3 Installer les dépendances

```bash
# Mettre à jour pip
pip install --upgrade pip

# Installer toutes les dépendances
pip install -r requirements.txt
```

⏱️ Cela prend 5-10 minutes selon votre connexion.

**En cas d'erreur :**
- Windows : Installez Microsoft C++ Build Tools
- Mac : `xcode-select --install`
- Linux : `sudo apt install python3-dev`

---

## 🐳 Étape 4 : Lancer Label Studio

### 4.1 Vérifier que Docker est lancé

Ouvrez Docker Desktop et vérifiez qu'il est en état "Running".

### 4.2 Démarrer Label Studio

```bash
# Depuis la racine du projet
docker-compose up -d
```

**Sortie attendue :**
```
Creating network "invoice-ml-system_invoice-network" ... done
Creating invoice-label-studio ... done
```

### 4.3 Vérifier que ça fonctionne

**Option 1 : Dans le navigateur**
- Ouvrir : http://localhost:8080
- Vous devriez voir la page de connexion Label Studio

**Option 2 : En ligne de commande**
```bash
docker ps
```

Vous devriez voir :
```
CONTAINER ID   IMAGE                              STATUS
xxx            heartexlabs/label-studio:latest    Up 10 seconds
```

### 4.4 Arrêter/Redémarrer Label Studio

**Arrêter :**
```bash
docker-compose down
```

**Redémarrer :**
```bash
docker-compose up -d
```

**Voir les logs :**
```bash
docker-compose logs -f
```

---

## 🎨 Étape 5 : Créer votre projet Label Studio

### 5.1 Créer un compte

1. Ouvrir http://localhost:8080
2. Cliquer sur "Sign Up"
3. Remplir :
   - Email : `admin@localhost` (ou votre email)
   - Mot de passe : `VotreMotDePasse123!`
4. Se connecter

### 5.2 Créer un projet

1. Cliquer sur "Create Project"
2. Nom du projet : `Factures`
3. Cliquer sur "Save"

### 5.3 Configurer le template d'annotation

1. Dans votre projet, aller dans "Settings" (⚙️)
2. Onglet "Labeling Interface"
3. Copier tout le contenu de `label-studio/invoice-template.xml`
4. Coller dans l'éditeur
5. Cliquer sur "Save"

**Aperçu du template :**
Vous devriez voir les labels de couleurs :
- 🔴 numero_facture
- 🟢 date_facture
- 🟡 montant_ttc
- etc.

### 5.4 Récupérer votre API Key

1. Cliquer sur votre nom (en haut à droite)
2. "Account Settings"
3. Onglet "Access Token"
4. Copier le token (format : `xxxxxxxxxxxxxxxxxxxxx`)

### 5.5 Récupérer le Project ID

Dans l'URL de votre projet :
```
http://localhost:8080/projects/1/data
                              ^
                              Votre project_id
```

---

## ⚙️ Étape 6 : Configurer le système

### 6.1 Créer le fichier de configuration

```bash
# Copier le fichier exemple
cp config/settings.example.yaml config/settings.yaml

# Ouvrir avec votre éditeur
# Windows :
notepad config/settings.yaml

# Mac :
open -a TextEdit config/settings.yaml

# Linux :
nano config/settings.yaml

# Ou avec VS Code :
code config/settings.yaml
```

### 6.2 Éditer la configuration

Modifier ces lignes :

```yaml
label_studio:
  url: "http://localhost:8080"
  api_key: "VOTRE_API_KEY_ICI"  # ← Coller votre API key
  project_id: 1                  # ← Votre project ID
```

**Sauvegarder et fermer.**

---

## 📁 Étape 7 : Préparer le dossier de factures

### 7.1 Créer la structure de dossiers

```bash
# Créer tous les dossiers nécessaires
mkdir -p data/raw/invoices
mkdir -p data/processed
mkdir -p data/models/production
mkdir -p data/models/staging
mkdir -p data/models/archive
mkdir -p logs
```

### 7.2 Placer vos factures

Copier vos factures (PDF, JPG, PNG) dans :
```
data/raw/invoices/
```

**Structure recommandée :**
```
data/raw/invoices/
├── facture_001.pdf
├── facture_002.jpg
├── facture_003.png
└── ...
```

---

## ✅ Étape 8 : Tester l'installation

### 8.1 Test Python

```bash
# Activer l'environnement si pas déjà fait
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Test rapide
python -c "import torch; import cv2; print('✅ Tout fonctionne !')"
```

### 8.2 Test Label Studio

```bash
# Vérifier que Label Studio répond
curl http://localhost:8080/api/health
```

Réponse attendue : `{"status":"UP"}`

### 8.3 Test d'import (optionnel)

Si vous avez déjà des factures dans `data/raw/invoices/` :

```bash
python scripts/import_to_label_studio.py
```

Vous devriez voir :
```
🚀 IMPORT DE FACTURES DANS LABEL STUDIO
✅ Connecté avec succès !
📁 Projet trouvé : Factures
📄 X factures trouvées
✅ Import réussi !
```

---

## 🎉 Phase 0 terminée !

### ✅ Checklist finale

- [x] Python 3.9+ installé
- [x] Docker Desktop installé et lancé
- [x] Projet cloné
- [x] Environnement virtuel créé et activé
- [x] Dépendances installées
- [x] Label Studio lancé (http://localhost:8080)
- [x] Compte Label Studio créé
- [x] Projet "Factures" créé
- [x] Template d'annotation configuré
- [x] Fichier config/settings.yaml configuré
- [x] Dossiers créés
- [x] Tests passés ✅

---

## 🚀 Prochaine étape

👉 **[Phase 1 : Labelling](phase1-labelling.md)**

C'est là que le vrai travail commence : annoter vos factures !

---

## 🆘 Problèmes courants

### Docker ne démarre pas

**Symptôme :** `Cannot connect to the Docker daemon`

**Solution :**
1. Ouvrir Docker Desktop
2. Attendre que le statut soit "Running"
3. Réessayer

### Port 8080 déjà utilisé

**Symptôme :** `port is already allocated`

**Solution :**
```bash
# Modifier le port dans docker-compose.yml
ports:
  - "8081:8080"  # Utiliser 8081 au lieu de 8080
```

### Import des factures ne fonctionne pas

**Symptôme :** `❌ Erreur de connexion`

**Vérifications :**
1. Label Studio est bien démarré ?
2. API key correcte dans config/settings.yaml ?
3. Project ID correct ?

### Python : module not found

**Symptôme :** `ModuleNotFoundError: No module named 'xxx'`

**Solution :**
```bash
# Vérifier que l'environnement est activé
# Devrait afficher (venv) au début de la ligne

# Réinstaller les dépendances
pip install -r requirements.txt
```

---

## 📞 Besoin d'aide ?

- 📖 Documentation : [README.md](../README.md)
- 🐛 Signaler un bug : [GitHub Issues](https://github.com/VOTRE-USERNAME/invoice-ml-system/issues)
- 💬 Poser une question : [GitHub Discussions](https://github.com/VOTRE-USERNAME/invoice-ml-system/discussions)

---

**Bon courage pour la suite ! 🚀**
