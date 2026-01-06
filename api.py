"""
FastAPI application for Z-Image-Turbo text-to-image generation
"""
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

from config import settings
from generator import get_generator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Z-Image-Turbo API",
    description="Text-to-image generation API using Z-Image-Turbo with OpenVINO",
    version="1.0.0"
)


class GenerationRequest(BaseModel):
    """Request model for image generation"""
    prompt: str = Field(..., description="Text prompt for image generation")
    height: Optional[int] = Field(None, description="Image height in pixels", ge=256, le=1024)
    width: Optional[int] = Field(None, description="Image width in pixels", ge=256, le=1024)
    num_inference_steps: Optional[int] = Field(None, description="Number of inference steps", ge=1, le=50)
    guidance_scale: Optional[float] = Field(None, description="Guidance scale (0.0 for Turbo models)", ge=0.0, le=10.0)
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")


class GenerationResponse(BaseModel):
    """Response model with image URL"""
    success: bool
    message: str
    image_url: Optional[str] = None
    filename: Optional[str] = None
    preview_url: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize model on startup"""
    logger.info("Starting Z-Image-Turbo API...")
    logger.info("Initializing model (this may take a while)...")
    try:
        generator = get_generator()
        generator.initialize()
        logger.info("Model initialized successfully")
        logger.info(f"API server ready on http://{settings.API_HOST}:{settings.API_PORT}")
    except Exception as e:
        logger.error(f"Failed to initialize model: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Z-Image-Turbo API",
        "version": "1.0.0",
        "endpoints": {
            "generate_file": "/generate/file - Generate and return image file directly",
            "generate_url": "/generate/url - Generate and return image URL",
            "preview": "/images/{filename} - Preview generated image",
            "health": "/health - Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/generate/file", response_class=FileResponse)
async def generate_image_file(request: GenerationRequest):
    """
    Generate image and return the file directly

    This endpoint generates an image and returns it as a file response.
    """
    try:
        logger.info(f"Received file generation request: {request.prompt[:50]}...")

        generator = get_generator()
        image, filename = generator.generate_image(
            prompt=request.prompt,
            height=request.height,
            width=request.width,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
            seed=request.seed
        )

        filepath = generator.get_image_path(filename)

        return FileResponse(
            path=str(filepath),
            media_type="image/png",
            filename=filename,
            headers={
                "X-Generated-Filename": filename
            }
        )

    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")


@app.post("/generate/url", response_model=GenerationResponse)
async def generate_image_url(request: GenerationRequest, http_request: Request):
    """
    Generate image and return URL for preview

    This endpoint generates an image and returns URLs to access it.
    """
    try:
        logger.info(f"Received URL generation request: {request.prompt[:50]}...")

        generator = get_generator()
        image, filename = generator.generate_image(
            prompt=request.prompt,
            height=request.height,
            width=request.width,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.guidance_scale,
            seed=request.seed
        )

        # Construct URLs
        base_url = str(http_request.base_url).rstrip('/')
        image_url = f"{base_url}/images/{filename}"
        preview_url = image_url  # Same URL for preview

        return GenerationResponse(
            success=True,
            message="Image generated successfully",
            image_url=image_url,
            filename=filename,
            preview_url=preview_url
        )

    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        return GenerationResponse(
            success=False,
            message=f"Image generation failed: {str(e)}"
        )


@app.get("/images/{filename}")
async def preview_image(filename: str):
    """
    Preview generated image

    This endpoint serves the generated image file for preview.
    """
    try:
        generator = get_generator()
        filepath = generator.get_image_path(filename)

        if not filepath.exists():
            raise HTTPException(status_code=404, detail="Image not found")

        return FileResponse(
            path=str(filepath),
            media_type="image/png",
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to serve image: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to serve image: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False
    )
