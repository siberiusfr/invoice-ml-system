"""
Tests unitaires pour les modèles Pydantic
"""
import pytest
from datetime import datetime
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.models import (
    BoundingBox,
    ExtractedField,
    InvoiceExtraction,
    ExtractionResponse,
    HealthResponse,
    StatsResponse
)


def test_bounding_box():
    """Test du modèle BoundingBox"""
    bbox = BoundingBox(x=0.1, y=0.2, width=0.3, height=0.4)
    assert bbox.x == 0.1
    assert bbox.y == 0.2
    assert bbox.width == 0.3
    assert bbox.height == 0.4


def test_bounding_box_invalid():
    """Test de validation BoundingBox"""
    with pytest.raises(Exception):
        BoundingBox(x="invalid", y=0.2, width=0.3, height=0.4)


def test_extracted_field():
    """Test du modèle ExtractedField"""
    bbox = BoundingBox(x=0.1, y=0.2, width=0.3, height=0.4)
    field = ExtractedField(
        label="numero_facture",
        value="INV-001",
        confidence=0.95,
        bbox=bbox
    )
    assert field.label == "numero_facture"
    assert field.value == "INV-001"
    assert field.confidence == 0.95
    assert field.bbox == bbox


def test_extracted_field_without_bbox():
    """Test ExtractedField sans bbox (optionnel)"""
    field = ExtractedField(
        label="montant_ttc",
        value="1000.00",
        confidence=0.85,
        bbox=None
    )
    assert field.bbox is None


def test_invoice_extraction():
    """Test du modèle InvoiceExtraction"""
    field = ExtractedField(
        label="numero_facture",
        value="INV-001",
        confidence=0.95
    )

    extraction = InvoiceExtraction(
        filename="test.pdf",
        fields=[field],
        overall_confidence=0.95,
        needs_review=False,
        model_version="test_v1"
    )

    assert extraction.filename == "test.pdf"
    assert len(extraction.fields) == 1
    assert extraction.overall_confidence == 0.95
    assert extraction.needs_review is False


def test_extraction_response_success():
    """Test ExtractionResponse avec succès"""
    field = ExtractedField(
        label="numero_facture",
        value="INV-001",
        confidence=0.95
    )

    extraction = InvoiceExtraction(
        filename="test.pdf",
        fields=[field],
        overall_confidence=0.95,
        needs_review=False,
        model_version="test_v1"
    )

    response = ExtractionResponse(
        success=True,
        data=extraction,
        message="Extraction réussie"
    )

    assert response.success is True
    assert response.data is not None
    assert response.error is None


def test_extraction_response_error():
    """Test ExtractionResponse avec erreur"""
    response = ExtractionResponse(
        success=False,
        error="Model not loaded",
        message="Le modèle n'est pas chargé"
    )

    assert response.success is False
    assert response.data is None
    assert response.error == "Model not loaded"


def test_health_response():
    """Test du modèle HealthResponse"""
    health = HealthResponse(
        status="healthy",
        version="1.0.0",
        model_loaded=True,
        model_version="test_v1",
        uptime_seconds=3600.5
    )

    assert health.status == "healthy"
    assert health.model_loaded is True
    assert health.uptime_seconds == 3600.5


def test_stats_response():
    """Test du modèle StatsResponse"""
    stats = StatsResponse(
        total_extractions=100,
        average_confidence=0.87,
        extractions_last_24h=10,
        model_version="test_v1",
        success_rate=0.95
    )

    assert stats.total_extractions == 100
    assert stats.average_confidence == 0.87
    assert stats.success_rate == 0.95


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
