"""
Tests unitaires pour l'API
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.app import app


client = TestClient(app)


def test_root():
    """Test de l'endpoint racine"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Invoice ML System API"
    assert data["version"] == "1.0.0"
    assert "docs" in data


def test_health():
    """Test du health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "model_loaded" in data
    assert "uptime_seconds" in data


def test_stats_without_model():
    """Test des statistiques sans modèle chargé"""
    response = client.get("/stats")
    # Peut retourner 503 si le modèle n'est pas chargé
    assert response.status_code in [200, 503]


def test_extract_without_file():
    """Test d'extraction sans fichier"""
    response = client.post("/extract")
    assert response.status_code == 422  # Validation error


def test_extract_invalid_file_type():
    """Test d'extraction avec type de fichier invalide"""
    files = {"file": ("test.txt", b"test content", "text/plain")}
    response = client.post("/extract", files=files)
    # Peut retourner 200 avec success=false ou 422
    assert response.status_code in [200, 422]


# NOTE: Ces tests nécessitent un modèle entraîné
# Pour les exécuter, assurez-vous d'avoir un modèle dans data/models/

@pytest.mark.skipif(
    not Path("data/models").exists() or not list(Path("data/models").glob("*.pt")),
    reason="Aucun modèle trouvé"
)
def test_extract_with_valid_image():
    """Test d'extraction avec une image valide"""
    # TODO: Créer une image de test
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
