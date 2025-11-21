#!/usr/bin/env python3
"""
Évaluer un modèle YOLO entraîné

Usage:
    python training/evaluate.py
    python training/evaluate.py --model data/models/invoice_model_20240101.pt
"""

import os
import yaml
import argparse
from pathlib import Path
import torch
from ultralytics import YOLO

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


def find_latest_model(models_dir: Path) -> Path:
    """Trouver le dernier modèle entraîné"""
    model_files = list(models_dir.glob('invoice_model_*.pt'))
    if not model_files:
        raise FileNotFoundError("Aucun modèle trouvé. Entraînez d'abord un modèle.")
    return max(model_files, key=os.path.getctime)


def evaluate_model(config: dict, model_path: Path):
    """Évaluer le modèle"""

    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}📊 ÉVALUATION DU MODÈLE{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

    # Vérifier que le modèle existe
    if not model_path.exists():
        print(f"{Colors.RED}❌ Modèle non trouvé: {model_path}{Colors.RESET}")
        exit(1)

    print(f"{Colors.YELLOW}📦 Modèle: {model_path.name}{Colors.RESET}\n")

    # Charger le modèle
    print(f"{Colors.YELLOW}📥 Chargement du modèle...{Colors.RESET}")
    model = YOLO(str(model_path))
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"{Colors.GREEN}✅ Modèle chargé (device: {device}){Colors.RESET}\n")

    # Trouver le fichier data.yaml
    dataset_root = Path(config['dataset']['processed_data_path']) / 'yolo_dataset'
    data_yaml = dataset_root / 'data.yaml'

    if not data_yaml.exists():
        print(f"{Colors.RED}❌ Dataset non trouvé: {data_yaml}{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Exécutez d'abord: python scripts/prepare_dataset.py{Colors.RESET}")
        exit(1)

    # Évaluation sur le set de test
    print(f"{Colors.YELLOW}🔍 Évaluation sur le set de test...{Colors.RESET}\n")

    results = model.val(
        data=str(data_yaml),
        split='test',
        device=device,
        plots=True
    )

    # Afficher les résultats
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}📊 RÉSULTATS{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

    # Métriques principales
    metrics = results.results_dict

    print(f"{Colors.YELLOW}Métriques globales:{Colors.RESET}")
    print(f"   Precision:    {metrics.get('metrics/precision(B)', 0):.3f}")
    print(f"   Recall:       {metrics.get('metrics/recall(B)', 0):.3f}")
    print(f"   mAP@0.5:      {metrics.get('metrics/mAP50(B)', 0):.3f}")
    print(f"   mAP@0.5:0.95: {metrics.get('metrics/mAP50-95(B)', 0):.3f}")
    print()

    # Interprétation
    map50 = metrics.get('metrics/mAP50(B)', 0)

    print(f"{Colors.YELLOW}💡 Interprétation:{Colors.RESET}")
    if map50 >= 0.8:
        print(f"{Colors.GREEN}   ✅ Excellent modèle ! (mAP50 >= 0.8){Colors.RESET}")
    elif map50 >= 0.6:
        print(f"{Colors.YELLOW}   ⚠️  Modèle correct (mAP50 >= 0.6){Colors.RESET}")
        print(f"{Colors.YELLOW}   💡 Annotez plus de factures pour améliorer{Colors.RESET}")
    else:
        print(f"{Colors.RED}   ❌ Modèle insuffisant (mAP50 < 0.6){Colors.RESET}")
        print(f"{Colors.RED}   💡 Besoin de plus de données ou ajustement des paramètres{Colors.RESET}")

    print()
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

    # Prochaines étapes
    print(f"{Colors.GREEN}➡️  Prochaines étapes :{Colors.RESET}")
    if map50 >= 0.6:
        print(f"   1. Tester l'API: python api/app.py")
        print(f"   2. Faire des prédictions de test")
    else:
        print(f"   1. Annoter plus de factures")
        print(f"   2. Réentraîner avec plus de données")
    print()


def main():
    """Main"""
    parser = argparse.ArgumentParser(description="Évaluer un modèle YOLO")
    parser.add_argument(
        '--model',
        type=str,
        help='Chemin vers le modèle (optionnel, prend le plus récent par défaut)'
    )
    args = parser.parse_args()

    config = load_config()

    # Trouver le modèle
    if args.model:
        model_path = Path(args.model)
    else:
        models_dir = Path('data/models')
        model_path = find_latest_model(models_dir)

    evaluate_model(config, model_path)


if __name__ == '__main__':
    main()
