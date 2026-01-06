"""
Model loading manager for Z-Image-Turbo with OpenVINO
"""
import logging
from typing import Optional

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelManager:
    """Manages OpenVINO model loading"""

    def __init__(self):
        self.model_path = settings.get_model_path()
        self.device = settings.DEVICE
        self.pipeline = None

    def load_model(self):
        """Load OpenVINO model pipeline"""
        if self.pipeline is not None:
            logger.info("Model already loaded")
            return self.pipeline

        try:
            from optimum.intel import OVZImagePipeline

            logger.info(f"Loading OpenVINO model from {self.model_path}")
            logger.info(f"Using device: {self.device}")

            self.pipeline = OVZImagePipeline.from_pretrained(
                str(self.model_path),
                device=self.device
            )

            logger.info("Model loaded successfully")
            return self.pipeline

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise RuntimeError(f"Failed to load model from {self.model_path}: {e}")

    def initialize(self):
        """Initialize model by loading it"""
        return self.load_model()

    def get_pipeline(self):
        """Get the loaded pipeline instance"""
        if self.pipeline is None:
            return self.initialize()
        return self.pipeline


# Global model manager instance
_model_manager: Optional[ModelManager] = None


def get_model_manager() -> ModelManager:
    """Get or create global model manager instance"""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager


def initialize_model():
    """Initialize and return the model pipeline"""
    manager = get_model_manager()
    return manager.initialize()
