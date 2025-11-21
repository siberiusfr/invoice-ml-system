#!/bin/bash
# ==================================================
# Script d'installation automatique
# Invoice ML System - Setup rapide
# ==================================================

set -e  # Arrêter en cas d'erreur

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                       ║${NC}"
echo -e "${BLUE}║       🧾 INVOICE ML SYSTEM - Installation            ║${NC}"
echo -e "${BLUE}║                                                       ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# ==================================================
# 1. Vérifications des prérequis
# ==================================================

echo -e "${YELLOW}📋 Vérification des prérequis...${NC}"
echo ""

# Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "  ${GREEN}✅ Python3 installé${NC} (version $PYTHON_VERSION)"
else
    echo -e "  ${RED}❌ Python3 non trouvé${NC}"
    echo -e "  ${YELLOW}➡️  Installez Python 3.9+ depuis https://www.python.org${NC}"
    exit 1
fi

# Docker
if command -v docker &> /dev/null; then
    echo -e "  ${GREEN}✅ Docker installé${NC}"
else
    echo -e "  ${RED}❌ Docker non trouvé${NC}"
    echo -e "  ${YELLOW}➡️  Installez Docker Desktop depuis https://www.docker.com${NC}"
    exit 1
fi

# Docker Compose
if command -v docker-compose &> /dev/null; then
    echo -e "  ${GREEN}✅ Docker Compose installé${NC}"
else
    echo -e "  ${RED}❌ Docker Compose non trouvé${NC}"
    echo -e "  ${YELLOW}➡️  Installez Docker Compose${NC}"
    exit 1
fi

echo ""

# ==================================================
# 2. Environnement virtuel Python
# ==================================================

echo -e "${YELLOW}🐍 Configuration de l'environnement Python...${NC}"
echo ""

if [ -d "venv" ]; then
    echo -e "  ${YELLOW}⚠️  Environnement virtuel existant détecté${NC}"
    read -p "  Voulez-vous le recréer ? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo -e "  ${GREEN}✅ Environnement virtuel recréé${NC}"
    else
        echo -e "  ${BLUE}ℹ️  Conservation de l'environnement existant${NC}"
    fi
else
    python3 -m venv venv
    echo -e "  ${GREEN}✅ Environnement virtuel créé${NC}"
fi

# Activer l'environnement
source venv/bin/activate

# Mettre à jour pip
echo -e "  ${YELLOW}Mise à jour de pip...${NC}"
pip install --upgrade pip --quiet
echo -e "  ${GREEN}✅ Pip mis à jour${NC}"

# Installer les dépendances
echo -e "  ${YELLOW}Installation des dépendances (cela peut prendre 5-10 min)...${NC}"
pip install -r requirements.txt --quiet
echo -e "  ${GREEN}✅ Dépendances installées${NC}"

echo ""

# ==================================================
# 3. Structure des dossiers
# ==================================================

echo -e "${YELLOW}📁 Création de la structure de dossiers...${NC}"
echo ""

mkdir -p data/raw/invoices
mkdir -p data/label-studio
mkdir -p data/processed
mkdir -p data/exports
mkdir -p data/models/production
mkdir -p data/models/staging
mkdir -p data/models/archive
mkdir -p logs

echo -e "  ${GREEN}✅ Structure créée${NC}"
echo ""

# ==================================================
# 4. Configuration
# ==================================================

echo -e "${YELLOW}⚙️  Configuration...${NC}"
echo ""

if [ ! -f "config/settings.yaml" ]; then
    cp config/settings.example.yaml config/settings.yaml
    echo -e "  ${GREEN}✅ Fichier de configuration créé${NC}"
    echo -e "  ${YELLOW}⚠️  N'oubliez pas de configurer config/settings.yaml avec votre API key !${NC}"
else
    echo -e "  ${BLUE}ℹ️  Configuration existante conservée${NC}"
fi

echo ""

# ==================================================
# 5. Label Studio
# ==================================================

echo -e "${YELLOW}🐳 Démarrage de Label Studio...${NC}"
echo ""

# Vérifier si Docker est lancé
if ! docker info &> /dev/null; then
    echo -e "  ${RED}❌ Docker n'est pas démarré${NC}"
    echo -e "  ${YELLOW}➡️  Lancez Docker Desktop et réessayez${NC}"
    exit 1
fi

# Démarrer Label Studio
docker-compose up -d

# Attendre que Label Studio soit prêt
echo -e "  ${YELLOW}Attente du démarrage de Label Studio...${NC}"
sleep 5

# Vérifier
if docker ps | grep -q "label-studio"; then
    echo -e "  ${GREEN}✅ Label Studio démarré${NC}"
    echo -e "  ${BLUE}➡️  Accessible sur http://localhost:8080${NC}"
else
    echo -e "  ${RED}❌ Erreur au démarrage de Label Studio${NC}"
    docker-compose logs label-studio
    exit 1
fi

echo ""

# ==================================================
# 6. Résumé
# ==================================================

echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                       ║${NC}"
echo -e "${GREEN}║              ✨ Installation terminée ! ✨             ║${NC}"
echo -e "${GREEN}║                                                       ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}📋 Récapitulatif :${NC}"
echo ""
echo -e "  ${GREEN}✅${NC} Python et environnement virtuel configurés"
echo -e "  ${GREEN}✅${NC} Dépendances installées"
echo -e "  ${GREEN}✅${NC} Structure de dossiers créée"
echo -e "  ${GREEN}✅${NC} Label Studio démarré"
echo ""

echo -e "${BLUE}🚀 Prochaines étapes :${NC}"
echo ""
echo -e "  1️⃣  Configurer Label Studio"
echo -e "      ${YELLOW}→ Ouvrir http://localhost:8080${NC}"
echo -e "      ${YELLOW}→ Créer un compte${NC}"
echo -e "      ${YELLOW}→ Créer un projet 'Factures'${NC}"
echo -e "      ${YELLOW}→ Récupérer votre API key${NC}"
echo ""
echo -e "  2️⃣  Éditer la configuration"
echo -e "      ${YELLOW}→ nano config/settings.yaml${NC}"
echo -e "      ${YELLOW}→ Ajouter votre API key et project_id${NC}"
echo ""
echo -e "  3️⃣  Importer vos factures"
echo -e "      ${YELLOW}→ Copier vos PDFs dans data/raw/invoices/${NC}"
echo -e "      ${YELLOW}→ python scripts/import_to_label_studio.py${NC}"
echo ""
echo -e "  4️⃣  Commencer l'annotation !"
echo -e "      ${YELLOW}→ http://localhost:8080${NC}"
echo ""

echo -e "${BLUE}📚 Documentation :${NC}"
echo -e "  ${YELLOW}→ README.md         : Vue d'ensemble${NC}"
echo -e "  ${YELLOW}→ QUICKSTART.md     : Démarrage rapide${NC}"
echo -e "  ${YELLOW}→ docs/phase0-setup.md : Guide détaillé${NC}"
echo ""

echo -e "${GREEN}Bon courage pour votre projet ! 🎉${NC}"
echo ""

# ==================================================
# Afficher comment activer l'environnement
# ==================================================

echo -e "${YELLOW}💡 Pour activer l'environnement Python plus tard :${NC}"
echo -e "   ${BLUE}source venv/bin/activate${NC}"
echo ""
