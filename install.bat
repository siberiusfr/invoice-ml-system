@echo off
REM ==================================================
REM Script d'installation automatique pour Windows
REM Invoice ML System - Setup rapide
REM ==================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo.
echo        Invoice ML System - Installation Windows
echo.
echo ============================================================
echo.

REM ==================================================
REM 1. Verification des prerequis
REM ==================================================

echo [1/5] Verification des prerequis...
echo.

REM Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python non trouve
    echo    Installez Python 3.9+ depuis https://www.python.org
    pause
    exit /b 1
)
echo [OK] Python installe

REM Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Docker non trouve
    echo    Installez Docker Desktop depuis https://www.docker.com
    pause
    exit /b 1
)
echo [OK] Docker installe

REM Docker Compose
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Docker Compose non trouve
    pause
    exit /b 1
)
echo [OK] Docker Compose installe

echo.

REM ==================================================
REM 2. Environnement virtuel Python
REM ==================================================

echo [2/5] Configuration de l'environnement Python...
echo.

if exist venv (
    echo [!] Environnement virtuel existant detecte
    set /p RECREATE="    Voulez-vous le recreer ? (o/N) "
    if /i "!RECREATE!"=="o" (
        rmdir /s /q venv
        python -m venv venv
        echo [OK] Environnement virtuel recree
    ) else (
        echo [i] Conservation de l'environnement existant
    )
) else (
    python -m venv venv
    echo [OK] Environnement virtuel cree
)

REM Activer l'environnement
call venv\Scripts\activate.bat

REM Mettre a jour pip
echo    Mise a jour de pip...
python -m pip install --upgrade pip --quiet
echo [OK] Pip mis a jour

REM Installer les dependances
echo    Installation des dependances (5-10 min)...
pip install -r requirements.txt --quiet
echo [OK] Dependances installees

echo.

REM ==================================================
REM 3. Structure des dossiers
REM ==================================================

echo [3/5] Creation de la structure de dossiers...
echo.

if not exist data\raw\invoices mkdir data\raw\invoices
if not exist data\label-studio mkdir data\label-studio
if not exist data\processed mkdir data\processed
if not exist data\exports mkdir data\exports
if not exist data\models\production mkdir data\models\production
if not exist data\models\staging mkdir data\models\staging
if not exist data\models\archive mkdir data\models\archive
if not exist logs mkdir logs

echo [OK] Structure creee
echo.

REM ==================================================
REM 4. Configuration
REM ==================================================

echo [4/5] Configuration...
echo.

if not exist config\settings.yaml (
    copy config\settings.example.yaml config\settings.yaml >nul
    echo [OK] Fichier de configuration cree
    echo [!] N'oubliez pas de configurer config\settings.yaml !
) else (
    echo [i] Configuration existante conservee
)

echo.

REM ==================================================
REM 5. Label Studio
REM ==================================================

echo [5/5] Demarrage de Label Studio...
echo.

REM Verifier si Docker est lance
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Docker n'est pas demarre
    echo    Lancez Docker Desktop et reessayez
    pause
    exit /b 1
)

REM Demarrer Label Studio
docker-compose up -d

REM Attendre
echo    Attente du demarrage (10 secondes)...
timeout /t 10 /nobreak >nul

REM Verifier
docker ps | findstr "label-studio" >nul
if %errorlevel% equ 0 (
    echo [OK] Label Studio demarre
    echo [i] Accessible sur http://localhost:8080
) else (
    echo [X] Erreur au demarrage
    docker-compose logs label-studio
    pause
    exit /b 1
)

echo.

REM ==================================================
REM 6. Resume
REM ==================================================

echo ============================================================
echo.
echo            Installation terminee avec succes !
echo.
echo ============================================================
echo.

echo Prochaines etapes :
echo.
echo   1. Configurer Label Studio
echo      - Ouvrir http://localhost:8080
echo      - Creer un compte
echo      - Creer un projet 'Factures'
echo      - Recuperer votre API key
echo.
echo   2. Editer la configuration
echo      - Ouvrir config\settings.yaml
echo      - Ajouter votre API key et project_id
echo.
echo   3. Importer vos factures
echo      - Copier vos PDFs dans data\raw\invoices\
echo      - python scripts\import_to_label_studio.py
echo.
echo   4. Commencer l'annotation !
echo      - http://localhost:8080
echo.

echo Documentation :
echo   - README.md
echo   - QUICKSTART.md
echo   - docs\phase0-setup.md
echo.

echo Pour activer l'environnement Python plus tard :
echo   venv\Scripts\activate
echo.

pause
