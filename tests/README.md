# 🧪 Tests

Tests unitaires et d'intégration pour le système Invoice ML.

## 📋 Structure

```
tests/
├── __init__.py
├── test_api.py          # Tests de l'API REST
├── test_models.py       # Tests des modèles Pydantic
└── README.md            # Ce fichier
```

## 🚀 Lancer les tests

### Tous les tests

```bash
pytest tests/ -v
```

### Tests spécifiques

```bash
# Tests de l'API
pytest tests/test_api.py -v

# Tests des modèles
pytest tests/test_models.py -v
```

### Avec couverture

```bash
pytest tests/ --cov=api --cov=training --cov-report=html
```

Le rapport de couverture sera généré dans `htmlcov/index.html`

## 📊 Tests disponibles

### test_api.py

Tests de l'API FastAPI:
- ✅ Endpoint racine (/)
- ✅ Health check (/health)
- ✅ Statistiques (/stats)
- ✅ Extraction (/extract)
- ⏭️ Tests avec modèle chargé (skip si pas de modèle)

### test_models.py

Tests des modèles Pydantic:
- ✅ BoundingBox
- ✅ ExtractedField
- ✅ InvoiceExtraction
- ✅ ExtractionResponse
- ✅ HealthResponse
- ✅ StatsResponse

## 🔧 Configuration

### Installer les dépendances de test

```bash
pip install pytest pytest-cov
```

### Fixtures

Les fixtures sont définies dans `conftest.py` (à créer si nécessaire).

## 📝 Écrire de nouveaux tests

### Template de test

```python
import pytest

def test_my_function():
    """Test de ma fonction"""
    # Arrange
    input_data = "test"

    # Act
    result = my_function(input_data)

    # Assert
    assert result == "expected"
```

### Tests avec fixtures

```python
@pytest.fixture
def sample_invoice():
    """Fixture pour une facture de test"""
    return {
        "filename": "test.pdf",
        "fields": [...]
    }

def test_with_fixture(sample_invoice):
    """Test utilisant une fixture"""
    assert sample_invoice["filename"] == "test.pdf"
```

### Tests paramétrés

```python
@pytest.mark.parametrize("input,expected", [
    (0.5, True),
    (0.3, False),
    (0.9, True)
])
def test_threshold(input, expected):
    """Test avec plusieurs valeurs"""
    result = is_above_threshold(input, 0.5)
    assert result == expected
```

## 🎯 Objectifs de couverture

| Module | Cible | Actuel |
|--------|-------|--------|
| api/ | 80% | TODO |
| training/ | 70% | TODO |
| scripts/ | 60% | TODO |

## 🐛 Tests d'intégration

### Test complet du workflow

```bash
# 1. Lancer Label Studio
docker-compose up -d

# 2. Lancer les tests d'intégration
pytest tests/integration/ -v
```

## 🔍 Debugging

### Mode verbose

```bash
pytest tests/ -vv
```

### Arrêter au premier échec

```bash
pytest tests/ -x
```

### Afficher les print()

```bash
pytest tests/ -s
```

### Lancer un test spécifique

```bash
pytest tests/test_api.py::test_root -v
```

## 📊 CI/CD

### GitHub Actions (exemple)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest tests/ --cov
```

## 🆘 Problèmes courants

### Import errors

```bash
# Ajouter le projet au PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:."
pytest tests/
```

### Tests qui skip

Les tests peuvent skip pour différentes raisons:
- Modèle non disponible
- Label Studio non lancé
- Données de test manquantes

Vérifier les messages avec `-v`

## 📚 Ressources

- [pytest documentation](https://docs.pytest.org/)
- [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Test coverage](https://coverage.readthedocs.io/)

---

**Dernière mise à jour:** 2024-01-15
