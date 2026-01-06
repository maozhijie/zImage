"""
Main entry point for Z-Image-Turbo API server
"""
import logging
import sys
import inspect

# Monkey patch inspect.getsource to avoid errors with PyInstaller
# transformers/utils/doc.py uses inspect.getsource which fails in frozen apps
def _get_source_patch(obj):
    return " "

inspect.getsource = _get_source_patch

import uvicorn

from config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Start the API server"""
    logger.info("=" * 60)
    logger.info("Z-Image-Turbo API Server")
    logger.info("=" * 60)
    logger.info(f"Model Path: {settings.MODEL_PATH}")
    logger.info(f"Device: {settings.DEVICE}")
    logger.info(f"Server: http://{settings.API_HOST}:{settings.API_PORT}")
    logger.info("=" * 60)
    
    # Import app here to avoid circular imports and ensure it's loaded for PyInstaller
    from api import app

    try:
        uvicorn.run(
            app,
            host=settings.API_HOST,
            port=settings.API_PORT,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
