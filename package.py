#!/usr/bin/env python
"""
Package script for Z-Image-Turbo API
Creates a portable package with models and dependencies
"""
import argparse
import logging
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Project root
PROJECT_ROOT = Path(__file__).parent.absolute()


def check_uv_installed():
    """Check if uv is installed"""
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("uv is not installed. Please install it first:")
        logger.error("  pip install uv")
        logger.error("  or visit: https://github.com/astral-sh/uv")
        return False


def ensure_models_converted():
    """Ensure OpenVINO models are converted"""
    from config import settings
    from model_manager import get_model_manager

    logger.info("Checking if models are converted...")
    model_manager = get_model_manager()

    if not model_manager.check_model_exists():
        logger.info("Models not found. Starting conversion...")
        logger.info("This may take 10-30 minutes depending on your hardware...")
        try:
            model_manager.convert_model()
            logger.info("Model conversion completed successfully")
        except Exception as e:
            logger.error(f"Model conversion failed: {e}")
            return False
    else:
        logger.info("Models already converted")

    return True


def create_package_structure(package_dir: Path):
    """Create package directory structure"""
    logger.info(f"Creating package structure in {package_dir}")

    # Remove existing package directory
    if package_dir.exists():
        logger.info(f"Removing existing package directory...")
        shutil.rmtree(package_dir)

    package_dir.mkdir(parents=True)

    # Copy source files
    logger.info("Copying source files...")
    source_files = [
        "main.py",
        "api.py",
        "generator.py",
        "model_manager.py",
        "config.py",
        "pyproject.toml",
        "README.md",
        ".env.example",
    ]

    for file in source_files:
        src = PROJECT_ROOT / file
        if src.exists():
            shutil.copy2(src, package_dir / file)
            logger.info(f"  Copied {file}")

    # Copy models directory
    models_dir = PROJECT_ROOT / "models"
    if models_dir.exists():
        logger.info("Copying models directory...")
        shutil.copytree(models_dir, package_dir / "models")
        logger.info(f"  Models directory copied")
    else:
        logger.warning("Models directory not found. Package will need to download models on first run.")

    # Create output directory placeholder
    (package_dir / "generated_images").mkdir(exist_ok=True)
    (package_dir / "generated_images" / ".gitkeep").touch()

    return True


def export_dependencies(package_dir: Path):
    """Export dependencies using uv"""
    logger.info("Exporting dependencies with uv...")

    try:
        # Export to requirements.txt
        requirements_file = package_dir / "requirements.txt"
        result = subprocess.run(
            ["uv", "pip", "compile", "pyproject.toml", "-o", str(requirements_file)],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"  Dependencies exported to requirements.txt")

        # Also copy pyproject.toml for uv sync
        shutil.copy2(PROJECT_ROOT / "pyproject.toml", package_dir / "pyproject.toml")

        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to export dependencies: {e}")
        logger.error(e.stderr)
        return False


def create_startup_scripts(package_dir: Path):
    """Create startup scripts for different platforms"""
    logger.info("Creating startup scripts...")

    # Unix/Linux/Mac startup script
    startup_sh = package_dir / "start.sh"
    startup_sh.write_text("""#!/bin/bash
set -e

echo "===================================================="
echo "Z-Image-Turbo API - Starting..."
echo "===================================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "ERROR: uv is not installed"
    echo "Please install uv first:"
    echo "  pip install uv"
    echo "  or visit: https://github.com/astral-sh/uv"
    exit 1
fi

# Install dependencies if .venv doesn't exist
if [ ! -d ".venv" ]; then
    echo "Installing dependencies..."
    uv venv
    uv pip sync requirements.txt
fi

# Activate virtual environment and run
echo "Starting API server..."
source .venv/bin/activate
python main.py
""")
    startup_sh.chmod(0o755)
    logger.info("  Created start.sh")

    # Windows startup script
    startup_bat = package_dir / "start.bat"
    startup_bat.write_text("""@echo off
setlocal

echo ====================================================
echo Z-Image-Turbo API - Starting...
echo ====================================================

REM Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: uv is not installed
    echo Please install uv first:
    echo   pip install uv
    echo   or visit: https://github.com/astral-sh/uv
    pause
    exit /b 1
)

REM Install dependencies if .venv doesn't exist
if not exist ".venv" (
    echo Installing dependencies...
    uv venv
    uv pip sync requirements.txt
)

REM Activate virtual environment and run
echo Starting API server...
call .venv\\Scripts\\activate.bat
python main.py

pause
""")
    logger.info("  Created start.bat")

    return True


def create_archive(package_dir: Path, output_format: str = "zip"):
    """Create compressed archive of the package"""
    logger.info(f"Creating {output_format} archive...")

    archive_name = f"zimage-api-package"

    if output_format == "zip":
        archive_path = PROJECT_ROOT / f"{archive_name}.zip"
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in package_dir.rglob('*'):
                if file.is_file():
                    arcname = file.relative_to(package_dir.parent)
                    zipf.write(file, arcname)
        logger.info(f"  Created {archive_path}")
    elif output_format == "tar.gz":
        archive_path = PROJECT_ROOT / f"{archive_name}.tar.gz"
        with tarfile.open(archive_path, 'w:gz') as tar:
            tar.add(package_dir, arcname=package_dir.name)
        logger.info(f"  Created {archive_path}")
    else:
        logger.error(f"Unsupported archive format: {output_format}")
        return None

    return archive_path


def main():
    parser = argparse.ArgumentParser(description="Package Z-Image-Turbo API")
    parser.add_argument(
        "--format",
        choices=["zip", "tar.gz", "both"],
        default="zip",
        help="Archive format (default: zip)"
    )
    parser.add_argument(
        "--skip-models",
        action="store_true",
        help="Skip model conversion (models will be downloaded on first run)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "zimage-package",
        help="Output directory for package (default: ./zimage-package)"
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Z-Image-Turbo API Packaging Tool")
    logger.info("=" * 60)

    # Check prerequisites
    if not check_uv_installed():
        return 1

    # Ensure models are converted
    if not args.skip_models:
        if not ensure_models_converted():
            logger.error("Failed to ensure models are converted")
            return 1
    else:
        logger.warning("Skipping model conversion. Package will download models on first run.")

    # Create package structure
    if not create_package_structure(args.output_dir):
        logger.error("Failed to create package structure")
        return 1

    # Export dependencies
    if not export_dependencies(args.output_dir):
        logger.error("Failed to export dependencies")
        return 1

    # Create startup scripts
    if not create_startup_scripts(args.output_dir):
        logger.error("Failed to create startup scripts")
        return 1

    # Create archives
    if args.format in ["zip", "both"]:
        archive_path = create_archive(args.output_dir, "zip")
        if archive_path:
            logger.info(f"\nPackage created: {archive_path}")
            logger.info(f"Size: {archive_path.stat().st_size / 1024 / 1024:.2f} MB")

    if args.format in ["tar.gz", "both"]:
        archive_path = create_archive(args.output_dir, "tar.gz")
        if archive_path:
            logger.info(f"\nPackage created: {archive_path}")
            logger.info(f"Size: {archive_path.stat().st_size / 1024 / 1024:.2f} MB")

    logger.info("\n" + "=" * 60)
    logger.info("Packaging completed successfully!")
    logger.info("=" * 60)
    logger.info("\nTo use the package:")
    logger.info("  1. Extract the archive on the target machine")
    logger.info("  2. Run start.sh (Linux/Mac) or start.bat (Windows)")
    logger.info("  3. The server will start at http://localhost:8000")

    return 0


if __name__ == "__main__":
    sys.exit(main())
