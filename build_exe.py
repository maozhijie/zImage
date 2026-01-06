#!/usr/bin/env python
"""
Build executable for Z-Image-Turbo API using PyInstaller
"""
import argparse
import logging
import shutil
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.absolute()


def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("PyInstaller is not installed. Installing now...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            logger.info("PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            logger.error("Failed to install PyInstaller")
            return False


def create_pyinstaller_spec():
    """Create PyInstaller spec file"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Additional imports that PyInstaller might miss
hiddenimports = [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'openvino',
    'openvino.runtime',
    'optimum.intel',
    'optimum.intel.openvino',
    'PIL',
    'PIL._tkinter_finder',
]

# Data files to include
datas = [
    ('.env.example', '.'),
]

# Collect data files for libraries that need them
datas += collect_data_files('rfc3987_syntax')
datas += collect_data_files('jsonschema_specifications')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='zimage-api',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
"""

    spec_file = PROJECT_ROOT / "zimage-api.spec"
    spec_file.write_text(spec_content)
    logger.info(f"Created spec file: {spec_file}")
    return spec_file


def build_executable(spec_file: Path, clean: bool = False):
    """Build executable using PyInstaller"""
    logger.info("Building executable with PyInstaller...")

    cmd = ["pyinstaller"]
    if clean:
        cmd.append("--clean")
    cmd.append(str(spec_file))

    try:
        subprocess.run(cmd, cwd=PROJECT_ROOT, check=True)
        logger.info("Executable built successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to build executable: {e}")
        return False


def create_distribution_package(dist_dir: Path):
    """Create distribution package with exe and necessary files"""
    logger.info("Creating distribution package...")

    # Source and destination paths
    exe_file = PROJECT_ROOT / "dist" / "zimage-api.exe"
    package_dir = dist_dir / "zimage-turbo-api"

    if not exe_file.exists():
        logger.error(f"Executable not found: {exe_file}")
        return False

    # Remove existing package
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    # Create package directory
    package_dir.mkdir(parents=True, exist_ok=True)

    # Copy executable
    logger.info(f"Copying executable to {package_dir}")
    shutil.copy2(exe_file, package_dir / "zimage-api.exe")

    # Create models directory placeholder
    models_dir = package_dir / "models"
    models_dir.mkdir(exist_ok=True)

    # Check if models exist in source
    source_models = PROJECT_ROOT / "models"
    if source_models.exists():
        logger.info("Copying models directory...")
        for item in source_models.iterdir():
            if item.is_dir():
                shutil.copytree(item, models_dir / item.name)
            else:
                shutil.copy2(item, models_dir / item.name)
    else:
        # Create placeholder file
        (models_dir / "README.txt").write_text(
            "请将OpenVINO模型放置在此目录下\n"
            "例如: models/Z-Image-Turbo/INT4/\n\n"
            "Place your OpenVINO models in this directory\n"
            "Example: models/Z-Image-Turbo/INT4/\n"
        )

    # Create generated_images directory
    (package_dir / "generated_images").mkdir(exist_ok=True)

    # Copy .env.example if exists
    env_example = PROJECT_ROOT / ".env.example"
    if env_example.exists():
        shutil.copy2(env_example, package_dir / ".env.example")

    logger.info("Distribution package created successfully")
    return package_dir


def create_batch_scripts(package_dir: Path):
    """Create Windows batch scripts for starting/stopping the server"""
    logger.info("Creating batch scripts...")

    # Start server script
    start_script = package_dir / "start_server.bat"
    start_script.write_text("""@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ====================================================
echo Z-Image-Turbo API Server
echo ====================================================
echo.

REM Check if .env exists
if not exist ".env" (
    if exist ".env.example" (
        echo 首次运行: 复制配置文件...
        copy ".env.example" ".env"
        echo.
        echo 配置文件已创建: .env
        echo 请编辑 .env 文件配置模型路径和其他设置
        echo.
        echo Press any key to continue after editing .env...
        pause
    ) else (
        echo 错误: 未找到 .env.example 配置文件
        echo.
        pause
        exit /b 1
    )
)

REM Check if models directory exists
if not exist "models" (
    echo 警告: 未找到 models 目录
    mkdir models
    echo 请将OpenVINO模型放置在 models 目录下
    echo 例如: models\\Z-Image-Turbo\\INT4\\
    echo.
    pause
)

REM Start the server
echo 启动服务器...
echo.
start "Z-Image-Turbo API" /B cmd /c "zimage-api.exe > server.log 2>&1"

REM Wait a moment for server to start
timeout /t 3 /nobreak >nul

REM Check if server is running
tasklist /FI "IMAGENAME eq zimage-api.exe" 2>NUL | find /I /N "zimage-api.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo ✓ 服务器已启动
    echo.
    echo 服务器日志: server.log
    echo API地址: http://localhost:8000
    echo 健康检查: http://localhost:8000/health
    echo.
    echo 使用 stop_server.bat 停止服务器
) else (
    echo ✗ 服务器启动失败
    echo 请检查 server.log 查看错误信息
)

echo.
pause
""", encoding='utf-8')
    logger.info(f"  Created {start_script.name}")

    # Stop server script
    stop_script = package_dir / "stop_server.bat"
    stop_script.write_text("""@echo off
chcp 65001 >nul
setlocal

echo ====================================================
echo 停止 Z-Image-Turbo API Server
echo ====================================================
echo.

REM Check if server is running
tasklist /FI "IMAGENAME eq zimage-api.exe" 2>NUL | find /I /N "zimage-api.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo 正在停止服务器...
    taskkill /F /IM zimage-api.exe >nul 2>&1
    timeout /t 2 /nobreak >nul

    REM Verify it's stopped
    tasklist /FI "IMAGENAME eq zimage-api.exe" 2>NUL | find /I /N "zimage-api.exe">NUL
    if "%ERRORLEVEL%"=="0" (
        echo ✗ 无法停止服务器
    ) else (
        echo ✓ 服务器已停止
    )
) else (
    echo 服务器未运行
)

echo.
pause
""", encoding='utf-8')
    logger.info(f"  Created {stop_script.name}")

    # Check server status script
    status_script = package_dir / "check_status.bat"
    status_script.write_text("""@echo off
chcp 65001 >nul
setlocal

echo ====================================================
echo Z-Image-Turbo API Server Status
echo ====================================================
echo.

REM Check if server process is running
tasklist /FI "IMAGENAME eq zimage-api.exe" 2>NUL | find /I /N "zimage-api.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo 服务器状态: 运行中
    echo.

    REM Try to check health endpoint
    curl -s http://localhost:8000/health >nul 2>&1
    if "%ERRORLEVEL%"=="0" (
        echo API健康检查: ✓ 正常
        echo.
        curl -s http://localhost:8000/health
    ) else (
        echo API健康检查: ✗ 无响应
        echo 服务器可能正在启动中...
    )
) else (
    echo 服务器状态: 未运行
)

echo.
pause
""", encoding='utf-8')
    logger.info(f"  Created {status_script.name}")

    # Test API script
    test_script = package_dir / "test_api.bat"
    test_script.write_text("""@echo off
chcp 65001 >nul
setlocal

echo ====================================================
echo 测试 Z-Image-Turbo API
echo ====================================================
echo.

set API_URL=http://localhost:8000
set PROMPT=A beautiful sunset over mountains, photorealistic
set OUTPUT=test_image.png

echo API地址: %API_URL%
echo 提示词: %PROMPT%
echo 输出文件: %OUTPUT%
echo.

REM Check if curl is available
where curl >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 错误: curl 未安装
    echo 请使用 test_api.py 或手动测试API
    pause
    exit /b 1
)

REM Test health endpoint
echo [1/3] 测试健康检查端点...
curl -s -f %API_URL%/health >nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ 健康检查成功
) else (
    echo ✗ 服务器未响应，请先启动服务器
    pause
    exit /b 1
)
echo.

REM Test image generation
echo [2/3] 生成测试图像...
echo 这可能需要几秒钟...
curl -X POST "%API_URL%/generate/file" ^
     -H "Content-Type: application/json" ^
     -d "{\"prompt\":\"%PROMPT%\",\"height\":512,\"width\":512,\"num_inference_steps\":9,\"seed\":42}" ^
     -o "%OUTPUT%" ^
     --silent --show-error

if %ERRORLEVEL% EQU 0 (
    echo ✓ 图像生成成功
    echo 图像已保存到: %OUTPUT%
) else (
    echo ✗ 图像生成失败
)
echo.

REM Test URL generation
echo [3/3] 测试URL生成端点...
curl -X POST "%API_URL%/generate/url" ^
     -H "Content-Type: application/json" ^
     -d "{\"prompt\":\"%PROMPT%\",\"height\":512,\"width\":512,\"num_inference_steps\":9,\"seed\":42}" ^
     --silent

echo.
echo.
echo 测试完成
pause
""", encoding='utf-8')
    logger.info(f"  Created {test_script.name}")

    return True


def main():
    parser = argparse.ArgumentParser(description="Build Z-Image-Turbo API executable")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean PyInstaller cache before building"
    )
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Skip building, only create distribution package"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "release",
        help="Output directory for distribution package"
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Z-Image-Turbo API Executable Builder")
    logger.info("=" * 60)

    # Check PyInstaller
    if not args.skip_build:
        if not check_pyinstaller():
            return 1

        # Create spec file
        spec_file = create_pyinstaller_spec()

        # Build executable
        if not build_executable(spec_file, args.clean):
            logger.error("Failed to build executable")
            return 1

    # Create distribution package
    package_dir = create_distribution_package(args.output_dir)
    if not package_dir:
        logger.error("Failed to create distribution package")
        return 1

    # Create batch scripts
    if not create_batch_scripts(package_dir):
        logger.error("Failed to create batch scripts")
        return 1

    logger.info("\n" + "=" * 60)
    logger.info("Build completed successfully!")
    logger.info("=" * 60)
    logger.info(f"\nDistribution package: {package_dir}")
    logger.info("\n分发包内容:")
    logger.info("  - zimage-api.exe      主程序")
    logger.info("  - start_server.bat    启动服务器")
    logger.info("  - stop_server.bat     停止服务器")
    logger.info("  - check_status.bat    检查服务器状态")
    logger.info("  - test_api.bat        测试API")
    logger.info("  - .env.example        配置文件模板")
    logger.info("  - models/             模型目录")
    logger.info("  - generated_images/   生成图像目录")

    # Calculate package size
    total_size = sum(f.stat().st_size for f in package_dir.rglob('*') if f.is_file())
    logger.info(f"\n包大小: {total_size / 1024 / 1024:.2f} MB")

    logger.info("\n使用说明:")
    logger.info("  1. 将整个目录复制到目标机器")
    logger.info("  2. 配置 .env 文件（首次运行会自动创建）")
    logger.info("  3. 将OpenVINO模型放入 models 目录")
    logger.info("  4. 运行 start_server.bat 启动服务器")

    return 0


if __name__ == "__main__":
    sys.exit(main())
