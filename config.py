"""
Configuration module for Z-Image-Turbo API
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# Get project root directory (where this config.py is located)
PROJECT_ROOT = Path(__file__).parent.absolute()


class Settings(BaseSettings):
    """Application settings"""

    # Model settings
    MODEL_PATH: str = "models/Z-Image-Turbo/INT4"  # Path to OpenVINO model
    DEVICE: str = "CPU"  # Options: CPU, GPU, AUTO

    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Image storage
    OUTPUT_DIR: str = "generated_images"  # Relative to project root
    MAX_STORED_IMAGES: int = 1000

    # Generation defaults
    DEFAULT_HEIGHT: int = 512
    DEFAULT_WIDTH: int = 512
    DEFAULT_STEPS: int = 9
    DEFAULT_GUIDANCE_SCALE: float = 0.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    def get_model_path(self) -> Path:
        """Get absolute path to OpenVINO model directory"""
        model_path = Path(self.MODEL_PATH)
        if model_path.is_absolute():
            return model_path
        return PROJECT_ROOT / self.MODEL_PATH

    def get_output_dir(self) -> Path:
        """Get absolute path to output directory"""
        return PROJECT_ROOT / self.OUTPUT_DIR


settings = Settings()

# Create directories if they don't exist
settings.get_output_dir().mkdir(exist_ok=True)
