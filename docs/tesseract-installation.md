# Installation de Tesseract OCR

Tesseract est requis pour extraire le texte des zones détectées sur les factures.

## 🖥️ Installation selon votre système

### Windows

**Option 1 : Installeur officiel (Recommandé)**

1. Télécharger l'installeur depuis : https://github.com/UB-Mannheim/tesseract/wiki
2. Choisir la version 64-bit (ex: `tesseract-ocr-w64-setup-5.3.3.exe`)
3. Lancer l'installeur
4. **IMPORTANT** : Cocher "Additional language data (download)" et sélectionner :
   - `fra` (Français)
   - `eng` (Anglais)
5. Noter le chemin d'installation (généralement `C:\Program Files\Tesseract-OCR`)

**Option 2 : Chocolatey**

```powershell
choco install tesseract
```

**Configuration Windows**

Ajouter Tesseract au PATH :
1. Rechercher "Variables d'environnement" dans Windows
2. Cliquer sur "Variables d'environnement..."
3. Dans "Variables système", sélectionner "Path" et cliquer "Modifier"
4. Ajouter : `C:\Program Files\Tesseract-OCR`
5. Redémarrer le terminal

Ou configurer dans votre code Python :
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

---

### macOS

**Option 1 : Homebrew (Recommandé)**

```bash
# Installer Homebrew si ce n'est pas fait
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Installer Tesseract avec les langues française et anglaise
brew install tesseract tesseract-lang
```

**Option 2 : MacPorts**

```bash
sudo port install tesseract
sudo port install tesseract-fra
sudo port install tesseract-eng
```

**Vérification**

```bash
tesseract --version
# Doit afficher : tesseract 5.x.x

tesseract --list-langs
# Doit inclure : fra, eng
```

---

### Linux (Ubuntu/Debian)

```bash
# Installer Tesseract et les packs de langue
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng

# Vérifier l'installation
tesseract --version
tesseract --list-langs
```

---

### Linux (Fedora/CentOS/RHEL)

```bash
# Installer Tesseract
sudo dnf install tesseract tesseract-langpack-fra tesseract-langpack-eng

# Vérifier l'installation
tesseract --version
tesseract --list-langs
```

---

### Linux (Arch)

```bash
# Installer Tesseract
sudo pacman -S tesseract tesseract-data-fra tesseract-data-eng

# Vérifier l'installation
tesseract --version
tesseract --list-langs
```

---

## ✅ Vérification de l'installation

Après installation, vérifier que tout fonctionne :

```bash
# Vérifier la version
tesseract --version

# Vérifier les langues installées
tesseract --list-langs
```

Vous devriez voir :
```
List of available languages (2):
eng
fra
```

---

## 🧪 Test rapide

Créer un fichier `test_ocr.py` :

```python
import pytesseract
from PIL import Image
import numpy as np

# Test simple
print("Version Tesseract:", pytesseract.get_tesseract_version())
print("Langues disponibles:", pytesseract.get_languages())

# Test d'extraction sur une image vide avec du texte
img = Image.new('RGB', (200, 50), color='white')
# (Normalement, vous utiliseriez une vraie image de facture)

text = pytesseract.image_to_string(img, lang='fra+eng')
print("Test OCR réussi !")
```

Exécuter :
```bash
python test_ocr.py
```

---

## 🐳 Utilisation avec Docker

Si vous utilisez Docker pour votre environnement, ajouter Tesseract au Dockerfile :

```dockerfile
# Pour Ubuntu/Debian
RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng && \
    rm -rf /var/lib/apt/lists/*
```

---

## ⚠️ Problèmes courants

### Erreur : "TesseractNotFoundError"

**Cause** : Tesseract n'est pas trouvé dans le PATH

**Solution Windows** :
```python
# Dans api/extractor.py, ajouter au début de la classe :
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**Solution Mac/Linux** :
```bash
# Vérifier que tesseract est dans le PATH
which tesseract
```

### Erreur : "requested language 'fra' is not available"

**Cause** : Les packs de langue ne sont pas installés

**Solution** : Réinstaller avec les langues (voir instructions ci-dessus)

### OCR de mauvaise qualité

**Solutions** :
1. Vérifier que l'image est de bonne qualité (min 300 DPI)
2. S'assurer que le contraste est bon
3. Tester avec différents modes PSM de Tesseract
4. Augmenter la résolution des images avant OCR

---

## 📊 Performance

### Temps d'exécution typique (par champ) :
- Petit champ (numéro) : ~50-100ms
- Champ moyen (montant) : ~100-200ms
- Gros champ (adresse) : ~200-500ms

### Précision attendue :
- Chiffres : 95-99%
- Texte simple : 90-95%
- Texte complexe : 80-90%

---

## 🚀 Pour aller plus loin

### Alternatives à Tesseract

Si Tesseract ne donne pas de bons résultats :

1. **PaddleOCR** (Recommandé pour meilleure précision)
   ```bash
   pip install paddlepaddle paddleocr
   ```

2. **EasyOCR**
   ```bash
   pip install easyocr
   ```

3. **Google Cloud Vision API** (Payant, très précis)
4. **Azure Computer Vision** (Payant)

### Configuration avancée

Créer un fichier de configuration Tesseract (`tesseract.conf`) :
```
tessedit_char_whitelist 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,€$-/
```

---

## 📚 Ressources

- [Tesseract Documentation](https://tesseract-ocr.github.io/)
- [Liste des PSM modes](https://github.com/tesseract-ocr/tesseract/blob/main/doc/tesseract.1.asc#options)
- [Améliorer la précision OCR](https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html)
