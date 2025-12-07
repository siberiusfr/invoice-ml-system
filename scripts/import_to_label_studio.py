#!/usr/bin/env python3
"""
Script d'import automatique des factures dans Label Studio

Ce script scanne le dossier data/raw/invoices/ et importe
toutes les factures (PDF, JPG, PNG) dans votre projet Label Studio.

Usage:
    python scripts/import_to_label_studio.py
"""

import os
import yaml
import base64
from pathlib import Path
from label_studio_sdk import LabelStudio
from tqdm import tqdm
import fitz  # PyMuPDF pour convertir PDF en image
from PIL import Image
import io

# Couleurs pour l'affichage terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def load_config():
    """Charger la configuration depuis settings.yaml"""
    config_path = Path(__file__).parent.parent / 'config' / 'settings.yaml'
    
    if not config_path.exists():
        print(f"{Colors.RED}❌ Fichier de configuration non trouvé !{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Copiez settings.example.yaml vers settings.yaml et configurez-le{Colors.RESET}")
        exit(1)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_invoice_files(invoices_dir):
    """Trouver tous les fichiers de factures"""
    supported_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    invoice_files = []
    
    if not os.path.exists(invoices_dir):
        print(f"{Colors.RED}❌ Dossier {invoices_dir} n'existe pas !{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Créez-le et placez-y vos factures{Colors.RESET}")
        exit(1)
    
    for file_path in Path(invoices_dir).rglob('*'):
        if file_path.suffix.lower() in supported_extensions:
            invoice_files.append(file_path)
    
    return invoice_files


def pdf_to_image_base64(pdf_path):
    """Convertir la première page d'un PDF en image PNG base64"""
    try:
        # Ouvrir le PDF
        doc = fitz.open(pdf_path)
        page = doc[0]  # Première page

        # Convertir en image avec bonne résolution
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom pour bonne qualité

        # Convertir en PNG bytes
        img_bytes = pix.tobytes("png")
        doc.close()

        # Encoder en base64
        base64_bytes = base64.b64encode(img_bytes)
        base64_string = base64_bytes.decode('utf-8')

        return f"data:image/png;base64,{base64_string}"
    except Exception as e:
        raise Exception(f"Erreur conversion PDF: {e}")


def convert_file_to_base64(file_path):
    """Convertir un fichier en base64 pour Label Studio"""
    extension = file_path.suffix.lower()

    # Si c'est un PDF, le convertir en image
    if extension == '.pdf':
        return pdf_to_image_base64(file_path)

    # Pour les images, lire directement
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
        base64_bytes = base64.b64encode(file_bytes)
        base64_string = base64_bytes.decode('utf-8')

    # Déterminer le type MIME
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png'
    }
    mime_type = mime_types.get(extension, 'image/jpeg')

    return f"data:{mime_type};base64,{base64_string}"


def import_to_label_studio(config):
    """Import principal des factures"""
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}🚀 IMPORT DE FACTURES DANS LABEL STUDIO{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    # Connexion à Label Studio
    print(f"{Colors.YELLOW}📡 Connexion à Label Studio...{Colors.RESET}")
    try:
        client = LabelStudio(base_url=config['label_studio']['url'], api_key=config['label_studio']['api_key'])
        # A basic request to verify connection is working
        me = client.users.whoami()
        print("username:", me.username)
        print("email:", me.email)
        print(f"{Colors.GREEN}✅ Connecté avec succès !{Colors.RESET}\n")
    except Exception as e:
        print(f"{Colors.RED}❌ Erreur de connexion : {e}{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Vérifiez que Label Studio est démarré (docker-compose up -d){Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Vérifiez votre API key dans config/settings.yaml{Colors.RESET}")
        exit(1)
    
    # Récupérer le projet
    try:
        project = client.projects.get(id=config['label_studio']['project_id'])
        print(f"{Colors.GREEN}📁 Projet trouvé : {project.title}{Colors.RESET}")
        print(f"   ID: {project.id}")
        print(f"   Tâches existantes : {project.task_number} \n")
    except Exception as e:
        print(f"{Colors.RED}❌ Projet non trouvé : {e}{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Vérifiez le project_id dans config/settings.yaml{Colors.RESET}")
        exit(1)
    
    # Trouver les factures
    invoices_dir = Path(config['dataset']['raw_data_path'])
    invoice_files = get_invoice_files(invoices_dir)
    
    if not invoice_files:
        print(f"{Colors.YELLOW}⚠️  Aucune facture trouvée dans {invoices_dir}{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Placez vos factures (PDF, JPG, PNG) dans ce dossier{Colors.RESET}")
        exit(0)
    
    print(f"{Colors.GREEN}📄 {len(invoice_files)} factures trouvées{Colors.RESET}\n")
    
    # Récupérer les tâches déjà importées pour éviter les doublons
    existing_tasks = client.tasks.list(project=project.id)
    existing_filenames = {task.data.get('filename') for task in existing_tasks if hasattr(task, 'data') and task.data and 'filename' in task.data}
    
    # Préparer les tâches à importer
    tasks_to_import = []
    skipped = 0

    print(f"{Colors.YELLOW}🔄 Préparation des imports...{Colors.RESET}")
    print(f"{Colors.YELLOW}💡 Les fichiers PDF seront automatiquement convertis en images PNG{Colors.RESET}\n")

    for invoice_file in tqdm(invoice_files, desc="Traitement", unit="facture"):
        filename = invoice_file.name
        
        # Vérifier si déjà importé
        if filename in existing_filenames:
            skipped += 1
            continue
        
        # Convertir en base64
        try:
            image_data = convert_file_to_base64(invoice_file)
            
            task = {
                'data': {
                    'image': image_data,
                    'filename': filename,
                    'file_path': str(invoice_file)
                },
                'meta': {
                    'file_size': invoice_file.stat().st_size,
                    'file_type': invoice_file.suffix
                }
            }
            
            tasks_to_import.append(task)
            
        except Exception as e:
            print(f"\n{Colors.RED}❌ Erreur avec {filename}: {e}{Colors.RESET}")
            continue
    
    # Importer les tâches
    if tasks_to_import:
        print(f"\n{Colors.YELLOW}📤 Import de {len(tasks_to_import)} nouvelles factures...{Colors.RESET}")

        try:
            # Importer chaque tâche individuellement avec barre de progression
            imported_count = 0
            for task in tqdm(tasks_to_import, desc="Import", unit="facture"):
                client.tasks.create(
                    project=project.id,
                    data=task['data'],
                    meta=task.get('meta')
                )
                imported_count += 1
            print(f"{Colors.GREEN}✅ {imported_count} factures importées avec succès !{Colors.RESET}\n")
        except Exception as e:
            print(f"{Colors.RED}❌ Erreur d'import : {e}{Colors.RESET}")
            if imported_count > 0:
                print(f"{Colors.YELLOW}⚠️  {imported_count} factures ont été importées avant l'erreur{Colors.RESET}")
            exit(1)
    else:
        print(f"\n{Colors.YELLOW}ℹ️  Aucune nouvelle facture à importer{Colors.RESET}\n")
    
    # Résumé
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}📊 RÉSUMÉ{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"  Factures trouvées     : {len(invoice_files)}")
    print(f"  Déjà importées        : {skipped}")
    print(f"  Nouvelles importées   : {len(tasks_to_import)}")
    # Récupérer le nombre de tâches après l'import
    updated_project = client.projects.get(id=project.id)
    print(f"  Total dans le projet  : {updated_project.task_number}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    print(f"{Colors.GREEN}✨ C'est prêt ! Rendez-vous sur {config['label_studio']['url']} pour commencer l'annotation{Colors.RESET}\n")


if __name__ == '__main__':
    config = load_config()
    import_to_label_studio(config)
