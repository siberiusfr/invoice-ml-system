"""
Pydantic models pour l'API
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class BoundingBox(BaseModel):
    """Coordonnées d'une bounding box"""
    x: float = Field(..., description="Coordonnée X (pourcentage)")
    y: float = Field(..., description="Coordonnée Y (pourcentage)")
    width: float = Field(..., description="Largeur (pourcentage)")
    height: float = Field(..., description="Hauteur (pourcentage)")


class ExtractedField(BaseModel):
    """Un champ extrait d'une facture"""
    label: str = Field(..., description="Type de champ (ex: numero_facture)")
    value: str = Field(..., description="Valeur extraite")
    confidence: float = Field(..., description="Confiance du modèle (0-1)")
    bbox: Optional[BoundingBox] = Field(None, description="Position du champ")


class InvoiceExtraction(BaseModel):
    """Résultat complet d'extraction d'une facture"""
    filename: str = Field(..., description="Nom du fichier")
    extracted_at: datetime = Field(default_factory=datetime.now)
    fields: List[ExtractedField] = Field(..., description="Champs extraits")
    overall_confidence: float = Field(..., description="Confiance moyenne")
    needs_review: bool = Field(..., description="Nécessite une revue humaine")
    model_version: str = Field(..., description="Version du modèle utilisé")


class ExtractionResponse(BaseModel):
    """Réponse de l'API d'extraction"""
    success: bool
    data: Optional[InvoiceExtraction] = None
    error: Optional[str] = None
    message: str


class HealthResponse(BaseModel):
    """Réponse du health check"""
    status: str
    version: str
    model_loaded: bool
    model_version: Optional[str] = None
    uptime_seconds: float


class StatsResponse(BaseModel):
    """Statistiques de l'API"""
    total_extractions: int
    average_confidence: float
    extractions_last_24h: int
    model_version: str
    success_rate: float
