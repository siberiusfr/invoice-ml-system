#!/usr/bin/env python3
"""
Script de test de l'API

Teste l'extraction de factures via l'API REST

Usage:
    python scripts/test_api.py
    python scripts/test_api.py --file path/to/invoice.pdf
"""

import requests
import argparse
import yaml
from pathlib import Path
import json

# Couleurs
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def load_config():
    """Charger la configuration"""
    config_path = Path(__file__).parent.parent / 'config' / 'settings.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def test_health(api_url: str):
    """Tester le health check"""
    print(f"{Colors.YELLOW}🏥 Test du health check...{Colors.RESET}")

    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        response.raise_for_status()

        data = response.json()
        print(f"{Colors.GREEN}✅ API opérationnelle{Colors.RESET}")
        print(f"   Status: {data.get('status')}")
        print(f"   Modèle chargé: {data.get('model_loaded')}")
        print(f"   Version: {data.get('model_version', 'N/A')}")
        return True

    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}❌ Impossible de se connecter à l'API{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Assurez-vous que l'API est lancée: python api/app.py{Colors.RESET}")
        return False
    except Exception as e:
        print(f"{Colors.RED}❌ Erreur: {e}{Colors.RESET}")
        return False


def test_extraction(api_url: str, file_path: Path):
    """Tester l'extraction d'une facture"""
    print(f"\n{Colors.YELLOW}🔍 Test d'extraction: {file_path.name}{Colors.RESET}")

    if not file_path.exists():
        print(f"{Colors.RED}❌ Fichier non trouvé: {file_path}{Colors.RESET}")
        return False

    try:
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f)}
            response = requests.post(f"{api_url}/extract", files=files, timeout=30)

        response.raise_for_status()
        data = response.json()

        if data.get('success'):
            print(f"{Colors.GREEN}✅ Extraction réussie !{Colors.RESET}\n")

            extraction = data.get('data', {})
            print(f"{Colors.BLUE}📊 Résultats:{Colors.RESET}")
            print(f"   Confiance globale: {extraction.get('overall_confidence', 0):.2%}")
            print(f"   Nécessite une revue: {extraction.get('needs_review', False)}")
            print(f"   Modèle utilisé: {extraction.get('model_version', 'N/A')}")

            fields = extraction.get('fields', [])
            print(f"\n{Colors.BLUE}   Champs extraits ({len(fields)}):{Colors.RESET}")

            for field in fields:
                print(f"      • {field['label']}: {field['value']} (confiance: {field['confidence']:.2%})")

            return True
        else:
            print(f"{Colors.RED}❌ Extraction échouée{Colors.RESET}")
            print(f"   Erreur: {data.get('error', 'Inconnue')}")
            print(f"   Message: {data.get('message', '')}")
            return False

    except Exception as e:
        print(f"{Colors.RED}❌ Erreur: {e}{Colors.RESET}")
        return False


def test_stats(api_url: str):
    """Tester les statistiques"""
    print(f"\n{Colors.YELLOW}📊 Test des statistiques...{Colors.RESET}")

    try:
        response = requests.get(f"{api_url}/stats", timeout=5)
        response.raise_for_status()

        data = response.json()
        print(f"{Colors.GREEN}✅ Statistiques récupérées{Colors.RESET}")
        print(f"   Total extractions: {data.get('total_extractions', 0)}")
        print(f"   Confiance moyenne: {data.get('average_confidence', 0):.2%}")
        print(f"   Taux de succès: {data.get('success_rate', 0):.2%}")
        return True

    except Exception as e:
        print(f"{Colors.RED}❌ Erreur: {e}{Colors.RESET}")
        return False


def main():
    """Main"""
    parser = argparse.ArgumentParser(description="Tester l'API d'extraction")
    parser.add_argument('--file', type=str, help='Fichier de facture à tester')
    parser.add_argument('--api', type=str, help='URL de l\'API (défaut depuis config)')
    args = parser.parse_args()

    config = load_config()
    api_url = args.api or f"http://{config['api']['host']}:{config['api']['port']}"

    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}🧪 TEST DE L'API{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    print(f"API: {api_url}\n")

    # Test 1: Health check
    if not test_health(api_url):
        return

    # Test 2: Statistiques
    test_stats(api_url)

    # Test 3: Extraction (si fichier fourni)
    if args.file:
        file_path = Path(args.file)
        test_extraction(api_url, file_path)
    else:
        # Essayer avec un fichier de test par défaut
        test_files_dir = Path('data/raw/invoices')
        if test_files_dir.exists():
            test_files = list(test_files_dir.glob('*'))
            if test_files:
                print(f"\n{Colors.YELLOW}💡 Aucun fichier spécifié, test avec: {test_files[0].name}{Colors.RESET}")
                test_extraction(api_url, test_files[0])
            else:
                print(f"\n{Colors.YELLOW}💡 Aucun fichier de test trouvé dans data/raw/invoices/{Colors.RESET}")
                print(f"{Colors.YELLOW}   Utilisez: python scripts/test_api.py --file path/to/invoice.pdf{Colors.RESET}")

    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}\n")


if __name__ == '__main__':
    main()
