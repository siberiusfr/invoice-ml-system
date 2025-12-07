#!/usr/bin/env python3
"""
Script pour supprimer toutes les tâches d'un projet Label Studio

Usage:
    python scripts/clear_label_studio_tasks.py
"""

import yaml
from pathlib import Path
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
        exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def clear_tasks(config):
    """Supprimer toutes les tâches du projet"""

    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}🗑️  NETTOYAGE DU PROJET LABEL STUDIO{Colors.RESET}")
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
        print(f"   Tâches actuelles : {project.task_number}\n")
    except Exception as e:
        print(f"{Colors.RED}❌ Projet non trouvé : {e}{Colors.RESET}")
        exit(1)

    if project.task_number == 0:
        print(f"{Colors.YELLOW}ℹ️  Le projet est déjà vide{Colors.RESET}\n")
        return

    # Confirmation
    print(f"{Colors.RED}⚠️  ATTENTION : Cette action va supprimer TOUTES les tâches du projet !{Colors.RESET}")
    response = input(f"{Colors.YELLOW}Êtes-vous sûr ? (oui/non): {Colors.RESET}").strip().lower()

    if response not in ['oui', 'yes', 'y', 'o']:
        print(f"\n{Colors.YELLOW}❌ Opération annulée{Colors.RESET}\n")
        return

    # Supprimer toutes les tâches
    print(f"\n{Colors.YELLOW}🗑️  Suppression en cours...{Colors.RESET}")
    try:
        client.tasks.delete_all_tasks(id=project.id)
        print(f"{Colors.GREEN}✅ Toutes les tâches ont été supprimées !{Colors.RESET}\n")
    except Exception as e:
        print(f"{Colors.RED}❌ Erreur lors de la suppression : {e}{Colors.RESET}")
        exit(1)

    # Vérification
    updated_project = client.projects.get(id=project.id)
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}📊 RÉSUMÉ{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"  Tâches restantes : {updated_project.task_number}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")


if __name__ == '__main__':
    config = load_config()
    clear_tasks(config)
