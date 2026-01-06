# Z-Image-Turbo

**Z-Image-Turbo** 是一个基于 **Intel OpenVINO™** 和 **FastAPI** 构建的高性能文本生成图像（Text-to-Image）API 服务。

专为 Windows 平台优化，利用 OpenVINO 对 Intel 硬件（CPU/GPU/NPU）的深度加速能力，支持 **INT4/FP16** 模型量化，在保持高质量生成的同时显著降低内存占用和推理延迟。

---

## ✨ 核心特性

- 🚀 **高性能推理**：集成 `optimum-intel` 和 `OpenVINO`，针对 Intel 硬件架构进行极致优化。
- 💾 **资源高效**：原生支持 INT4/FP16 模型量化，在消费级硬件上也能流畅运行大模型。
- 🔌 **标准 API**：基于 FastAPI 提供易用的 RESTful 接口，支持 Swagger UI 文档。
- 📦 **一键部署**：提供 `start.bat` 自动化脚本和 PyInstaller 打包工具，开箱即用。
- 🛠️ **灵活配置**：支持通过 `.env` 文件灵活配置模型路径、推理设备（CPU/GPU）和生成参数。

---

## 🚀 快速开始

### 前置要求

- **操作系统**: Windows 10 或 Windows 11
- **Python**: 3.12 或更高版本
- **硬件**: 建议使用 Intel CPU (Core i5/i7/i9) 或 Intel Arc GPU

### 安装与运行

#### 方法一：使用自动化脚本（推荐）

我们提供了一个一键启动脚本，会自动检测并安装 `uv` 包管理器、创建虚拟环境并启动服务。

1.  克隆本仓库：
    ```bash
    git clone <repository-url>
    cd zImage
    ```
2.  双击运行 **`start.bat`**。

#### 方法二：手动安装

如果你更喜欢手动管理环境：

```bash
# 1. 安装 uv (如果尚未安装)
pip install uv

# 2. 创建虚拟环境
uv venv

# 3. 激活环境
.venv\Scripts\activate

# 4. 安装依赖
uv pip install -r requirements.txt

# 5. 启动服务
python main.py
```

服务启动后，访问 `http://localhost:8000/docs` 即可查看交互式 API 文档。

---

## 📖 文档导航

为了帮助您更好地使用和开发本项目，我们提供了详细的分类文档：

- 📖 **[DEPLOYMENT.md](DEPLOYMENT.md)**: **部署与使用指南**。包含详细的 API 接口说明、配置项解释以及常见故障排查。
- 🛠️ **[BUILD.md](BUILD.md)**: **构建指南**。详细说明如何从源码构建项目，以及如何使用 PyInstaller 将项目打包为独立的 `.exe` 文件。
- ⚡ **[PACKAGING_QUICKSTART.md](PACKAGING_QUICKSTART.md)**: **打包速查表**。如果您需要快速打包发布，请参考此文档。
- 🤖 **[CLAUDE.md](CLAUDE.md)**: **开发备忘录**。面向贡献者和 AI 助手的快速参考，包含项目架构和常用开发命令。

---

## 💻 API 使用示例

### 1. 健康检查

确认服务是否正常运行：

```bash
curl http://localhost:8000/health
```

### 2. 生成图像 (保存到文件)

发送文本提示词，服务器生成图像并返回文件路径：

```bash
curl -X POST "http://localhost:8000/generate/file" \
     -H "Content-Type: application/json" \
     -d "{\"prompt\": \"A cyberpunk city with neon lights\", \"width\": 512, \"height\": 512}"
```

更多高级用法（如 Base64 返回、自定义步数、Guidance Scale 等）请参考 **[DEPLOYMENT.md](DEPLOYMENT.md)**。

---

## 📂 项目结构

```text
zImage/
├── main.py              # 程序入口，启动 API 服务
├── api.py               # FastAPI 应用定义与路由逻辑
├── config.py            # 配置管理 (加载 .env)
├── model_manager.py     # OpenVINO 模型加载与管理
├── generator.py         # 图像生成核心逻辑
├── build_exe.py         # PyInstaller 打包脚本
├── start.bat            # Windows 一键启动脚本
├── models/              # 模型存放目录
└── requirements.txt     # 项目依赖列表
```

---

## 📄 许可证

本项目采用 MIT 许可证。
