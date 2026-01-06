"""
Image generation service for Z-Image-Turbo
"""
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import torch
from PIL import Image

from config import settings
from model_manager import get_model_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageGenerator:
    """Handles text-to-image generation"""

    def __init__(self):
        self.output_dir = settings.get_output_dir()
        self.output_dir.mkdir(exist_ok=True)
        self.model_manager = get_model_manager()
        self.pipeline = None

    def initialize(self):
        """Initialize the generator by loading the model"""
        if self.pipeline is None:
            logger.info("Initializing image generator...")
            self.pipeline = self.model_manager.initialize()
            logger.info("Image generator initialized")

    def generate_image(
        self,
        prompt: str,
        height: Optional[int] = None,
        width: Optional[int] = None,
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        seed: Optional[int] = None
    ) -> tuple[Image.Image, str]:
        """
        Generate an image from a text prompt

        Args:
            prompt: Text description of the image to generate
            height: Image height (default from settings)
            width: Image width (default from settings)
            num_inference_steps: Number of denoising steps (default from settings)
            guidance_scale: Guidance scale (default from settings, should be 0.0 for Turbo)
            seed: Random seed for reproducibility

        Returns:
            tuple: (PIL Image, image filename)
        """
        if self.pipeline is None:
            self.initialize()

        # Use defaults from settings if not provided
        height = height or settings.DEFAULT_HEIGHT
        width = width or settings.DEFAULT_WIDTH
        num_inference_steps = num_inference_steps or settings.DEFAULT_STEPS
        guidance_scale = guidance_scale if guidance_scale is not None else settings.DEFAULT_GUIDANCE_SCALE

        logger.info(f"Generating image with prompt: {prompt[:50]}...")
        logger.info(f"Parameters: {height}x{width}, steps={num_inference_steps}, "
                   f"guidance={guidance_scale}, seed={seed}")

        try:
            # Set up generator for reproducibility
            generator = None
            if seed is not None:
                generator = torch.Generator("cpu").manual_seed(seed)

            # Generate image
            result = self.pipeline(
                prompt=prompt,
                height=height,
                width=width,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator
            )

            image = result.images[0]

            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"image_{timestamp}_{unique_id}.png"
            filepath = self.output_dir / filename

            # Save image
            image.save(filepath)
            logger.info(f"Image saved to {filepath}")

            # Clean up old images if necessary
            self._cleanup_old_images()

            return image, filename

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise RuntimeError(f"Failed to generate image: {e}")

    def get_image_path(self, filename: str) -> Path:
        """Get full path for an image filename"""
        return self.output_dir / filename

    def _cleanup_old_images(self):
        """Remove oldest images if storage limit is exceeded"""
        try:
            images = sorted(
                self.output_dir.glob("*.png"),
                key=lambda p: p.stat().st_mtime
            )

            if len(images) > settings.MAX_STORED_IMAGES:
                num_to_delete = len(images) - settings.MAX_STORED_IMAGES
                for image_path in images[:num_to_delete]:
                    image_path.unlink()
                    logger.info(f"Deleted old image: {image_path.name}")

        except Exception as e:
            logger.warning(f"Failed to cleanup old images: {e}")


# Global generator instance
_generator: Optional[ImageGenerator] = None


def get_generator() -> ImageGenerator:
    """Get or create global image generator instance"""
    global _generator
    if _generator is None:
        _generator = ImageGenerator()
    return _generator
