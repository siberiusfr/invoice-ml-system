#!/usr/bin/env python3
"""
Configuration du réentraînement automatique

Configure un cron job (Linux/Mac) ou une tâche planifiée (Windows)
pour exécuter auto_retrain.py automatiquement.

Usage:
    python scripts/setup_auto_retrain.py
"""

import os
import sys
import yaml
from pathlib import Path
import platform

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


def setup_linux_cron(schedule: str, script_path: Path):
    """Configurer un cron job sur Linux/Mac"""

    print(f"{Colors.YELLOW}🐧 Configuration du cron job Linux/Mac...{Colors.RESET}\n")

    cron_command = f"{schedule} cd {script_path.parent.parent} && python {script_path}"

    print(f"{Colors.YELLOW}Ajoutez cette ligne à votre crontab:{Colors.RESET}\n")
    print(f"  {cron_command}\n")
    print(f"{Colors.YELLOW}Pour éditer votre crontab:{Colors.RESET}")
    print(f"  crontab -e\n")


def setup_windows_task(schedule: str, script_path: Path):
    """Configurer une tâche planifiée sur Windows"""

    print(f"{Colors.YELLOW}🪟 Configuration de la tâche planifiée Windows...{Colors.RESET}\n")

    # Convertir le format cron en format Windows
    # Format cron: minute hour day month weekday
    # Exemple: "0 3 * * *" = tous les jours à 3h du matin

    parts = schedule.split()
    if len(parts) >= 2:
        minute = parts[0]
        hour = parts[1]
        time_str = f"{hour.zfill(2)}:{minute.zfill(2)}"
    else:
        time_str = "03:00"

    print(f"{Colors.YELLOW}Créez une tâche planifiée avec ces paramètres:{Colors.RESET}\n")
    print(f"  Nom: Invoice ML Auto-Retrain")
    print(f"  Heure: {time_str}")
    print(f"  Fréquence: Quotidienne")
    print(f"  Action: Démarrer un programme")
    print(f"  Programme: python")
    print(f"  Arguments: {script_path}")
    print(f"  Dossier de démarrage: {script_path.parent.parent}\n")

    print(f"{Colors.YELLOW}Pour créer la tâche via PowerShell:{Colors.RESET}\n")

    ps_command = f"""
$action = New-ScheduledTaskAction -Execute "python" -Argument "{script_path}" -WorkingDirectory "{script_path.parent.parent}"
$trigger = New-ScheduledTaskTrigger -Daily -At {time_str}
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "InvoiceMLAutoRetrain" -Description "Réentraînement automatique du modèle Invoice ML"
    """

    print(ps_command)


def main():
    """Main"""

    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}⚙️  CONFIGURATION DU RÉENTRAÎNEMENT AUTOMATIQUE{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

    config = load_config()

    if not config['auto_retrain']['enabled']:
        print(f"{Colors.YELLOW}⚠️  Le réentraînement automatique est désactivé{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Activez-le dans config/settings.yaml avant de continuer{Colors.RESET}\n")
        return

    schedule = config['auto_retrain']['schedule']
    script_path = Path(__file__).parent / 'auto_retrain.py'

    print(f"{Colors.YELLOW}Configuration:{Colors.RESET}")
    print(f"  Schedule cron: {schedule}")
    print(f"  Script: {script_path}\n")

    # Détecter l'OS
    system = platform.system()

    if system in ['Linux', 'Darwin']:  # Darwin = macOS
        setup_linux_cron(schedule, script_path.absolute())
    elif system == 'Windows':
        setup_windows_task(schedule, script_path.absolute())
    else:
        print(f"{Colors.RED}❌ Système non supporté: {system}{Colors.RESET}")

    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.GREEN}✅ Instructions affichées{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

    print(f"{Colors.YELLOW}💡 Pour tester le réentraînement automatique:{Colors.RESET}")
    print(f"    python scripts/auto_retrain.py --dry-run\n")


if __name__ == '__main__':
    main()
