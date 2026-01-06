# 快速开始指南

## 开发环境快速启动

### Windows 用户
```cmd
start.bat
```

### Linux/Mac 用户
```bash
chmod +x start.sh
./start.sh
```

访问 http://localhost:8000 查看 API

## 生产环境打包部署

### 1. 准备打包（在开发机器上）

```bash
# 安装 uv
pip install uv

# 安装依赖
uv pip install -e .
uv pip install git+https://github.com/huggingface/diffusers
uv pip install git+https://github.com/openvino-dev-samples/optimum-intel.git@zimage

# 创建打包（会自动转换模型）
python package.py

# 生成文件：zimage-api-package.zip
```

### 2. 部署到生产机器

```bash
# 解压
unzip zimage-api-package.zip
cd zimage-package

# 确保安装了 uv
pip install uv

# 启动（自动安装依赖）
./start.sh      # Linux/Mac
start.bat       # Windows
```

## API 测试

```python
import requests

# 生成图片并获取文件
response = requests.post(
    "http://localhost:8000/generate/file",
    json={"prompt": "美丽的日落风景"}
)
with open("output.png", "wb") as f:
    f.write(response.content)

# 生成图片并获取URL
response = requests.post(
    "http://localhost:8000/generate/url",
    json={"prompt": "美丽的日落风景"}
)
print(response.json()["image_url"])
```

## 目录结构

```
项目根目录/
├── models/              # 模型存储（可配置）
│   └── Z-Image-Turbo/
│       └── INT4/        # 转换后的模型
├── generated_images/    # 生成的图片（可配置）
└── .venv/              # Python 虚拟环境
```

## 配置文件

复制 `.env.example` 为 `.env` 并修改：

```env
MODEL_PATH=models/Z-Image-Turbo/INT4  # OpenVINO 模型路径
OUTPUT_DIR=generated_images            # 图片输出位置
DEVICE=CPU                             # 或 GPU
```

## 常见问题

### 模型在哪里？
- 默认位置：`项目根目录/models/Z-Image-Turbo/INT4/`
- 可通过 `MODEL_PATH` 环境变量修改

### 如何使用 GPU？
```env
DEVICE=GPU
```

### 打包文件太大？
```bash
# 不包含模型打包（目标机器首次运行会自动下载转换）
python package.py --skip-models
```

### 切换 FP16 精度？
```env
MODEL_PATH=models/Z-Image-Turbo/FP16
```
确保你已有对应的 FP16 模型文件，然后重启服务。

## 性能参考

- 首次启动：10-30 秒（加载模型）
- 后续启动：10-30 秒
- 单张图片生成：5-15 秒（CPU），1-3 秒（GPU）
- 内存占用：8-16GB（INT4），16-32GB（FP16）
- 磁盘空间：3-5GB（INT4），6-10GB（FP16）
