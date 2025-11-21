#!/usr/bin/env python3
"""
Script de réentraînement automatique

Vérifie s'il y a assez de nouvelles annotations et réentraîne le modèle automatiquement.

Usage:
    python scripts/auto_retrain.py
    python scripts/auto_retrain.py --dry-run  # Test sans réentraîner
"""

import os
import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime
import subprocess

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


def get_latest_export() -> dict:
    """Récupérer le dernier export d'annotations"""
    exports_dir = Path('data/exports')
    if not exports_dir.exists():
        return None

    export_files = list(exports_dir.glob('annotations_*.json'))
    if not export_files:
        return None

    latest_export = max(export_files, key=os.path.getctime)
    with open(latest_export, 'r') as f:
        return json.load(f)


def get_last_training_info() -> dict:
    """Récupérer les informations du dernier entraînement"""
    training_log = Path('data/models/training_log.json')

    if not training_log.exists():
        return {
            'last_training_date': None,
            'samples_used': 0,
            'model_path': None
        }

    with open(training_log, 'r') as f:
        return json.load(f)


def save_training_info(samples_count: int, model_path: str):
    """Sauvegarder les informations d'entraînement"""
    training_log = Path('data/models/training_log.json')
    training_log.parent.mkdir(parents=True, exist_ok=True)

    info = {
        'last_training_date': datetime.now().isoformat(),
        'samples_used': samples_count,
        'model_path': model_path
    }

    with open(training_log, 'w') as f:
        json.dump(info, f, indent=2)


def check_if_retrain_needed(config: dict) -> tuple:
    """
    Vérifier si un réentraînement est nécessaire

    Returns:
        (needs_retrain, reason, new_samples_count)
    """
    # Récupérer les données actuelles
    export_data = get_latest_export()
    if not export_data:
        return False, "Aucun export d'annotations trouvé", 0

    current_samples = export_data.get('completed_tasks', 0)

    # Récupérer les infos du dernier entraînement
    last_training = get_last_training_info()
    previous_samples = last_training.get('samples_used', 0)

    # Calculer les nouvelles annotations
    new_samples = current_samples - previous_samples

    # Seuil minimum
    min_new_samples = config['training']['min_new_samples']

    if new_samples >= min_new_samples:
        return True, f"{new_samples} nouvelles annotations (seuil: {min_new_samples})", new_samples
    else:
        return False, f"Seulement {new_samples} nouvelles annotations (seuil: {min_new_samples})", new_samples


def run_training_pipeline(config: dict, dry_run: bool = False):
    """Exécuter le pipeline complet d'entraînement"""

    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}🔄 RÉENTRAÎNEMENT AUTOMATIQUE{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

    if dry_run:
        print(f"{Colors.YELLOW}🧪 MODE TEST (dry-run) - Aucun entraînement ne sera effectué{Colors.RESET}\n")

    # Vérifier si un réentraînement est nécessaire
    needs_retrain, reason, new_samples = check_if_retrain_needed(config)

    print(f"{Colors.YELLOW}📊 État actuel:{Colors.RESET}")
    print(f"   {reason}\n")

    if not needs_retrain:
        print(f"{Colors.YELLOW}⏸️  Réentraînement non nécessaire pour le moment{Colors.RESET}\n")
        return

    print(f"{Colors.GREEN}✅ Réentraînement nécessaire !{Colors.RESET}\n")

    if dry_run:
        print(f"{Colors.YELLOW}Mode test activé - Les étapes suivantes seraient exécutées:{Colors.RESET}")
        print(f"   1. Export depuis Label Studio")
        print(f"   2. Préparation du dataset")
        print(f"   3. Entraînement du modèle")
        print(f"   4. Évaluation")
        print(f"   5. Sauvegarde des informations")
        return

    # Étape 1: Exporter depuis Label Studio
    print(f"{Colors.YELLOW}📤 Étape 1/4: Export depuis Label Studio...{Colors.RESET}")
    try:
        result = subprocess.run(
            ['python', 'scripts/export_from_label_studio.py'],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"{Colors.GREEN}✅ Export terminé{Colors.RESET}\n")
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ Erreur lors de l'export: {e}{Colors.RESET}")
        return

    # Étape 2: Préparer le dataset
    print(f"{Colors.YELLOW}📦 Étape 2/4: Préparation du dataset...{Colors.RESET}")
    try:
        result = subprocess.run(
            ['python', 'scripts/prepare_dataset.py'],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"{Colors.GREEN}✅ Dataset préparé{Colors.RESET}\n")
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ Erreur lors de la préparation: {e}{Colors.RESET}")
        return

    # Étape 3: Entraîner le modèle
    print(f"{Colors.YELLOW}🤖 Étape 3/4: Entraînement du modèle...{Colors.RESET}")
    try:
        result = subprocess.run(
            ['python', 'training/train_yolo.py'],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"{Colors.GREEN}✅ Entraînement terminé{Colors.RESET}\n")
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ Erreur lors de l'entraînement: {e}{Colors.RESET}")
        return

    # Étape 4: Évaluer le modèle
    print(f"{Colors.YELLOW}📊 Étape 4/4: Évaluation du modèle...{Colors.RESET}")
    try:
        result = subprocess.run(
            ['python', 'training/evaluate.py'],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"{Colors.GREEN}✅ Évaluation terminée{Colors.RESET}\n")
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}❌ Erreur lors de l'évaluation: {e}{Colors.RESET}")
        # Continuer même si l'évaluation échoue

    # Sauvegarder les informations
    export_data = get_latest_export()
    save_training_info(
        samples_count=export_data.get('completed_tasks', 0),
        model_path="data/models/latest"
    )

    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.GREEN}✨ Réentraînement terminé avec succès !{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")


def main():
    """Main"""
    parser = argparse.ArgumentParser(description="Réentraînement automatique")
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Mode test - vérifie sans réentraîner'
    )
    args = parser.parse_args()

    config = load_config()

    if not config['auto_retrain']['enabled'] and not args.dry_run:
        print(f"{Colors.YELLOW}⚠️  Réentraînement automatique désactivé dans la configuration{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Activez-le dans config/settings.yaml ou utilisez --dry-run{Colors.RESET}")
        return

    run_training_pipeline(config, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
