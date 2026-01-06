# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Z-Image-Turbo is a FastAPI-based text-to-image generation API that uses Intel's OpenVINO-optimized Z-Image-Turbo diffusion model. The project is designed to run high-performance inference on CPU/GPU using OpenVINO IR format models.

## Key Dependencies

- **OpenVINO** (>= 2025.4): Core inference runtime
- **PyTorch** (2.8): Model operations and random number generation
- **Diffusers**: Installed from source (`git+https://github.com/huggingface/diffusers`)
- **Optimum Intel**: Custom fork with Z-Image support (`git+https://github.com/openvino-dev-samples/optimum-intel.git@zimage`)
- **FastAPI** + **Uvicorn**: API server framework

## Environment Setup

1. **Configuration**: Copy `.env.example` to `.env` and configure:
   - `MODEL_PATH`: Path to OpenVINO model directory (e.g., `models/Z-Image-Turbo/INT4`)
   - `DEVICE`: Inference device (`CPU`, `GPU`, or `AUTO`)
   - API and image generation settings

2. **Verify configuration**:
   ```bash
   python check_env.py
   ```

3. **Install dependencies** (Windows):
   ```bash
   start.bat
   ```

   Or manually:
   ```bash
   uv venv --python=3.12
   .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

## Common Commands

### Run the API Server
```bash
python main.py
```
Server will start on `http://0.0.0.0:8000` (configurable via `.env`)

### Test the API
```bash
# Run all tests
python test_api.py

# Test specific endpoint
python test_api.py --test health
python test_api.py --test file --prompt "A futuristic city at night"
python test_api.py --test url

# Custom API URL
python test_api.py --url http://localhost:8000
```

### Test Configuration
```bash
python test_config.py
```

### Check Environment
```bash
python check_env.py
```

## Architecture

### Core Components

1. **config.py** (`Settings` class)
   - Pydantic-based configuration management
   - Loads from `.env` file using `pydantic-settings`
   - Provides helper methods: `get_model_path()` returns absolute path to OpenVINO model, `get_output_dir()` returns absolute path to image storage
   - All paths support both absolute and relative (to project root) configuration

2. **model_manager.py** (`ModelManager` class)
   - Singleton pattern via `get_model_manager()` global function
   - Lazy-loads the `OVZImagePipeline` from Optimum Intel
   - Pipeline is cached in `self.pipeline` after first load
   - Device configuration passed to OpenVINO from settings

3. **generator.py** (`ImageGenerator` class)
   - Singleton pattern via `get_generator()` global function
   - Wraps `ModelManager` and handles image generation workflow
   - Manages image storage with automatic cleanup (respects `MAX_STORED_IMAGES` limit)
   - Generates unique filenames: `image_YYYYMMDD_HHMMSS_{uuid}.png`
   - Supports reproducible generation via seed parameter

4. **api.py** (FastAPI application)
   - Two generation endpoints:
     - `POST /generate/file`: Returns image file directly as `FileResponse`
     - `POST /generate/url`: Returns JSON with URL to generated image
   - `GET /images/{filename}`: Serves generated images for preview
   - Model initialization happens in `startup_event()` to ensure model is loaded before accepting requests
   - Uses singleton generator via `get_generator()`

### Request Flow

1. API request arrives → `api.py` endpoint
2. Endpoint calls `get_generator()` → returns singleton `ImageGenerator`
3. `ImageGenerator.generate_image()` called → lazy-initializes if needed
4. Generator calls `ModelManager.get_pipeline()` → returns `OVZImagePipeline`
5. Pipeline generates image → returns PIL Image
6. Generator saves to disk → returns (image, filename)
7. API endpoint returns file or URL response

### Singleton Pattern

Both `ModelManager` and `ImageGenerator` use global singleton instances to ensure:
- Model is loaded only once per process
- Memory efficiency (OpenVINO models can be large)
- Consistent state across API requests

### Model Path Resolution

The project uses a consistent path resolution strategy (implemented in `config.py`):
- `MODEL_PATH` in `.env` can be absolute or relative
- If relative, it's resolved against `PROJECT_ROOT` (directory containing `config.py`)
- `get_model_path()` always returns an absolute `Path` object
- This allows flexible deployment (development, production, Docker, etc.)

## Image Generation Parameters

- **prompt** (required): Text description
- **height/width**: 256-1024px (default: 512x512)
- **num_inference_steps**: 1-50 steps (default: 9 for Turbo models)
- **guidance_scale**: 0.0-10.0 (default: 0.0 for Turbo - CFG-free distillation)
- **seed**: Optional int for reproducibility

Z-Image-Turbo is a distilled model optimized for guidance_scale=0.0, which enables fast, single-pass generation.

## Testing Strategy

The codebase includes test files but they are primarily integration tests:
- `test_api.py`: End-to-end API testing (requires running server)
- `test_config.py`: Configuration validation
- `test_load_model.py`: Model loading verification
- `check_env.py`: Environment setup verification
- `client_test.py`: Standalone API client for testing (supports interactive mode)

When modifying code, ensure tests still pass and the API server starts successfully.

## Building and Packaging

### Executable Packaging (Windows)

The project includes tools to package the API as a standalone Windows executable:

**Build Script**: `build_exe.py`
- Uses PyInstaller to create standalone exe
- Bundles all Python dependencies
- Creates complete distribution package with helper scripts
- Output: `release/zimage-turbo-api/` directory

**Build Command**:
```bash
python build_exe.py --clean
```

**Distribution Package Contents**:
- `zimage-api.exe` - Main executable (no Python required)
- `start_server.bat` - Start API server in background
- `stop_server.bat` - Stop running server
- `check_status.bat` - Check server status and health
- `test_api.bat` - Quick API test using curl
- `.env.example` - Configuration template
- `models/` - Directory for OpenVINO models
- `generated_images/` - Output directory for generated images
- `_internal/` - Bundled runtime dependencies (don't modify)

**Helper Scripts in Distribution**:
- All batch scripts handle UTF-8 encoding for Chinese characters
- `start_server.bat` runs exe in background, logs to `server.log`
- Scripts check for process existence and provide user-friendly feedback
- Auto-creates `.env` from `.env.example` on first run

**Documentation**:
- `BUILD.md` - Detailed build instructions for developers
- `DEPLOYMENT.md` - End-user deployment and usage guide
- `PACKAGING_QUICKSTART.md` - Quick reference for both builders and users

**Key Considerations**:
- PyInstaller spec includes hidden imports for uvicorn, openvino, and optimum-intel
- Console mode enabled to show server logs
- UPX compression enabled to reduce file size
- Models are NOT bundled in exe (distributed separately)
