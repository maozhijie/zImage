# 快速开始 - EXE打包指南

## 对于开发者 (构建exe)

### 1. 准备环境
```bash
# 创建虚拟环境
uv venv --python=3.12
.venv\Scripts\activate

# 安装依赖
uv pip install -r requirements.txt
```

### 2. 构建exe
```bash
python build_exe.py --clean
```

构建完成后，分发包位于: `release/zimage-turbo-api/`

**详细说明**: 参见 `BUILD.md`

---

## 对于最终用户 (使用exe)

### 1. 配置
```bash
# 复制配置文件
copy .env.example .env

# 编辑配置 (设置模型路径等)
notepad .env
```

### 2. 放置模型
将OpenVINO模型放到 `models` 目录:
```
models/
└── Z-Image-Turbo/
    └── INT4/
        ├── model.xml
        └── model.bin
```

### 3. 启动服务器
```bash
start_server.bat
```

### 4. 测试API
```bash
test_api.bat
```

或访问: http://localhost:8000

**详细说明**: 参见 `DEPLOYMENT.md`

---

## 文件说明

| 文件 | 用途 | 使用者 |
|------|------|--------|
| `build_exe.py` | 构建可执行文件 | 开发者 |
| `BUILD.md` | 构建详细说明 | 开发者 |
| `DEPLOYMENT.md` | 部署使用说明 | 最终用户 |
| `client_test.py` | Python测试客户端 | 开发者/用户 |
| `start_server.bat` | 启动服务器 | 最终用户 |
| `stop_server.bat` | 停止服务器 | 最终用户 |
| `test_api.bat` | 测试API | 最终用户 |

---

## 快速命令参考

### 构建
```bash
# 基本构建
python build_exe.py

# 清理构建
python build_exe.py --clean

# 自定义输出目录
python build_exe.py --output-dir D:\MyRelease
```

### 测试
```bash
# Python客户端
python client_test.py --check
python client_test.py --prompt "A beautiful sunset" --output test.png
python client_test.py --interactive

# 批处理脚本
test_api.bat
check_status.bat
```

### 服务管理
```bash
# 启动
start_server.bat

# 停止
stop_server.bat

# 检查状态
check_status.bat
```

---

## 常见问题

**Q: 构建需要多长时间?**
A: 10-20分钟，取决于机器性能。

**Q: exe文件多大?**
A: 主程序约50MB，包含依赖后总计约500MB-1GB (不含模型)。

**Q: 需要安装Python吗?**
A: 最终用户不需要，所有依赖已打包。开发者构建时需要。

**Q: 支持Linux/Mac吗?**
A: 当前仅支持Windows。Linux/Mac用户请使用源代码版本。

---

## 获取帮助

- 构建问题: 查看 `BUILD.md`
- 部署问题: 查看 `DEPLOYMENT.md`
- API使用: 查看 `DEPLOYMENT.md` 的API使用章节
