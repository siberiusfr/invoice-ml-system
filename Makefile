# Makefile pour Invoice ML System

.PHONY: help install setup clean test api dashboard train

help:  ## Afficher l'aide
	@echo "📋 Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Installer les dépendances
	pip install -r requirements.txt

setup:  ## Configuration initiale complète
	@echo "🚀 Configuration du projet..."
	python -m venv venv
	./venv/bin/pip install -r requirements.txt
	cp config/settings.example.yaml config/settings.yaml
	docker-compose up -d
	@echo "✅ Configuration terminée !"
	@echo "📝 N'oubliez pas de configurer votre API key dans config/settings.yaml"

clean:  ## Nettoyer les fichiers temporaires
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".DS_Store" -delete

test:  ## Lancer les tests
	pytest tests/ -v

test-coverage:  ## Tests avec couverture
	pytest tests/ --cov=api --cov=training --cov-report=html
	@echo "📊 Rapport de couverture: htmlcov/index.html"

# Label Studio
label-studio-start:  ## Démarrer Label Studio
	docker-compose up -d
	@echo "✅ Label Studio: http://localhost:8080"

label-studio-stop:  ## Arrêter Label Studio
	docker-compose down

label-studio-logs:  ## Voir les logs Label Studio
	docker-compose logs -f

# Scripts
import:  ## Importer les factures dans Label Studio
	python scripts/import_to_label_studio.py

export:  ## Exporter les annotations depuis Label Studio
	python scripts/export_from_label_studio.py

prepare:  ## Préparer le dataset pour l'entraînement
	python scripts/prepare_dataset.py

# Training
train:  ## Entraîner le modèle YOLO
	python training/train_yolo.py

train-small:  ## Entraîner avec le modèle nano (rapide)
	python training/train_yolo.py --model yolov8n.pt --epochs 50

evaluate:  ## Évaluer le modèle
	python training/evaluate.py

# API
api:  ## Lancer l'API
	python api/app.py

api-dev:  ## Lancer l'API en mode développement
	uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

test-api:  ## Tester l'API
	python scripts/test_api.py

# Monitoring
dashboard:  ## Lancer le dashboard de monitoring
	python monitoring/dashboard.py

# Auto-retrain
auto-retrain:  ## Lancer le réentraînement automatique
	python scripts/auto_retrain.py

auto-retrain-dry:  ## Test du réentraînement (dry-run)
	python scripts/auto_retrain.py --dry-run

setup-cron:  ## Configurer le réentraînement automatique
	python scripts/setup_auto_retrain.py

# Workflow complet
workflow-phase1:  ## Phase 1 complète (annotation)
	@echo "📝 Phase 1: Annotation"
	@echo "1. Démarrage de Label Studio..."
	docker-compose up -d
	@echo "2. Import des factures..."
	python scripts/import_to_label_studio.py
	@echo "✅ Annotez maintenant dans Label Studio: http://localhost:8080"

workflow-phase2:  ## Phase 2 complète (entraînement)
	@echo "🤖 Phase 2: Entraînement"
	@echo "1. Export des annotations..."
	python scripts/export_from_label_studio.py
	@echo "2. Préparation du dataset..."
	python scripts/prepare_dataset.py
	@echo "3. Entraînement du modèle..."
	python training/train_yolo.py
	@echo "4. Évaluation..."
	python training/evaluate.py
	@echo "✅ Phase 2 terminée !"

workflow-phase3:  ## Phase 3 complète (production)
	@echo "🚀 Phase 3: Production"
	@echo "1. Démarrage de l'API..."
	python api/app.py &
	@echo "2. Démarrage du dashboard..."
	python monitoring/dashboard.py &
	@echo "✅ API: http://localhost:8000"
	@echo "✅ Dashboard: http://localhost:8001/dashboard"

# Docker
docker-build:  ## Construire l'image Docker de l'API
	docker build -t invoice-ml-api .

docker-run:  ## Lancer l'API dans Docker
	docker run -p 8000:8000 -v $(PWD)/data:/app/data invoice-ml-api

# Utilitaires
stats:  ## Afficher les statistiques du projet
	@echo "📊 Statistiques du projet"
	@echo "=========================="
	@echo "Lignes de code Python:"
	@find . -name "*.py" -not -path "./venv/*" | xargs wc -l | tail -1
	@echo "\nFichiers de code:"
	@find . -name "*.py" -not -path "./venv/*" | wc -l
	@echo "\nTaille du projet:"
	@du -sh . 2>/dev/null | awk '{print $$1}'

logs:  ## Créer le dossier de logs
	mkdir -p logs

all:  ## Workflow complet (dangereux, longue durée)
	@echo "⚠️  Lancement du workflow complet..."
	make workflow-phase1
	@echo "\n⏸️  Annotez vos factures puis appuyez sur Entrée pour continuer..."
	@read dummy
	make workflow-phase2
	make workflow-phase3
