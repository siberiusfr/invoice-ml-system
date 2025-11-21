#!/usr/bin/env python3
"""
Entraîner un modèle YOLO pour la détection de champs de factures

Usage:
    python training/train_yolo.py
    python training/train_yolo.py --epochs 200 --batch 32
"""

import os
import yaml
import argparse
from pathlib import Path
from datetime import datetime
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


def check_dataset(data_yaml_path: Path):
    """Vérifier que le dataset existe"""
    if not data_yaml_path.exists():
        print(f"{Colors.RED}❌ Fichier de données non trouvé: {data_yaml_path}{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Exécutez d'abord: python scripts/prepare_dataset.py{Colors.RESET}")
        exit(1)

    # Vérifier la structure
    with open(data_yaml_path, 'r') as f:
        data_config = yaml.safe_load(f)

    dataset_path = Path(data_config['path'])
    train_path = dataset_path / data_config['train']
    val_path = dataset_path / data_config['val']

    if not train_path.exists():
        print(f"{Colors.RED}❌ Dossier train non trouvé: {train_path}{Colors.RESET}")
        exit(1)

    if not val_path.exists():
        print(f"{Colors.RED}❌ Dossier val non trouvé: {val_path}{Colors.RESET}")
        exit(1)

    # Compter les images
    n_train = len(list(train_path.glob('*')))
    n_val = len(list(val_path.glob('*')))

    print(f"{Colors.GREEN}✅ Dataset trouvé:{Colors.RESET}")
    print(f"   Train: {n_train} images")
    print(f"   Val:   {n_val} images")
    print(f"   Classes: {data_config['nc']}")
    print()

    return n_train, n_val


def train_yolo(config: dict, args):
    """Entraîner le modèle YOLO"""

    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}🤖 ENTRAÎNEMENT DU MODÈLE YOLO{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

    # Vérifier le GPU
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"{Colors.YELLOW}🖥️  Device: {device}{Colors.RESET}")
    if device == 'cpu':
        print(f"{Colors.YELLOW}⚠️  Pas de GPU détecté. L'entraînement sera lent.{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Utilisez Google Colab pour un GPU gratuit{Colors.RESET}")
    print()

    # Trouver le fichier data.yaml
    dataset_root = Path(config['dataset']['processed_data_path']) / 'yolo_dataset'
    data_yaml = dataset_root / 'data.yaml'

    # Vérifier le dataset
    n_train, n_val = check_dataset(data_yaml)

    if n_train < 50:
        print(f"{Colors.YELLOW}⚠️  Seulement {n_train} images d'entraînement !{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Recommandation: au moins 100 images pour de bons résultats{Colors.RESET}\n")

    # Paramètres d'entraînement
    yolo_config = config['training']['yolo']
    model_name = args.model or yolo_config['model']
    epochs = args.epochs or yolo_config['epochs']
    batch = args.batch or yolo_config['batch_size']
    imgsz = args.imgsz or yolo_config['img_size']
    patience = yolo_config['patience']

    print(f"{Colors.YELLOW}⚙️  Paramètres d'entraînement:{Colors.RESET}")
    print(f"   Modèle de base: {model_name}")
    print(f"   Epochs: {epochs}")
    print(f"   Batch size: {batch}")
    print(f"   Image size: {imgsz}")
    print(f"   Patience (early stopping): {patience}")
    print()

    # Créer le dossier de sortie
    output_dir = Path('data/models')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Charger le modèle
    print(f"{Colors.YELLOW}📥 Chargement du modèle {model_name}...{Colors.RESET}")
    model = YOLO(model_name)
    print(f"{Colors.GREEN}✅ Modèle chargé{Colors.RESET}\n")

    # Lancer l'entraînement
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}🚀 DÉBUT DE L'ENTRAÎNEMENT{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    project_name = f"invoice_yolo_{timestamp}"

    results = model.train(
        data=str(data_yaml),
        epochs=epochs,
        batch=batch,
        imgsz=imgsz,
        patience=patience,
        device=device,
        project=str(output_dir),
        name=project_name,
        save=True,
        plots=True,
        verbose=True
    )

    # Résultats
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}✨ ENTRAÎNEMENT TERMINÉ !{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

    # Sauvegarder le meilleur modèle
    best_model_path = output_dir / project_name / 'weights' / 'best.pt'
    final_model_path = output_dir / f'invoice_model_{timestamp}.pt'

    if best_model_path.exists():
        import shutil
        shutil.copy2(best_model_path, final_model_path)
        print(f"{Colors.GREEN}✅ Meilleur modèle sauvegardé:{Colors.RESET}")
        print(f"   {final_model_path}\n")

    # Afficher les métriques
    print(f"{Colors.YELLOW}📊 Métriques finales:{Colors.RESET}")
    print(f"   Consultez les graphiques dans:")
    print(f"   {output_dir / project_name}\n")

    print(f"{Colors.GREEN}➡️  Prochaines étapes :{Colors.RESET}")
    print(f"   1. Évaluer le modèle: python training/evaluate.py")
    print(f"   2. Tester l'API: python api/app.py")
    print()

    return final_model_path


def main():
    """Main"""
    parser = argparse.ArgumentParser(description="Entraîner un modèle YOLO")
    parser.add_argument('--model', type=str, help='Modèle de base (yolov8n.pt, yolov8s.pt, etc.)')
    parser.add_argument('--epochs', type=int, help='Nombre d\'epochs')
    parser.add_argument('--batch', type=int, help='Batch size')
    parser.add_argument('--imgsz', type=int, help='Taille des images')
    args = parser.parse_args()

    config = load_config()
    train_yolo(config, args)


if __name__ == '__main__':
    main()
