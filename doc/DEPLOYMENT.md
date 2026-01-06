# Z-Image-Turbo API 部署文档

本文档说明如何部署和使用Z-Image-Turbo API的可执行文件版本。

## 系统要求

### 最低要求
- **操作系统**: Windows 10/11 (64位)
- **内存**: 8GB RAM (推荐16GB以上)
- **存储**: 10GB可用空间 (模型文件较大)
- **GPU** (可选但推荐):
  - Intel集成显卡 (支持OpenVINO)
  - Intel独立显卡 (Arc系列)
  - 或使用CPU运行

### 软件依赖
- 无需安装Python
- 无需安装其他依赖
- 所有依赖已打包在exe中

## 快速开始

### 1. 获取分发包

分发包目录结构:
```
zimage-turbo-api/
├── zimage-api.exe          # 主程序
├── start_server.bat        # 启动服务器脚本
├── stop_server.bat         # 停止服务器脚本
├── check_status.bat        # 检查服务器状态
├── test_api.bat            # 测试API脚本
├── .env.example            # 配置文件模板
├── models/                 # 模型目录
│   └── README.txt          # 模型说明
├── generated_images/       # 生成图像存放目录
└── _internal/              # 运行时依赖 (不要修改)
```

### 2. 配置模型

#### 2.1 准备OpenVINO模型

将OpenVINO格式的Z-Image-Turbo模型放置到 `models` 目录:

```
models/
└── Z-Image-Turbo/
    └── INT4/               # 或 FP16, INT8 等
        ├── model.xml
        ├── model.bin
        └── ... (其他模型文件)
```

#### 2.2 配置环境变量

首次运行时，`start_server.bat` 会自动从 `.env.example` 创建 `.env` 文件。

编辑 `.env` 文件配置:

```bash
# 模型路径 (相对于exe所在目录)
MODEL_PATH=models/Z-Image-Turbo/INT4

# 设备选择: CPU, GPU, AUTO
DEVICE=GPU

# API服务器配置
API_HOST=0.0.0.0
API_PORT=8000

# 图像存储
OUTPUT_DIR=generated_images
MAX_STORED_IMAGES=1000

# 生成默认参数
DEFAULT_HEIGHT=512
DEFAULT_WIDTH=512
DEFAULT_STEPS=9
DEFAULT_GUIDANCE_SCALE=0.0
```

**重要配置说明:**

- `MODEL_PATH`: 模型目录路径，可以是相对路径或绝对路径
- `DEVICE`:
  - `CPU` - 使用CPU运行 (兼容性最好，速度较慢)
  - `GPU` - 使用GPU加速 (需要Intel GPU，速度快)
  - `AUTO` - 自动选择最佳设备

### 3. 启动服务器

双击运行 `start_server.bat` 或在命令行中执行:

```bash
start_server.bat
```

**首次运行流程:**
1. 脚本会检查 `.env` 文件，如不存在则自动创建
2. 提示编辑配置文件（如果需要）
3. 检查模型目录是否存在
4. 启动服务器进程

**成功启动后:**
- 服务器在后台运行
- 日志输出到 `server.log` 文件
- 可以访问 `http://localhost:8000`

### 4. 验证服务器状态

#### 方法1: 使用状态检查脚本

```bash
check_status.bat
```

#### 方法2: 浏览器访问

打开浏览器访问: `http://localhost:8000`

或访问健康检查端点: `http://localhost:8000/health`

#### 方法3: 使用curl命令

```bash
curl http://localhost:8000/health
```

### 5. 测试API

#### 使用测试脚本

```bash
test_api.bat
```

该脚本会:
1. 检查健康状态
2. 生成测试图像
3. 测试URL生成端点

#### 使用Python测试客户端

如果您的系统安装了Python和requests库:

```bash
# 基本测试
python client_test.py --check

# 生成图像
python client_test.py --prompt "A beautiful sunset over mountains" --output test.png

# 交互式模式
python client_test.py --interactive

# 自定义参数
python client_test.py --prompt "A cat" --width 768 --height 768 --steps 12 --seed 42
```

### 6. 停止服务器

双击运行 `stop_server.bat` 或在命令行中执行:

```bash
stop_server.bat
```

## API使用说明

### API端点

服务器默认运行在 `http://localhost:8000`

#### 1. 健康检查
```
GET /health
```

返回示例:
```json
{
  "status": "healthy"
}
```

#### 2. API信息
```
GET /
```

返回API版本和可用端点信息。

#### 3. 生成图像 (文件方式)
```
POST /generate/file
Content-Type: application/json

{
  "prompt": "A beautiful sunset over mountains",
  "height": 512,
  "width": 512,
  "num_inference_steps": 9,
  "guidance_scale": 0.0,
  "seed": 42
}
```

直接返回图像文件 (PNG格式)。

#### 4. 生成图像 (URL方式)
```
POST /generate/url
Content-Type: application/json

{
  "prompt": "A beautiful sunset over mountains",
  "height": 512,
  "width": 512,
  "num_inference_steps": 9,
  "guidance_scale": 0.0,
  "seed": 42
}
```

返回示例:
```json
{
  "success": true,
  "message": "Image generated successfully",
  "image_url": "http://localhost:8000/images/image_20260106_123456_abcd1234.png",
  "preview_url": "http://localhost:8000/images/image_20260106_123456_abcd1234.png",
  "filename": "image_20260106_123456_abcd1234.png"
}
```

#### 5. 预览图像
```
GET /images/{filename}
```

返回指定的生成图像文件。

### 参数说明

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| prompt | string | ✓ | - | 图像描述文本 |
| height | integer | ✗ | 512 | 图像高度 (256-1024) |
| width | integer | ✗ | 512 | 图像宽度 (256-1024) |
| num_inference_steps | integer | ✗ | 9 | 推理步数 (1-50) |
| guidance_scale | float | ✗ | 0.0 | 引导比例 (0.0-10.0) |
| seed | integer | ✗ | null | 随机种子 (用于复现) |

**注意**: Z-Image-Turbo是Turbo模型，推荐使用 `guidance_scale=0.0` 以获得最佳性能。

## 使用示例

### cURL 示例

```bash
# 健康检查
curl http://localhost:8000/health

# 生成图像并保存
curl -X POST "http://localhost:8000/generate/file" \
     -H "Content-Type: application/json" \
     -d "{\"prompt\":\"A beautiful sunset\",\"seed\":42}" \
     -o output.png

# 获取图像URL
curl -X POST "http://localhost:8000/generate/url" \
     -H "Content-Type: application/json" \
     -d "{\"prompt\":\"A cat\",\"width\":768,\"height\":768}"
```

### Python 示例

```python
import requests

# API基础URL
BASE_URL = "http://localhost:8000"

# 生成图像
response = requests.post(
    f"{BASE_URL}/generate/file",
    json={
        "prompt": "A beautiful sunset over mountains",
        "height": 512,
        "width": 512,
        "num_inference_steps": 9,
        "seed": 42
    }
)

# 保存图像
if response.status_code == 200:
    with open("output.png", "wb") as f:
        f.write(response.content)
    print("图像已保存")
```

### JavaScript 示例

```javascript
// 生成图像
async function generateImage(prompt) {
  const response = await fetch('http://localhost:8000/generate/url', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt: prompt,
      height: 512,
      width: 512,
      num_inference_steps: 9,
      seed: 42
    })
  });

  const result = await response.json();
  console.log('Image URL:', result.image_url);
  return result;
}

// 使用
generateImage('A beautiful sunset over mountains');
```

## 故障排查

### 服务器无法启动

**问题1: 端口被占用**
```
错误: Address already in use
```

解决方法:
- 修改 `.env` 文件中的 `API_PORT` 为其他端口 (如 8001)
- 或停止占用8000端口的其他程序

**问题2: 模型路径错误**
```
错误: Model not found
```

解决方法:
- 检查 `.env` 中的 `MODEL_PATH` 是否正确
- 确认模型文件确实存在于指定路径
- 运行 `python check_env.py` (如果有Python环境)

**问题3: GPU不可用**
```
错误: GPU device not found
```

解决方法:
- 将 `.env` 中的 `DEVICE` 改为 `CPU` 或 `AUTO`
- 确保Intel GPU驱动已正确安装

### 图像生成失败

**问题: 内存不足**
```
错误: Out of memory
```

解决方法:
- 减小图像尺寸 (如从1024降到512)
- 关闭其他占用内存的程序
- 使用CPU而不是GPU (修改DEVICE配置)

**问题: 生成速度慢**

优化方法:
- 使用GPU设备 (`DEVICE=GPU`)
- 使用INT4量化模型 (最快)
- 减少推理步数 (steps=4-9)

### 查看日志

服务器运行日志保存在 `server.log` 文件中:

```bash
# Windows
type server.log

# 或用记事本打开
notepad server.log
```

## 性能优化

### 设备选择

| 设备 | 速度 | 兼容性 | 推荐场景 |
|------|------|--------|----------|
| CPU | 慢 | 最佳 | 开发、测试、无GPU环境 |
| GPU | 快 | 需要Intel GPU | 生产环境、高并发 |
| AUTO | 自动 | 好 | 不确定硬件配置时 |

### 模型量化

| 量化方式 | 模型大小 | 速度 | 质量 |
|----------|----------|------|------|
| FP16 | 最大 | 慢 | 最佳 |
| INT8 | 中等 | 中等 | 好 |
| INT4 | 最小 | 最快 | 良好 |

推荐使用 INT4 以获得最佳性能/质量平衡。

### 批处理

API不直接支持批处理，但可以通过并发请求提高吞吐量:

```python
import concurrent.futures
import requests

def generate_image(prompt):
    response = requests.post(
        "http://localhost:8000/generate/file",
        json={"prompt": prompt}
    )
    return response.content

# 并发生成多张图像
prompts = ["sunset", "cat", "mountain", "ocean"]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(generate_image, prompts))
```

## 网络访问配置

### 局域网访问

默认配置 `API_HOST=0.0.0.0` 已允许局域网访问。

客户端访问地址: `http://<服务器IP>:8000`

例如: `http://192.168.1.100:8000`

### 防火墙配置

如果无法从其他机器访问，需要配置Windows防火墙:

1. 打开 "Windows Defender 防火墙"
2. 点击 "高级设置"
3. 选择 "入站规则" → "新建规则"
4. 选择 "端口" → TCP → 特定端口 → 输入 8000
5. 允许连接 → 完成

### 安全建议

⚠️ **生产环境安全提示:**

- 不要将服务暴露到公网，除非有适当的安全措施
- 考虑使用反向代理 (如Nginx) 添加认证
- 限制 `API_HOST` 为特定IP (如 `127.0.0.1` 仅本地访问)
- 定期清理生成的图像以节省空间

## 更新和维护

### 更新模型

1. 停止服务器 (`stop_server.bat`)
2. 替换 `models` 目录下的模型文件
3. 更新 `.env` 中的 `MODEL_PATH`
4. 重启服务器 (`start_server.bat`)

### 清理生成的图像

手动删除 `generated_images` 目录下的文件，或配置 `MAX_STORED_IMAGES` 限制自动清理。

### 备份配置

重要文件:
- `.env` - 配置文件
- `models/` - 模型文件 (较大，可选)

## 技术支持

遇到问题时:

1. 查看 `server.log` 日志文件
2. 运行 `check_status.bat` 检查状态
3. 确认模型文件和配置正确
4. 查看本文档的故障排查章节

## 附录

### 系统要求详细说明

**CPU要求:**
- x64架构处理器
- 推荐: Intel Core i5或更高
- 最低: 4核心

**内存要求:**
- 推荐: 16GB或更多
- 最低: 8GB
- 注意: 模型加载会占用3-6GB内存

**存储要求:**
- 程序: 约500MB-2GB
- 模型: 2-8GB (取决于量化方式)
- 生成图像: 建议预留5-10GB

**GPU要求 (可选):**
- Intel集成显卡: HD Graphics 600系列或更新
- Intel独立显卡: Arc A系列
- 驱动: 最新Intel Graphics驱动

### 命令行参数

`zimage-api.exe` 本身不接受命令行参数，所有配置通过 `.env` 文件。

如需自定义启动方式，可以修改 `.env` 后直接运行:
```bash
zimage-api.exe
```

### 环境变量优先级

配置加载顺序 (从高到低):
1. 系统环境变量
2. `.env` 文件
3. 代码中的默认值

建议统一使用 `.env` 文件管理配置。
