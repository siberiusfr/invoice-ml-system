# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an invoice data extraction system using Machine Learning (YOLO object detection + Tesseract OCR). The system follows a three-phase workflow:
1. **Phase 1 (Labelling)**: Annotate invoices in Label Studio
2. **Phase 2 (Training)**: Train YOLO model on annotated data
3. **Phase 3 (Production)**: Deploy REST API for automatic extraction

## Key Commands

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Or use Makefile
make install

# Create config file
cp config/settings.example.yaml config/settings.yaml
# Edit config/settings.yaml to add Label Studio API key

# Start Label Studio (Docker required)
docker-compose up -d
# or: make label-studio-start
```

### Testing
```bash
# Run all tests
pytest tests/ -v
# or: make test

# Run tests with coverage
pytest tests/ --cov=api --cov=training --cov-report=html
# or: make test-coverage

# Test API manually
python scripts/test_api.py
# or: make test-api

# Check dependencies
python scripts/check_dependencies.py
```

### Phase 1: Annotation Workflow
```bash
# Import invoices to Label Studio
python scripts/import_to_label_studio.py
# or: make import

# After annotation in Label Studio UI, export annotations
python scripts/export_from_label_studio.py
# or: make export
```

### Phase 2: Training Workflow
```bash
# 1. Prepare YOLO dataset from Label Studio exports
python scripts/prepare_dataset.py
# or: make prepare

# 2. Train YOLO model
python training/train_yolo.py
# or: make train

# With custom parameters
python training/train_yolo.py --epochs 200 --batch 32 --model yolov8s.pt

# Quick training (for testing)
make train-small

# 3. Evaluate model
python training/evaluate.py
# or: make evaluate
```

### Phase 3: API & Production
```bash
# Start API server
python api/app.py
# or: make api

# Development mode with auto-reload
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
# or: make api-dev

# Start monitoring dashboard
python monitoring/dashboard.py
# or: make dashboard

# Auto-retrain (dry run)
python scripts/auto_retrain.py --dry-run
# or: make auto-retrain-dry
```

## Architecture Overview

### Core Components

**API Layer** (`api/`)
- `app.py`: FastAPI application with endpoints for extraction, health checks, and model reloading
- `extractor.py`: Core extraction logic combining YOLO detection + Tesseract OCR
- `models.py`: Pydantic models for request/response validation

**Training Pipeline** (`training/`)
- `train_yolo.py`: YOLO training script with GPU/CPU support
- `train_layoutlm.py`: Alternative LayoutLM training (optional, more advanced)
- `evaluate.py`: Model evaluation and metrics

**Scripts** (`scripts/`)
- `import_to_label_studio.py`: Upload invoices to Label Studio
- `export_from_label_studio.py`: Download annotations from Label Studio
- `prepare_dataset.py`: Convert Label Studio format to YOLO format
- `auto_retrain.py`: Automated retraining when new annotations are available

**Data Flow**
```
Raw invoices (data/raw/invoices/)
    ↓
Label Studio annotation
    ↓
Export to JSON (data/exports/)
    ↓
Convert to YOLO format (data/processed/yolo_dataset/)
    ↓
Train model → Save to data/models/
    ↓
API loads model for inference
```

### Label Studio Integration

The system uses Label Studio SDK to:
- Import invoice images/PDFs for annotation
- Export annotations in Label Studio JSON format
- Implement feedback loop: low-confidence extractions are sent back to Label Studio

**Label Configuration**: `label-studio/invoice-template.xml` defines the annotation interface with these labels:
- `numero_facture`, `date_facture`
- `montant_ht`, `montant_tva`, `montant_ttc`
- `nom_fournisseur`, `adresse_fournisseur`
- `siret_fournisseur`, `ligne_produit`

### Extraction Pipeline (api/extractor.py)

1. **Image Preprocessing**: Convert PDF to image using PyMuPDF if needed
2. **YOLO Detection**: Detect bounding boxes for each invoice field
3. **OCR Extraction**: For each detected region:
   - Extract ROI from image
   - Preprocess: grayscale → resize → enhance contrast → denoise → binarize
   - Run Tesseract with field-specific configs
   - Post-process text based on field type (numbers, dates, etc.)
4. **Confidence Scoring**: Calculate overall confidence; flag for review if below threshold

### Configuration (config/settings.yaml)

Key settings to adjust:
- `label_studio.api_key`: Required for Label Studio integration
- `training.yolo.epochs`: Default 100, reduce for quick testing
- `api.confidence_threshold`: Default 0.85, extractions below this need review
- `api.feedback_loop.enabled`: Send low-confidence results back to Label Studio
- `dataset.split_ratios`: train/val/test split (0.8/0.1/0.1)

## Development Patterns

### Adding New Invoice Fields

1. Add label to `config/settings.yaml` in the `labels` list
2. Update Label Studio template: `label-studio/invoice-template.xml`
3. Re-export and retrain model with new annotations
4. Update OCR post-processing in `api/extractor.py::_extract_text_from_bbox()` if needed

### Model Versioning

Models are saved with timestamp: `invoice_model_YYYYMMDD_HHMMSS.pt`
- Latest model is auto-loaded by API from `data/models/`
- Use `/reload-model` endpoint to reload after training
- Model version is tracked in extraction responses

### Testing Strategy

- API tests: `tests/test_api.py` (FastAPI TestClient)
- Model tests: `tests/test_models.py` (Pydantic validation)
- Most tests run without trained model; some marked with `@pytest.mark.skipif`
- Manual testing: `scripts/test_api.py` sends real invoice to API

### Windows-Specific Notes

- `install.bat` provided for Windows setup
- Use `python` instead of `python3` on Windows
- Tesseract must be installed separately and added to PATH
- Docker Desktop required for Label Studio

## Common Development Tasks

### Debugging Low Extraction Accuracy
1. Check `data/models/invoice_yolo_*/` for training plots (confusion matrix, F1 curve)
2. Review confidence scores in API responses
3. Verify OCR preprocessing in `api/extractor.py::_extract_text_from_bbox()`
4. Ensure sufficient training data (100+ annotated invoices recommended)

### Updating Dependencies
```bash
pip install -r requirements.txt --upgrade
pip freeze > requirements.txt  # If you need to update versions
```

### Working with Label Studio API
```python
from label_studio_sdk import LabelStudio

# SDK version 2.0.15+ uses LabelStudio client
client = LabelStudio(base_url="http://localhost:8080", api_key="YOUR_KEY")
project = client.projects.get(id=PROJECT_ID)

# List tasks (returns Task objects)
tasks_obj = client.tasks.list(project=project.id)

# Convert to dictionaries if needed
tasks = [task.model_dump() for task in tasks_obj]

# Create tasks (one by one - no batch create in v2.0.15)
for task in tasks:
    client.tasks.create(project=project.id, data=task['data'], meta=task.get('meta'))
```

### Dataset Format Conversion
- Label Studio exports rectangles with `x, y, width, height` as percentages
- YOLO expects `class_id x_center y_center width height` normalized to [0,1]
- Conversion logic: `scripts/prepare_dataset.py::convert_label_studio_to_yolo()`

### Monitoring & Logs
- API logs: stdout (or configure in `monitoring.log_file`)
- Training logs: `data/models/invoice_yolo_*/` contains metrics and plots
- Dashboard: `monitoring/dashboard.py` provides real-time stats (port 8001)

## Important Constraints

- YOLO requires consistent image sizes (default 640px)
- Tesseract quality depends heavily on image preprocessing
- GPU strongly recommended for training (use Google Colab if unavailable)
- Label Studio requires Docker
- Minimum 100 annotated invoices for decent accuracy
- PDF processing uses first page only

## Project Structure Notes

- `venv/` is gitignored; virtual environment must be created locally
- `data/` structure: `raw/`, `processed/`, `models/`, `exports/` (mostly gitignored)
- Config file `config/settings.yaml` is gitignored (use `settings.example.yaml` as template)
- Makefile commands work on Unix systems; use Python commands directly on Windows
