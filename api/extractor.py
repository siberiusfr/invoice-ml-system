"""
Logique d'extraction de factures utilisant le modèle YOLO
"""
import os
import yaml
import torch
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
from PIL import Image
import fitz  # PyMuPDF
from datetime import datetime

from .models import ExtractedField, InvoiceExtraction, BoundingBox


class InvoiceExtractor:
    """Extracteur de données de factures"""

    def __init__(self, config_path: str = "config/settings.yaml"):
        """
        Initialiser l'extracteur

        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config = self._load_config(config_path)
        self.model = None
        self.model_version = "not_loaded"
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.confidence_threshold = self.config['api']['confidence_threshold']

        # Statistiques
        self.stats = {
            'total_extractions': 0,
            'total_confidence': 0.0,
            'extractions_today': 0,
            'last_reset': datetime.now().date()
        }

    def _load_config(self, config_path: str) -> dict:
        """Charger la configuration"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def load_model(self, model_path: Optional[str] = None):
        """
        Charger le modèle YOLO

        Args:
            model_path: Chemin vers le modèle entraîné
        """
        if model_path is None:
            # Chercher le dernier modèle entraîné
            models_dir = Path("data/models")
            if not models_dir.exists():
                raise FileNotFoundError("Aucun modèle trouvé. Entraînez d'abord un modèle.")

            model_files = list(models_dir.glob("*.pt"))
            if not model_files:
                raise FileNotFoundError("Aucun fichier .pt trouvé dans data/models/")

            # Prendre le plus récent
            model_path = max(model_files, key=os.path.getctime)

        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path)
            self.model_version = Path(model_path).stem
            print(f"✅ Modèle chargé: {model_path} (device: {self.device})")
        except Exception as e:
            raise RuntimeError(f"Erreur lors du chargement du modèle: {e}")

    def is_model_loaded(self) -> bool:
        """Vérifier si le modèle est chargé"""
        return self.model is not None

    def pdf_to_image(self, pdf_path: str) -> np.ndarray:
        """
        Convertir la première page d'un PDF en image

        Args:
            pdf_path: Chemin vers le PDF

        Returns:
            Image au format numpy array
        """
        doc = fitz.open(pdf_path)
        page = doc[0]  # Première page

        # Convertir en image avec bonne résolution
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)

        # Convertir RGBA en RGB si nécessaire
        if img.shape[2] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

        doc.close()
        return img

    def extract_from_file(self, file_path: str) -> InvoiceExtraction:
        """
        Extraire les données d'une facture

        Args:
            file_path: Chemin vers le fichier (PDF ou image)

        Returns:
            Données extraites
        """
        if not self.is_model_loaded():
            raise RuntimeError("Modèle non chargé. Appelez load_model() d'abord.")

        # Charger l'image
        file_extension = Path(file_path).suffix.lower()

        if file_extension == '.pdf':
            image = self.pdf_to_image(file_path)
        else:
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError(f"Impossible de lire l'image: {file_path}")

        # Prédiction
        results = self.model(image, verbose=False)[0]

        # Extraire les champs
        fields = []
        confidences = []

        for box in results.boxes:
            # Coordonnées normalisées (0-1)
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            h, w = image.shape[:2]

            bbox = BoundingBox(
                x=float(x1 / w),
                y=float(y1 / h),
                width=float((x2 - x1) / w),
                height=float((y2 - y1) / h)
            )

            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            label_name = results.names[class_id]

            # TODO: Implémenter OCR pour extraire le texte
            # Pour l'instant, on met une valeur placeholder
            value = f"[À extraire avec OCR]"

            field = ExtractedField(
                label=label_name,
                value=value,
                confidence=confidence,
                bbox=bbox
            )

            fields.append(field)
            confidences.append(confidence)

        # Calculer la confiance moyenne
        overall_confidence = np.mean(confidences) if confidences else 0.0
        needs_review = overall_confidence < self.confidence_threshold

        # Mettre à jour les stats
        self._update_stats(overall_confidence)

        return InvoiceExtraction(
            filename=Path(file_path).name,
            fields=fields,
            overall_confidence=float(overall_confidence),
            needs_review=needs_review,
            model_version=self.model_version
        )

    def _update_stats(self, confidence: float):
        """Mettre à jour les statistiques"""
        today = datetime.now().date()

        # Reset des stats journalières si nouveau jour
        if today != self.stats['last_reset']:
            self.stats['extractions_today'] = 0
            self.stats['last_reset'] = today

        self.stats['total_extractions'] += 1
        self.stats['total_confidence'] += confidence
        self.stats['extractions_today'] += 1

    def get_stats(self) -> Dict:
        """Obtenir les statistiques"""
        avg_confidence = (
            self.stats['total_confidence'] / self.stats['total_extractions']
            if self.stats['total_extractions'] > 0 else 0.0
        )

        return {
            'total_extractions': self.stats['total_extractions'],
            'average_confidence': avg_confidence,
            'extractions_last_24h': self.stats['extractions_today'],
            'model_version': self.model_version,
            'success_rate': 0.95  # TODO: Calculer basé sur le feedback
        }
