"""
Main entry point for Z-Image-Turbo API server
"""
import logging
import sys

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
    logger.info(f"Model ID: {settings.MODEL_ID}")
    logger.info(f"Device: {settings.DEVICE}")
    logger.info(f"INT4 Compression: {settings.USE_INT4_COMPRESSION}")
    logger.info(f"Server: http://{settings.API_HOST}:{settings.API_PORT}")
    logger.info("=" * 60)

    try:
        uvicorn.run(
            "api:app",
            host=settings.API_HOST,
            port=settings.API_PORT,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
