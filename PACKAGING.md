# 打包部署指南

## 打包流程说明

### 准备阶段

1. **安装 UV 包管理器**
   ```bash
   pip install uv
   ```

2. **安装项目依赖**
   ```bash
   uv pip install -e .
   uv pip install git+https://github.com/huggingface/diffusers
   uv pip install git+https://github.com/openvino-dev-samples/optimum-intel.git@zimage
   ```

### 打包选项

#### 选项 1: 完整打包（推荐）

包含已转换的模型，解压即用，无需联网。

```bash
python package.py
```

**优点：**
- ✅ 解压后立即可用
- ✅ 无需联网
- ✅ 无需等待模型转换
- ✅ 适合生产部署

**缺点：**
- ❌ 包体积大（3-5GB INT4 / 6-10GB FP16）

**包含内容：**
- 所有源代码
- 转换好的 OpenVINO 模型
- 依赖清单（requirements.txt）
- 跨平台启动脚本

#### 选项 2: 轻量打包

不包含模型，首次运行时自动下载转换。

```bash
python package.py --skip-models
```

**优点：**
- ✅ 包体积小（< 100MB）
- ✅ 下载传输快
- ✅ 适合测试环境

**缺点：**
- ❌ 首次运行需要联网
- ❌ 首次启动慢（10-30分钟）
- ❌ 需要目标机器有足够内存进行转换

### 打包命令参考

```bash
# 创建 ZIP 格式（Windows 友好）
python package.py --format zip

# 创建 tar.gz 格式（Linux 友好）
python package.py --format tar.gz

# 同时创建两种格式
python package.py --format both

# 自定义输出目录
python package.py --output-dir /path/to/output

# 轻量打包
python package.py --skip-models

# 组合使用
python package.py --format both --skip-models
```

## 部署流程

### 目标机器要求

- **Python**: 3.8 或更高版本
- **内存**:
  - 完整包：8GB+（运行）
  - 轻量包：32GB+（首次转换） → 8GB+（运行）
- **磁盘空间**:
  - 完整包：5-10GB
  - 轻量包：1GB → 5-10GB（转换后）
- **网络**:
  - 完整包：仅需安装 uv
  - 轻量包：首次运行需要下载模型

### 部署步骤

#### 1. 传输包文件

```bash
# 使用 scp (Linux)
scp zimage-api-package.zip user@server:/path/to/destination/

# 或使用其他传输方式（FTP, SFTP, USB 等）
```

#### 2. 解压

```bash
# ZIP 格式
unzip zimage-api-package.zip

# tar.gz 格式
tar -xzf zimage-api-package.tar.gz

# 进入目录
cd zimage-package
```

#### 3. 安装 UV（如果未安装）

```bash
pip install uv
```

#### 4. 启动服务

```bash
# Linux/Mac
chmod +x start.sh
./start.sh

# Windows
start.bat
```

**首次启动时：**
- 自动创建虚拟环境
- 安装所有依赖
- 如果是轻量包，会自动下载并转换模型
- 启动 API 服务器

**后续启动：**
- 直接使用已有环境
- 快速启动（10-30秒）

## 打包内容清单

### 完整包目录结构

```
zimage-package/
├── main.py                  # 主程序入口
├── api.py                   # API 路由
├── generator.py             # 图片生成
├── model_manager.py         # 模型管理
├── config.py               # 配置文件
├── pyproject.toml          # 项目元数据
├── requirements.txt        # Python 依赖（锁定版本）
├── README.md               # 使用文档
├── .env.example           # 配置模板
├── start.sh               # Linux/Mac 启动脚本
├── start.bat              # Windows 启动脚本
├── generated_images/      # 输出目录（空）
└── models/                # 模型目录
    └── Z-Image-Turbo/
        └── INT4/          # 或 FP16
            ├── *.xml      # OpenVINO 模型定义
            └── *.bin      # 模型权重
```

### 轻量包目录结构

```
zimage-package/
├── main.py
├── api.py
├── ... (其他源代码)
├── requirements.txt
├── start.sh
├── start.bat
└── generated_images/
    # models/ 目录不存在，首次运行时创建
```

## 配置说明

解压后可以创建 `.env` 文件自定义配置：

```bash
cp .env.example .env
nano .env  # 或使用其他编辑器
```

### 关键配置项

```env
# 模型配置
MODEL_PATH=models/Z-Image-Turbo/INT4  # OpenVINO 模型路径（INT4 或 FP16）
DEVICE=CPU                             # 运行设备：CPU / GPU / AUTO

# 服务配置
API_HOST=0.0.0.0                  # 监听地址（0.0.0.0 = 所有网卡）
API_PORT=8000                      # 端口号

# 存储配置
OUTPUT_DIR=generated_images        # 图片输出目录
MAX_STORED_IMAGES=1000            # 最大保存图片数

# 生成默认值
DEFAULT_HEIGHT=512                 # 默认图片高度
DEFAULT_WIDTH=512                  # 默认图片宽度
DEFAULT_STEPS=9                    # 推理步数（越大越慢但质量更好）
DEFAULT_GUIDANCE_SCALE=0.0        # Turbo 模型建议 0.0
```

## 验证部署

### 1. 检查服务状态

```bash
curl http://localhost:8000/health
```

应该返回：
```json
{"status": "healthy"}
```

### 2. 生成测试图片

```bash
curl -X POST http://localhost:8000/generate/file \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A beautiful sunset"}' \
  -o test.png
```

### 3. 查看 API 文档

浏览器访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 故障排除

### UV 未安装

**错误：** `command not found: uv`

**解决：**
```bash
pip install uv
# 或
pip3 install uv
```

### 端口被占用

**错误：** `Address already in use`

**解决：** 修改 `.env` 文件中的 `API_PORT`
```env
API_PORT=8080
```

### 内存不足

**错误：** `Out of memory`

**解决：**
1. 使用 INT4 模型：
   ```env
   MODEL_PATH=models/Z-Image-Turbo/INT4
   ```
2. 关闭其他程序释放内存
3. 减小生成图片尺寸

### 模型加载失败

**错误：** `Failed to load model`

**解决：**
1. 确认模型文件存在于配置的路径
2. 检查模型目录包含必要文件（openvino_model.xml 等）
3. 验证有足够内存加载模型

## 更新部署

### 更新代码

```bash
# 备份配置
cp .env .env.backup

# 解压新版本（覆盖）
unzip -o zimage-api-package-new.zip

# 恢复配置
cp .env.backup .env

# 重启服务
./start.sh  # 或 start.bat
```

### 更新模型

### 切换模型

如果要在 INT4 和 FP16 之间切换：

```bash
# 修改配置
nano .env  # 修改 MODEL_PATH

# 例如切换到 FP16：
# MODEL_PATH=models/Z-Image-Turbo/FP16

# 重启服务
./start.sh
```

## 生产环境建议

### 1. 使用进程管理器

**Systemd (Linux):**

创建 `/etc/systemd/system/zimage-api.service`:

```ini
[Unit]
Description=Z-Image-Turbo API
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/zimage-package
ExecStart=/path/to/zimage-package/.venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动：
```bash
sudo systemctl enable zimage-api
sudo systemctl start zimage-api
sudo systemctl status zimage-api
```

**PM2 (跨平台):**

```bash
npm install -g pm2
pm2 start main.py --name zimage-api --interpreter .venv/bin/python
pm2 save
pm2 startup
```

### 2. 反向代理

使用 Nginx 做反向代理：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
    }
}
```

### 3. 安全建议

- 修改默认端口
- 使用 HTTPS
- 添加认证中间件
- 限制访问 IP
- 设置请求速率限制

## 性能优化

### CPU 优化

```env
DEVICE=CPU
# 使用 INT4 模型
MODEL_PATH=models/Z-Image-Turbo/INT4
```

### GPU 优化

```env
DEVICE=GPU
# 可以使用 FP16 获得更好质量
MODEL_PATH=models/Z-Image-Turbo/FP16
```

### 并发处理

API 本身不支持并发生成，建议：
- 使用负载均衡部署多个实例
- 或实现请求队列系统

## 监控建议

- 监控 API 响应时间
- 监控内存使用
- 监控磁盘空间（生成图片累积）
- 设置日志轮转

## 备份建议

需要备份的内容：
- `.env` 配置文件
- `models/` 目录（可选，可重新转换）
- `generated_images/` 目录（根据需求）

不需要备份：
- `.venv/` 虚拟环境（可重新创建）
- `__pycache__/` Python 缓存

---

**有问题？** 查看 README.md 或提交 Issue。
