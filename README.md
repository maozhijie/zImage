# Z-Image-Turbo API

--trust-remote-code
Text-to-image generation API using Alibaba's Z-Image-Turbo model with OpenVINO optimization.

## Features

- **Automatic Model Conversion**: Automatically detects and converts PyTorch models to OpenVINO format
- **INT4/FP16 Quantization**: Supports weight compression for reduced memory footprint
- **REST API**: Two endpoints for different use cases
  - Direct image file response
  - Image URL response with preview endpoint
- **High Performance**: Optimized with OpenVINO for fast inference on CPU/GPU
- **Easy Configuration**: Environment-based configuration with sensible defaults
- **UV Package Manager**: Fast dependency management with uv
- **Portable Packaging**: Create self-contained packages for easy deployment

## Requirements

- Python 3.8+
- At least 32GB RAM recommended for model conversion
- CPU or GPU with OpenVINO support
- uv package manager (recommended) or pip

## Quick Start

### Option 1: Using Quick Start Scripts (Recommended)

The easiest way to get started:

**Linux/Mac:**

```bash
chmod +x start.sh
./start.sh
```

**Windows:**

````cmd
start.bat
The script will automatically:
1. Install uv if needed
2. Create a virtual environment
3. Install all dependencies
4. Start the API server
2. 创建虚拟环境
### Option 2: Manual Installation with UV (Recommended)
4. 启动 API 服务器
#### 1. Install UV
### 选项 2：使用 UV 手动安装（推荐）

#### 1. 安装 UV

```bash
Or visit [uv documentation](https://github.com/astral-sh/uv) for other installation methods.
````

#### 2. Create Virtual Environment and Install Dependencies

或者访问 [uv 文档](https://github.com/astral-sh/uv) 查看其他安装方法。

# Create virtual environment

```bash
# Activate it
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install project dependencies
source .venv/bin/activate  # Windows 上使用: .venv\Scripts\activate

# Install git dependencies (required for Z-Image-Turbo support)
uv pip install -e .

# 安装 git 依赖（Z-Image-Turbo 支持所需）
uv pip install git+https://github.com/huggingface/diffusers
#### 3. Run the Server
```

#### 3. 运行服务器

```bash
### Option 3: Using pip
```

# Create virtual environment

source venv/bin/activate # On Windows: venv\Scripts\activate

# 创建虚拟环境

# Install dependencies

source venv/bin/activate # Windows 上使用: venv\Scripts\activate

# Run the server

pip install -r requirements.txt

# 运行服务器

### 4. Configure Settings (Optional)

````
Create a `.env` file in the project root to customize settings:
### 4. 配置设置（可选）

# Model settings

```env
# 模型设置
# 直接指定 OpenVINO 模型的路径
MODEL_PATH=models/Z-Image-Turbo/INT4
# API settings
DEVICE=CPU

# API 设置
# Image storage
API_PORT=8000

# 图片存储
# Generation defaults
MAX_STORED_IMAGES=1000

# 生成默认值
DEFAULT_HEIGHT=512
DEFAULT_WIDTH=512
DEFAULT_STEPS=9
## Creating Portable Package (Deploy Anywhere)
````

You can create a self-contained package that includes the converted models and all dependencies. This package can be extracted and run on any machine without internet access.

## 创建便携式安装包（随处部署）

### 1. Build the Package

您可以创建一个包含已转换模型和所有依赖项的自包含安装包。该安装包可以解压并在任何机器上运行，无需互联网访问。

# Install dependencies first

````bash
# 首先安装依赖
uv pip install -e .
# Run packaging script (this will convert models if needed)
uv pip install git+https://github.com/openvino-dev-samples/optimum-intel.git@zimage

# Or create tar.gz for Linux
python package.py

# Or create both formats
python package.py --format tar.gz

# Skip model conversion if you want a lighter package
python package.py --format both

# 如果想要更轻量的包，可以跳过模型转换
The packaging process will:
1. Check if models are converted (and convert them if needed)
2. Copy all source files
3. Copy converted models
4. Export dependencies to requirements.txt
5. Create startup scripts for all platforms
6. Create a compressed archive (zip or tar.gz)
3. 复制已转换的模型
**Package size**: ~3-5GB with INT4 models, ~1-2GB without models
5. 为所有平台创建启动脚本
### 2. Deploy the Package

**On the target machine:**

### 2. 部署安装包
# Extract the package
**在目标机器上：**

```bash
# Run the startup script
unzip zimage-api-package.zip
# or

# 运行启动脚本
./start.sh  # Linux/Mac
The startup script will:
1. Check if uv is installed
2. Create a virtual environment (if needed)
3. Install dependencies from requirements.txt
4. Start the API server

**That's it!** No model conversion needed on the target machine.
2. 创建虚拟环境（如果需要）
### Package Options
4. 启动 API 服务器
- `--format`: Choose archive format (`zip`, `tar.gz`, or `both`)
- `--skip-models`: Skip model conversion (package will download models on first run)
- `--output-dir`: Custom output directory for the package
### 打包选项
## Usage
- `--format`：选择归档格式（`zip`, `tar.gz`, 或 `both`）
### Start the API Server
- `--output-dir`：自定义安装包输出目录

## 使用方法

### 启动 API 服务器
**First Run**: The server will automatically download and convert the model to OpenVINO format. This process may take 10-30 minutes depending on your hardware. Subsequent runs will use the cached converted model.
```bash
The server will start at `http://localhost:8000` by default.
````

### API Endpoints

**首次运行**：服务器将自动下载模型并将其转换为 OpenVINO 格式。根据您的硬件情况，此过程可能需要 10-30 分钟。后续运行将使用缓存的已转换模型。

#### 1. Generate and Return Image File

默认情况下，服务器将在 `http://localhost:8000` 启动。
**Endpoint**: `POST /generate/file`

### API 端点

Returns the generated image directly as a file.

#### 1. 生成并返回图片文件

**Example**:
**端点**：`POST /generate/file`

直接以文件形式返回生成的图片。

**示例**：

```bash
curl -X POST "http://localhost:8000/generate/file" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful sunset over mountains",
    "height": 512,
    "width": 512,
    "num_inference_steps": 9,
**Python Example**:
  }' \
  --output image.png
```

**Python 示例**：

```python
import requests

response = requests.post(
    "http://localhost:8000/generate/file",
    json={
        "prompt": "A beautiful sunset over mountains",
        "height": 512,
        "width": 512,
        "num_inference_steps": 9,
        "seed": 42
    }
)
#### 2. Generate and Return Image URL
with open("image.png", "wb") as f:
**Endpoint**: `POST /generate/url`
```

Returns URLs to access the generated image.

#### 2. 生成并返回图片 URL

**Example**:
**端点**：`POST /generate/url`

返回访问生成图片的 URL。

**示例**：

```bash
curl -X POST "http://localhost:8000/generate/url" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful sunset over mountains",
    "height": 512,
**Response**:
    "seed": 42
  }'
```

**响应**：

```json
{
  "success": true,
  "message": "Image generated successfully",
  "image_url": "http://localhost:8000/images/image_20260104_143022_a1b2c3d4.png",
**Python Example**:
  "preview_url": "http://localhost:8000/images/image_20260104_143022_a1b2c3d4.png"
}
```

**Python 示例**：

```python
import requests

response = requests.post(
    "http://localhost:8000/generate/url",
    json={
        "prompt": "A beautiful sunset over mountains",
        "height": 512,
        "width": 512,
        "seed": 42
    }
)

result = response.json()
#### 3. Preview Image
    print(f"Image URL: {result['image_url']}")
**Endpoint**: `GET /images/{filename}`
```

View a previously generated image.

#### 3. 预览图片

**Example**:
**端点**：`GET /images/{filename}`

查看之前生成的图片。

**示例**：
Or simply open the URL in a browser.

```bash
#### 4. Health Check
```

**Endpoint**: `GET /health`
或者直接在浏览器中打开 URL。
Check if the API is running.

#### 4. 健康检查

**端点**：`GET /health`

检查 API 是否正在运行。

### Request Parameters

```bash
| Parameter | Type | Required | Default | Description |
```

| `prompt` | string | Yes | - | Text description of the image to generate |
| `height` | integer | No | 512 | Image height (256-1024) |
| `width` | integer | No | 512 | Image width (256-1024) |
| `num_inference_steps` | integer | No | 9 | Number of denoising steps (1-50) |
| `guidance_scale` | float | No | 0.0 | Guidance scale (0.0-10.0, use 0.0 for Turbo) |
| `seed` | integer | No | random | Random seed for reproducibility |
| `height` | integer | 否 | 512 | 图片高度 (256-1024) |

### Interactive API Documentation

| `num_inference_steps` | integer | 否 | 9 | 去噪步数 (1-50) |
FastAPI automatically generates interactive API documentation:
| `seed` | integer | 否 | 随机 | 用于复现的随机种子 |

### 交互式 API 文档

## Project Structure

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
  ├── main.py # Main entry point
  ├── api.py # FastAPI application and endpoints
  ├── generator.py # Image generation service
  ├── model_manager.py # Model conversion and loading
  ├── config.py # Configuration settings
  ├── package.py # Packaging script for deployment
  ├── test_api.py # API testing script
  ├── pyproject.toml # Project metadata and dependencies (uv)
  ├── requirements.txt # Python dependencies (pip)
  ├── start.sh # Linux/Mac startup script
  ├── start.bat # Windows startup script
  ├── .env.example # Example environment variables
  ├── .env # Environment variables (create from .env.example)
  ├── README.md # This file
  ├── generated_images/ # Output directory for images
  ├── models/ # Converted OpenVINO models
  ├── .env.example # 环境变量示例
  │ ├── INT4/ # INT4 quantized models
  │ └── FP16/ # FP16 models
  └── .venv/ # Virtual environment (created by uv/venv)
  ├── models/ # 已转换的 OpenVINO 模型
  │ └── Z-Image-Turbo/

## Model Conversion

The model conversion happens automatically on first run. If you want to manually trigger conversion or switch between INT4 and FP16:

1. **Delete the model directory**:

## 模型切换

如果您想在 INT4 和 FP16 模型之间切换：

1. **确保您已有对应的模型文件**（INT4 或 FP16）

2. **更新配置** 在 `.env` 中：

   ```env
   # 使用 INT4
   MODEL_PATH=models/Z-Image-Turbo/INT4

   # 或使用 FP16
   MODEL_PATH=models/Z-Image-Turbo/FP16
   ```

3. **重启服务**

## Performance Tips

- **INT4 Quantization**: Reduces memory usage significantly with minimal quality loss
- **CPU Inference**: Works well on modern CPUs with AVX2/AVX512
- **GPU Inference**: Set `DEVICE=GPU` in `.env` for GPU acceleration
- **Batch Processing**: Generate multiple images sequentially through the API

## Troubleshooting

### Model Conversion Fails

### Model Loading Fails

If model loading fails:

1. Ensure your OpenVINO model exists at the path specified in `MODEL_PATH`
2. Check that the model directory contains required files (openvino_model.xml, etc.)
3. Verify you have enough RAM for the model size

### Out of Memory

If you encounter OOM errors:

1. Use INT4 model: `MODEL_PATH=models/Z-Image-Turbo/INT4`
2. Reduce image size in generation requests
3. Close other applications to free up memory

### Slow Generation

If generation is slow:

1. First generation is always slower (model loading)
2. Consider using GPU: `DEVICE=GPU`
3. Reduce `num_inference_steps` (minimum 4-5 recommended)

## License

This project uses the Z-Image-Turbo model from Tongyi-MAI. Please refer to the [model card](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo) for license information.

## Acknowledgments

1. 第一次生成总是较慢（模型加载）
2. 考虑使用 GPU：`DEVICE=GPU`
3. 减少 `num_inference_steps`（推荐最少 4-5 步）

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 致谢

- [Z-Image-Turbo](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo) by Tongyi-MAI
- [OpenVINO](https://github.com/openvinotoolkit/openvino) by Intel
- [Optimum Intel](https://github.com/huggingface/optimum-intel) by Hugging Face

## 贡献

欢迎贡献！请随时提交 issue 或 pull request。
