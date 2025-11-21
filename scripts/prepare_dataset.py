#!/usr/bin/env python3
"""
Préparer le dataset pour l'entraînement YOLO

Ce script convertit les annotations Label Studio au format YOLO
et crée les splits train/val/test.

Usage:
    python scripts/prepare_dataset.py
    python scripts/prepare_dataset.py --input exports/annotations_20240101.json
"""

import os
import json
import yaml
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import random
from tqdm import tqdm

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


def find_latest_export(exports_dir: Path) -> Path:
    """Trouver le dernier fichier d'export"""
    export_files = list(exports_dir.glob('annotations_*.json'))
    if not export_files:
        raise FileNotFoundError(f"Aucun fichier d'export trouvé dans {exports_dir}")
    return max(export_files, key=os.path.getctime)


def convert_label_studio_to_yolo(annotation: dict, label_map: Dict[str, int], img_width: int, img_height: int) -> List[str]:
    """
    Convertir une annotation Label Studio au format YOLO

    Format YOLO: <class_id> <x_center> <y_center> <width> <height>
    Toutes les valeurs sont normalisées (0-1)
    """
    yolo_annotations = []

    for result in annotation.get('result', []):
        if 'value' not in result:
            continue

        value = result['value']

        # Vérifier que c'est une annotation de type rectangle
        if 'rectanglelabels' not in value:
            continue

        # Coordonnées Label Studio (en pourcentage)
        x = value['x'] / 100.0  # Déjà en pourcentage
        y = value['y'] / 100.0
        width = value['width'] / 100.0
        height = value['height'] / 100.0

        # Convertir en format YOLO (centre + dimensions)
        x_center = x + width / 2
        y_center = y + height / 2

        # Label
        for label in value['rectanglelabels']:
            if label in label_map:
                class_id = label_map[label]
                yolo_line = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
                yolo_annotations.append(yolo_line)

    return yolo_annotations


def prepare_yolo_dataset(config: dict, export_file: Path):
    """Préparer le dataset complet pour YOLO"""

    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}📦 PRÉPARATION DU DATASET YOLO{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

    # Charger les annotations
    print(f"{Colors.YELLOW}📥 Chargement des annotations...{Colors.RESET}")
    with open(export_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    tasks = data['tasks']
    print(f"{Colors.GREEN}✅ {len(tasks)} factures annotées chargées{Colors.RESET}\n")

    # Créer le mapping des labels
    labels = config['labels']
    label_map = {label: idx for idx, label in enumerate(labels)}

    print(f"{Colors.YELLOW}🏷️  Labels détectés:{Colors.RESET}")
    for label, idx in label_map.items():
        print(f"   {idx}: {label}")
    print()

    # Créer la structure de dossiers YOLO
    dataset_root = Path(config['dataset']['processed_data_path']) / 'yolo_dataset'
    dataset_root.mkdir(parents=True, exist_ok=True)

    for split in ['train', 'val', 'test']:
        (dataset_root / split / 'images').mkdir(parents=True, exist_ok=True)
        (dataset_root / split / 'labels').mkdir(parents=True, exist_ok=True)

    # Split des données
    random.shuffle(tasks)
    n_tasks = len(tasks)

    split_ratios = config['dataset']['split_ratios']
    n_train = int(n_tasks * split_ratios['train'])
    n_val = int(n_tasks * split_ratios['val'])

    train_tasks = tasks[:n_train]
    val_tasks = tasks[n_train:n_train + n_val]
    test_tasks = tasks[n_train + n_val:]

    print(f"{Colors.YELLOW}📊 Répartition des données:{Colors.RESET}")
    print(f"   Train: {len(train_tasks)} factures ({split_ratios['train']*100:.0f}%)")
    print(f"   Val:   {len(val_tasks)} factures ({split_ratios['val']*100:.0f}%)")
    print(f"   Test:  {len(test_tasks)} factures ({split_ratios['test']*100:.0f}%)")
    print()

    # Traiter chaque split
    for split_name, split_tasks in [('train', train_tasks), ('val', val_tasks), ('test', test_tasks)]:
        print(f"{Colors.YELLOW}🔄 Traitement du split '{split_name}'...{Colors.RESET}")

        for task in tqdm(split_tasks, desc=f"  {split_name}", unit="facture"):
            # Récupérer le chemin de l'image originale
            filename = task['data'].get('filename')
            if not filename:
                continue

            # Chercher l'image
            original_path = Path(config['dataset']['raw_data_path']) / filename
            if not original_path.exists():
                continue

            # Copier l'image
            img_dest = dataset_root / split_name / 'images' / filename
            shutil.copy2(original_path, img_dest)

            # Convertir les annotations
            # TODO: Récupérer les vraies dimensions de l'image
            img_width, img_height = 1000, 1000  # Placeholder

            yolo_annotations = []
            for annotation in task.get('annotations', []):
                yolo_lines = convert_label_studio_to_yolo(
                    annotation, label_map, img_width, img_height
                )
                yolo_annotations.extend(yolo_lines)

            # Sauvegarder les annotations
            label_file = dataset_root / split_name / 'labels' / f"{Path(filename).stem}.txt"
            with open(label_file, 'w') as f:
                f.write('\n'.join(yolo_annotations))

    # Créer le fichier data.yaml pour YOLO
    data_yaml = {
        'path': str(dataset_root.absolute()),
        'train': 'train/images',
        'val': 'val/images',
        'test': 'test/images',
        'nc': len(labels),
        'names': labels
    }

    yaml_path = dataset_root / 'data.yaml'
    with open(yaml_path, 'w') as f:
        yaml.dump(data_yaml, f, default_flow_style=False)

    print(f"\n{Colors.GREEN}✅ Fichier de configuration YOLO créé: {yaml_path}{Colors.RESET}")

    # Résumé
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}✨ DATASET PRÊT !{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"  Emplacement: {dataset_root}")
    print(f"  Fichier de config: {yaml_path}")
    print(f"  Nombre de classes: {len(labels)}")
    print(f"  Total d'images: {len(tasks)}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

    print(f"{Colors.GREEN}➡️  Prochaine étape :{Colors.RESET}")
    print(f"    python training/train_yolo.py\n")

    return dataset_root


def main():
    """Main"""
    parser = argparse.ArgumentParser(description="Préparer le dataset YOLO")
    parser.add_argument(
        '--input',
        type=str,
        help="Fichier d'export JSON (optionnel, prend le plus récent par défaut)"
    )
    args = parser.parse_args()

    # Charger la config
    config = load_config()

    # Trouver le fichier d'export
    if args.input:
        export_file = Path(args.input)
    else:
        exports_dir = Path(config['dataset']['processed_data_path']).parent / 'exports'
        export_file = find_latest_export(exports_dir)

    print(f"{Colors.YELLOW}📄 Utilisation de: {export_file}{Colors.RESET}")

    # Préparer le dataset
    prepare_yolo_dataset(config, export_file)


if __name__ == '__main__':
    main()
