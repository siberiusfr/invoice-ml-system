#!/usr/bin/env python3
"""
Script de vérification des dépendances du système Invoice ML
"""
import sys
import subprocess
from colorama import init, Fore, Style

init(autoreset=True)


def print_header(text):
    """Afficher un en-tête"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}{text.center(60)}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")


def check_python_packages():
    """Vérifier les packages Python"""
    print(f"{Fore.YELLOW}📦 Vérification des packages Python...{Style.RESET_ALL}")

    required_packages = [
        'torch',
        'ultralytics',
        'transformers',
        'opencv-python',
        'pytesseract',
        'fastapi',
        'uvicorn',
        'label-studio-sdk',
        'numpy',
        'pandas',
        'pyyaml'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n{Fore.RED}⚠️  Packages manquants : {', '.join(missing_packages)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Installer avec : pip install -r requirements.txt{Style.RESET_ALL}")
        return False
    else:
        print(f"\n{Fore.GREEN}✅ Tous les packages Python sont installés{Style.RESET_ALL}")
        return True


def check_tesseract():
    """Vérifier l'installation de Tesseract"""
    print(f"\n{Fore.YELLOW}🔍 Vérification de Tesseract OCR...{Style.RESET_ALL}")

    try:
        result = subprocess.run(['tesseract', '--version'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"  ✅ Tesseract installé : {version_line}")

            # Vérifier les langues
            result_langs = subprocess.run(['tesseract', '--list-langs'],
                                        capture_output=True, text=True, timeout=5)
            langs = result_langs.stdout.strip().split('\n')[1:]  # Skip header

            required_langs = ['fra', 'eng']
            missing_langs = [lang for lang in required_langs if lang not in langs]

            if missing_langs:
                print(f"  ⚠️  Langues manquantes : {', '.join(missing_langs)}")
                print(f"  💡 Voir : docs/tesseract-installation.md")
                return False
            else:
                print(f"  ✅ Langues disponibles : {', '.join(required_langs)}")
                return True
        else:
            print(f"  ❌ Tesseract trouvé mais erreur lors de l'exécution")
            return False

    except FileNotFoundError:
        print(f"  ❌ Tesseract n'est pas installé")
        print(f"\n{Fore.RED}⚠️  Tesseract OCR est requis pour l'extraction de texte{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}📖 Guide d'installation : docs/tesseract-installation.md{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Installation rapide :{Style.RESET_ALL}")
        print(f"  • Windows : Télécharger depuis https://github.com/UB-Mannheim/tesseract/wiki")
        print(f"  • macOS   : brew install tesseract tesseract-lang")
        print(f"  • Linux   : sudo apt-get install tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng")
        return False
    except subprocess.TimeoutExpired:
        print(f"  ❌ Timeout lors de la vérification de Tesseract")
        return False


def check_docker():
    """Vérifier l'installation de Docker"""
    print(f"\n{Fore.YELLOW}🐳 Vérification de Docker...{Style.RESET_ALL}")

    try:
        result = subprocess.run(['docker', '--version'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_line = result.stdout.strip()
            print(f"  ✅ Docker installé : {version_line}")

            # Vérifier que Docker daemon tourne
            result_ps = subprocess.run(['docker', 'ps'],
                                      capture_output=True, text=True, timeout=5)
            if result_ps.returncode == 0:
                print(f"  ✅ Docker daemon actif")
                return True
            else:
                print(f"  ⚠️  Docker installé mais daemon non actif")
                print(f"  💡 Lancer Docker Desktop ou démarrer le daemon")
                return False
        else:
            print(f"  ❌ Docker trouvé mais erreur lors de l'exécution")
            return False

    except FileNotFoundError:
        print(f"  ❌ Docker n'est pas installé")
        print(f"\n{Fore.YELLOW}💡 Docker est requis pour Label Studio{Style.RESET_ALL}")
        print(f"📥 Télécharger : https://www.docker.com/products/docker-desktop/")
        return False
    except subprocess.TimeoutExpired:
        print(f"  ❌ Timeout lors de la vérification de Docker")
        return False


def check_gpu():
    """Vérifier la disponibilité du GPU"""
    print(f"\n{Fore.YELLOW}🎮 Vérification du GPU...{Style.RESET_ALL}")

    try:
        import torch

        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_count = torch.cuda.device_count()
            print(f"  ✅ GPU CUDA disponible : {gpu_name}")
            print(f"  ℹ️  Nombre de GPU : {gpu_count}")
            return True
        else:
            print(f"  ⚠️  Aucun GPU CUDA détecté")
            print(f"  ℹ️  L'entraînement utilisera le CPU (plus lent)")
            print(f"  💡 Utiliser Google Colab pour entraîner avec GPU gratuit")
            print(f"     Voir : notebooks/train_yolo_colab.ipynb")
            return False

    except ImportError:
        print(f"  ❌ PyTorch non installé, impossible de vérifier le GPU")
        return False


def check_directories():
    """Vérifier la structure des dossiers"""
    print(f"\n{Fore.YELLOW}📁 Vérification de la structure des dossiers...{Style.RESET_ALL}")

    from pathlib import Path

    required_dirs = [
        'data/raw/invoices',
        'data/exports',
        'data/processed',
        'data/models',
        'data/label-studio',
        'data/logs',
        'config',
        'api',
        'training',
        'scripts',
        'monitoring',
        'tests'
    ]

    missing_dirs = []

    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ⚠️  {dir_path} (sera créé automatiquement)")
            missing_dirs.append(dir_path)

    if missing_dirs:
        print(f"\n{Fore.YELLOW}💡 Certains dossiers seront créés automatiquement lors de l'utilisation{Style.RESET_ALL}")

    return True


def check_config():
    """Vérifier la configuration"""
    print(f"\n{Fore.YELLOW}⚙️  Vérification de la configuration...{Style.RESET_ALL}")

    from pathlib import Path

    config_file = Path('config/settings.yaml')
    example_file = Path('config/settings.example.yaml')

    if config_file.exists():
        print(f"  ✅ config/settings.yaml existe")
        return True
    elif example_file.exists():
        print(f"  ⚠️  config/settings.yaml n'existe pas")
        print(f"  💡 Copier depuis l'exemple :")
        print(f"     cp config/settings.example.yaml config/settings.yaml")
        return False
    else:
        print(f"  ❌ Aucun fichier de configuration trouvé")
        return False


def main():
    """Fonction principale"""
    print_header("🔍 VÉRIFICATION DES DÉPENDANCES")
    print(f"{Fore.CYAN}Invoice ML System - Dependency Checker{Style.RESET_ALL}\n")

    results = {
        'Python Packages': check_python_packages(),
        'Tesseract OCR': check_tesseract(),
        'Docker': check_docker(),
        'GPU': check_gpu(),
        'Directories': check_directories(),
        'Config': check_config()
    }

    print_header("📊 RÉSUMÉ")

    for component, status in results.items():
        status_icon = "✅" if status else "❌"
        color = Fore.GREEN if status else Fore.RED
        print(f"{color}{status_icon} {component}{Style.RESET_ALL}")

    critical_checks = ['Python Packages', 'Tesseract OCR', 'Docker']
    critical_passed = all(results[check] for check in critical_checks if check in results)

    print()

    if critical_passed:
        print(f"{Fore.GREEN}{'='*60}")
        print(f"{Fore.GREEN}✅ Système prêt ! Vous pouvez commencer.{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}🚀 Prochaines étapes :{Style.RESET_ALL}")
        print(f"  1. Lancer Label Studio : make label-studio-start")
        print(f"  2. Lire la doc : README.md")
        print(f"  3. Importer des factures : python scripts/import_to_label_studio.py")
        return 0
    else:
        print(f"{Fore.RED}{'='*60}")
        print(f"{Fore.RED}⚠️  Configuration incomplète{Style.RESET_ALL}")
        print(f"{Fore.RED}{'='*60}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}💡 Veuillez installer les composants manquants.{Style.RESET_ALL}")
        print(f"   Voir la documentation : docs/")
        return 1


if __name__ == "__main__":
    sys.exit(main())
