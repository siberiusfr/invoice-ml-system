#!/usr/bin/env python3
"""
Script d'export des annotations depuis Label Studio

Exporte toutes les factures annotées depuis Label Studio
pour préparer l'entraînement du modèle.

Usage:
    python scripts/export_from_label_studio.py
"""

import os
import json
import yaml
from pathlib import Path
from datetime import datetime
from label_studio_sdk import LabelStudio

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
    
    if not config_path.exists():
        print(f"{Colors.RED}❌ Fichier de configuration non trouvé !{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Copiez settings.example.yaml vers settings.yaml{Colors.RESET}")
        exit(1)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def export_annotations(config):
    """Exporter les annotations depuis Label Studio"""
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}📤 EXPORT DES ANNOTATIONS{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    # Connexion
    print(f"{Colors.YELLOW}📡 Connexion à Label Studio...{Colors.RESET}")
    try:
        client = LabelStudio(
            base_url=config['label_studio']['url'],
            api_key=config['label_studio']['api_key']
        )
        print(f"{Colors.GREEN}✅ Connecté !{Colors.RESET}\n")
    except Exception as e:
        print(f"{Colors.RED}❌ Erreur de connexion : {e}{Colors.RESET}")
        exit(1)

    # Récupérer le projet
    try:
        project = client.projects.get(id=config['label_studio']['project_id'])
        print(f"{Colors.GREEN}📁 Projet : {project.title}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}❌ Projet non trouvé : {e}{Colors.RESET}")
        exit(1)

    # Récupérer les tâches
    print(f"{Colors.YELLOW}🔍 Récupération des tâches...{Colors.RESET}")
    tasks_obj = client.tasks.list(project=project.id)
    # Convertir les objets Task en dictionnaires pour compatibilité
    tasks = [task.model_dump() if hasattr(task, 'model_dump') else task.dict() for task in tasks_obj]
    
    # Filtrer les tâches complètes (annotées)
    completed_tasks = [t for t in tasks if t.get('annotations')]
    
    print(f"  Total de tâches : {len(tasks)}")
    print(f"  Annotées : {len(completed_tasks)}")
    print(f"  Non annotées : {len(tasks) - len(completed_tasks)}\n")
    
    if len(completed_tasks) == 0:
        print(f"{Colors.YELLOW}⚠️  Aucune facture annotée trouvée !{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Annotez au moins quelques factures avant d'exporter{Colors.RESET}")
        exit(0)
    
    if len(completed_tasks) < 50:
        print(f"{Colors.YELLOW}⚠️  Seulement {len(completed_tasks)} factures annotées{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Recommandation : annotez au moins 100 factures pour de bons résultats{Colors.RESET}\n")
    
    # Créer le dossier d'export
    export_dir = Path(config['dataset']['processed_data_path']).parent / 'exports'
    export_dir.mkdir(parents=True, exist_ok=True)
    
    # Nom du fichier avec timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    export_file = export_dir / f'annotations_{timestamp}.json'
    
    # Sauvegarder
    print(f"{Colors.YELLOW}💾 Sauvegarde des annotations...{Colors.RESET}")
    
    export_data = {
        'project_name': project.title,
        'export_date': datetime.now().isoformat(),
        'total_tasks': len(tasks),
        'completed_tasks': len(completed_tasks),
        'tasks': completed_tasks
    }
    
    with open(export_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"{Colors.GREEN}✅ Export sauvegardé : {export_file}{Colors.RESET}")
    
    # Statistiques
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}📊 STATISTIQUES{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    # Compter les labels
    label_counts = {}
    for task in completed_tasks:
        for annotation in task.get('annotations', []):
            for result in annotation.get('result', []):
                if 'value' in result and 'rectanglelabels' in result['value']:
                    for label in result['value']['rectanglelabels']:
                        label_counts[label] = label_counts.get(label, 0) + 1
    
    print(f"\n  Factures annotées : {len(completed_tasks)}")
    print(f"\n  Annotations par type :")
    for label, count in sorted(label_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    • {label:25s} : {count:4d} occurrences")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    # Moyenne d'annotations par facture
    total_annotations = sum(label_counts.values())
    avg_per_invoice = total_annotations / len(completed_tasks) if completed_tasks else 0
    print(f"  Moyenne : {avg_per_invoice:.1f} annotations par facture\n")
    
    # Recommandations
    if len(completed_tasks) < 100:
        print(f"{Colors.YELLOW}💡 CONSEIL : Annotez au moins {100 - len(completed_tasks)} factures supplémentaires{Colors.RESET}")
    else:
        print(f"{Colors.GREEN}✨ Excellent ! Vous avez assez de données pour l'entraînement{Colors.RESET}")
    
    print(f"\n{Colors.GREEN}🎉 Export terminé avec succès !{Colors.RESET}\n")
    
    # Prochaine étape
    print(f"{Colors.BLUE}➡️  Prochaine étape :{Colors.RESET}")
    print(f"    python scripts/prepare_dataset.py\n")
    
    return export_file


if __name__ == '__main__':
    config = load_config()
    export_file = export_annotations(config)
