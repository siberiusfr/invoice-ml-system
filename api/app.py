#!/usr/bin/env python3
"""
API REST pour l'extraction automatique de factures

Lance l'API avec:
    python api/app.py

Ou avec uvicorn:
    uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
"""
import os
import time
import tempfile
import yaml
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .models import (
    ExtractionResponse,
    HealthResponse,
    StatsResponse,
    InvoiceExtraction
)
from .extractor import InvoiceExtractor


# ============================================
# Configuration
# ============================================

def load_config():
    """Charger la configuration"""
    config_path = Path(__file__).parent.parent / 'config' / 'settings.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


config = load_config()

# ============================================
# FastAPI App
# ============================================

app = FastAPI(
    title="Invoice ML System API",
    description="API d'extraction automatique de données de factures",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales
extractor = InvoiceExtractor()
start_time = time.time()


# ============================================
# Startup / Shutdown
# ============================================

@app.on_event("startup")
async def startup_event():
    """Charger le modèle au démarrage"""
    print("\n" + "="*60)
    print("🚀 INVOICE ML SYSTEM API")
    print("="*60)

    try:
        extractor.load_model()
        print("✅ Modèle chargé avec succès")
    except Exception as e:
        print(f"⚠️  Impossible de charger le modèle: {e}")
        print("💡 L'API démarre sans modèle. Entraînez d'abord un modèle.")

    print(f"\n📡 API disponible sur: http://localhost:{config['api']['port']}")
    print(f"📖 Documentation: http://localhost:{config['api']['port']}/docs")
    print("="*60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage à l'arrêt"""
    print("\n👋 Arrêt de l'API...")


# ============================================
# Routes
# ============================================

@app.get("/", tags=["General"])
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "Invoice ML System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Vérifier l'état de l'API"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        model_loaded=extractor.is_model_loaded(),
        model_version=extractor.model_version if extractor.is_model_loaded() else None,
        uptime_seconds=time.time() - start_time
    )


@app.get("/stats", response_model=StatsResponse, tags=["General"])
async def get_stats():
    """Obtenir les statistiques d'utilisation"""
    if not extractor.is_model_loaded():
        raise HTTPException(status_code=503, detail="Modèle non chargé")

    stats = extractor.get_stats()
    return StatsResponse(**stats)


@app.post("/extract", response_model=ExtractionResponse, tags=["Extraction"])
async def extract_invoice(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Extraire les données d'une facture

    Args:
        file: Fichier PDF ou image de la facture

    Returns:
        Données extraites avec confiance et coordonnées
    """
    if not extractor.is_model_loaded():
        return ExtractionResponse(
            success=False,
            error="Model not loaded",
            message="Le modèle n'est pas chargé. Entraînez d'abord un modèle."
        )

    # Vérifier le type de fichier
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    file_extension = Path(file.filename).suffix.lower()

    if file_extension not in allowed_extensions:
        return ExtractionResponse(
            success=False,
            error="Invalid file type",
            message=f"Type de fichier non supporté. Utilisez: {', '.join(allowed_extensions)}"
        )

    # Sauvegarder temporairement le fichier
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Extraire les données
        extraction = extractor.extract_from_file(tmp_path)

        # Nettoyer le fichier temporaire
        os.unlink(tmp_path)

        # Si confiance faible et feedback loop activé, envoyer vers Label Studio
        if extraction.needs_review and config['api']['feedback_loop']['enabled']:
            if config['api']['feedback_loop']['auto_send_to_label_studio']:
                # TODO: Implémenter l'envoi automatique vers Label Studio
                pass

        return ExtractionResponse(
            success=True,
            data=extraction,
            message="Extraction réussie" if not extraction.needs_review else "Extraction réussie mais nécessite une revue"
        )

    except Exception as e:
        # Nettoyer en cas d'erreur
        if 'tmp_path' in locals():
            try:
                os.unlink(tmp_path)
            except:
                pass

        return ExtractionResponse(
            success=False,
            error=str(e),
            message=f"Erreur lors de l'extraction: {str(e)}"
        )


@app.post("/reload-model", tags=["Model"])
async def reload_model(model_path: Optional[str] = None):
    """
    Recharger le modèle (utile après réentraînement)

    Args:
        model_path: Chemin optionnel vers un modèle spécifique
    """
    try:
        extractor.load_model(model_path)
        return {
            "success": True,
            "message": "Modèle rechargé avec succès",
            "model_version": extractor.model_version
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# Main
# ============================================

def main():
    """Lancer l'API"""
    uvicorn.run(
        "api.app:app",
        host=config['api']['host'],
        port=config['api']['port'],
        reload=config['api']['reload'],
        log_level="info"
    )


if __name__ == "__main__":
    main()
