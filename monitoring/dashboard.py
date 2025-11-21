#!/usr/bin/env python3
"""
Dashboard de monitoring simple pour le système d'extraction de factures

Lance un serveur web simple pour visualiser les statistiques.

Usage:
    python monitoring/dashboard.py
"""

import yaml
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
import http.server
import socketserver
import webbrowser
from threading import Timer

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


def gather_statistics() -> Dict:
    """Collecter les statistiques du système"""
    stats = {
        'timestamp': datetime.now().isoformat(),
        'label_studio': {},
        'training': {},
        'api': {}
    }

    # Stats Label Studio (depuis les exports)
    exports_dir = Path('data/exports')
    if exports_dir.exists():
        export_files = list(exports_dir.glob('annotations_*.json'))
        if export_files:
            latest_export = max(export_files, key=lambda p: p.stat().st_mtime)
            with open(latest_export, 'r') as f:
                data = json.load(f)
                stats['label_studio'] = {
                    'total_tasks': data.get('total_tasks', 0),
                    'completed_tasks': data.get('completed_tasks', 0),
                    'last_export': data.get('export_date', '')
                }

    # Stats des modèles
    models_dir = Path('data/models')
    if models_dir.exists():
        model_files = list(models_dir.glob('invoice_model_*.pt'))
        stats['training'] = {
            'total_models': len(model_files),
            'latest_model': max(model_files, key=lambda p: p.stat().st_mtime).name if model_files else None
        }

    return stats


def generate_html(stats: Dict) -> str:
    """Générer le HTML du dashboard"""

    html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invoice ML System - Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        h1 {{
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}

        .cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}

        .card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }}

        .card:hover {{
            transform: translateY(-5px);
        }}

        .card h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}

        .stat {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
        }}

        .stat:last-child {{
            border-bottom: none;
        }}

        .stat-label {{
            color: #666;
            font-weight: 500;
        }}

        .stat-value {{
            color: #333;
            font-weight: bold;
            font-size: 1.2em;
        }}

        .stat-value.good {{
            color: #10b981;
        }}

        .stat-value.warning {{
            color: #f59e0b;
        }}

        .stat-value.bad {{
            color: #ef4444;
        }}

        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
        }}

        .refresh-btn {{
            display: block;
            width: 200px;
            margin: 20px auto;
            padding: 12px 24px;
            background: white;
            color: #667eea;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .refresh-btn:hover {{
            background: #667eea;
            color: white;
            transform: scale(1.05);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Invoice ML System - Dashboard</h1>

        <div class="cards">
            <!-- Label Studio Stats -->
            <div class="card">
                <h2>📝 Annotation (Label Studio)</h2>
                <div class="stat">
                    <span class="stat-label">Total de tâches</span>
                    <span class="stat-value">{stats['label_studio'].get('total_tasks', 0)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Factures annotées</span>
                    <span class="stat-value {'good' if stats['label_studio'].get('completed_tasks', 0) >= 100 else 'warning'}">
                        {stats['label_studio'].get('completed_tasks', 0)}
                    </span>
                </div>
                <div class="stat">
                    <span class="stat-label">Dernier export</span>
                    <span class="stat-value">{stats['label_studio'].get('last_export', 'Jamais')[:10] if stats['label_studio'].get('last_export') else 'Jamais'}</span>
                </div>
            </div>

            <!-- Training Stats -->
            <div class="card">
                <h2>🤖 Entraînement</h2>
                <div class="stat">
                    <span class="stat-label">Modèles entraînés</span>
                    <span class="stat-value {'good' if stats['training'].get('total_models', 0) > 0 else 'warning'}">
                        {stats['training'].get('total_models', 0)}
                    </span>
                </div>
                <div class="stat">
                    <span class="stat-label">Dernier modèle</span>
                    <span class="stat-value">{stats['training'].get('latest_model', 'Aucun')[:30] if stats['training'].get('latest_model') else 'Aucun'}</span>
                </div>
            </div>

            <!-- System Info -->
            <div class="card">
                <h2>ℹ️ Informations Système</h2>
                <div class="stat">
                    <span class="stat-label">Dernière mise à jour</span>
                    <span class="stat-value">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Statut</span>
                    <span class="stat-value good">✅ Opérationnel</span>
                </div>
            </div>
        </div>

        <button class="refresh-btn" onclick="location.reload()">🔄 Rafraîchir</button>

        <div class="footer">
            <p>Invoice ML System v1.0</p>
            <p>Généré le {datetime.now().strftime('%Y-%m-%d à %H:%M:%S')}</p>
        </div>
    </div>

    <script>
        // Auto-refresh toutes les 30 secondes
        setTimeout(function(){{
            location.reload();
        }}, 30000);
    </script>
</body>
</html>
    """
    return html


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Handler personnalisé pour le dashboard"""

    def do_GET(self):
        """Servir le dashboard"""
        if self.path == '/' or self.path == '/dashboard':
            stats = gather_statistics()
            html = generate_html(stats)

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_error(404, "Page non trouvée")

    def log_message(self, format, *args):
        """Supprimer les logs de requêtes pour un affichage plus propre"""
        pass


def open_browser(port):
    """Ouvrir le navigateur après un délai"""
    webbrowser.open(f'http://localhost:{port}/dashboard')


def main():
    """Lancer le dashboard"""
    config = load_config()
    port = config['monitoring']['dashboard'].get('port', 8001)

    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}📊 DASHBOARD DE MONITORING{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

    print(f"{Colors.GREEN}✅ Dashboard lancé sur: http://localhost:{port}/dashboard{Colors.RESET}")
    print(f"{Colors.YELLOW}💡 Appuyez sur Ctrl+C pour arrêter{Colors.RESET}\n")

    # Ouvrir le navigateur après 1 seconde
    Timer(1.0, open_browser, args=[port]).start()

    # Lancer le serveur
    with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}👋 Arrêt du dashboard...{Colors.RESET}\n")


if __name__ == '__main__':
    main()
