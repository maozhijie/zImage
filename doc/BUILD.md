# Z-Image-Turbo API 构建说明

本文档说明如何从源代码构建可执行文件 (exe) 版本的Z-Image-Turbo API。

## 前提条件

### 系统要求
- **操作系统**: Windows 10/11 (64位)
- **Python**: 3.12 或更高版本
- **内存**: 16GB+ RAM (构建过程需要较多内存)
- **存储**: 20GB+ 可用空间

### 必需软件
- Python 3.12+
- pip
- git (可选，用于克隆仓库)

## 构建步骤

### 1. 准备环境

#### 1.1 克隆或获取源代码

```bash
# 如果使用git
git clone <repository-url>
cd zImage

# 或直接解压源代码包
```

#### 1.2 创建虚拟环境

推荐使用 `uv` (更快):

```bash
# 安装uv
pip install uv

# 创建虚拟环境
uv venv --python=3.12

# 激活虚拟环境 (Windows)
.venv\Scripts\activate
```

或使用标准venv:

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
.venv\Scripts\activate
```

#### 1.3 安装依赖

```bash
# 使用uv (推荐)
uv pip install -r requirements.txt

# 或使用pip
pip install -r requirements.txt
```

**注意**: 这一步可能需要10-30分钟，因为需要编译某些依赖包。

### 2. 准备模型 (可选)

如果您已经有OpenVINO格式的Z-Image-Turbo模型，将其放置到 `models` 目录:

```
models/
└── Z-Image-Turbo/
    └── INT4/
        ├── model.xml
        ├── model.bin
        └── ...
```

如果没有模型，构建后的exe也可以正常运行，只需在部署时提供模型即可。

### 3. 构建可执行文件

#### 3.1 运行构建脚本

```bash
# 基本构建
python build_exe.py

# 清理构建 (推荐首次构建)
python build_exe.py --clean

# 跳过构建，仅打包 (如果已经构建过)
python build_exe.py --skip-build

# 指定输出目录
python build_exe.py --output-dir D:\MyRelease
```

#### 3.2 构建过程

构建脚本会执行以下步骤:

1. **检查PyInstaller**: 自动安装PyInstaller (如果未安装)
2. **创建spec文件**: 生成 `zimage-api.spec` 配置文件
3. **运行PyInstaller**: 打包所有依赖到exe
4. **创建分发包**: 组织文件到分发目录
5. **创建批处理脚本**: 生成启动/停止/测试脚本

**预计时间**: 10-20分钟 (取决于机器性能)

### 4. 构建输出

构建成功后，会在指定的输出目录 (默认 `release/`) 生成完整的分发包:

```
release/
└── zimage-turbo-api/
    ├── zimage-api.exe          # 主程序
    ├── start_server.bat        # 启动服务器
    ├── stop_server.bat         # 停止服务器
    ├── check_status.bat        # 检查状态
    ├── test_api.bat            # 测试API
    ├── .env.example            # 配置模板
    ├── models/                 # 模型目录
    ├── generated_images/       # 图像输出目录
    └── _internal/              # 依赖库
        ├── *.dll
        ├── *.pyd
        └── ...
```

### 5. 测试构建结果

#### 5.1 本地测试

```bash
# 进入构建目录
cd release\zimage-turbo-api

# 配置环境 (复制.env.example为.env并编辑)
copy .env.example .env
notepad .env

# 如果有模型，确保模型路径正确
# 然后启动服务器
start_server.bat
```

#### 5.2 验证功能

```bash
# 检查状态
check_status.bat

# 运行测试
test_api.bat
```

## 构建选项详解

### PyInstaller 选项

构建脚本创建的 `zimage-api.spec` 文件包含以下关键配置:

```python
# 隐藏导入 (PyInstaller可能遗漏的模块)
hiddenimports = [
    'uvicorn.logging',
    'uvicorn.loops.auto',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan.on',
    'openvino',
    'openvino.runtime',
    'optimum.intel',
    'PIL',
]

# UPX压缩 (减小文件大小)
upx=True

# 控制台模式 (显示日志输出)
console=True
```

### 自定义构建

如需自定义构建，可以编辑 `zimage-api.spec` 文件:

#### 添加图标

```python
exe = EXE(
    ...
    icon='path/to/icon.ico',  # 添加图标
)
```

#### 单文件模式

将所有内容打包成单个exe (启动较慢，但分发方便):

```python
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,      # 移到这里
    a.zipfiles,      # 移到这里
    a.datas,         # 移到这里
    [],
    name='zimage-api',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)

# 删除 COLLECT 部分
```

#### 禁用UPX

如果遇到UPX相关问题:

```python
exe = EXE(
    ...
    upx=False,  # 禁用UPX压缩
)
```

## 常见构建问题

### 问题1: PyInstaller导入错误

```
ImportError: No module named 'xxx'
```

**解决方法**:
1. 在 `zimage-api.spec` 的 `hiddenimports` 列表中添加缺失的模块
2. 重新构建: `python build_exe.py --clean`

### 问题2: 构建失败 - 内存不足

```
MemoryError
```

**解决方法**:
- 关闭其他程序释放内存
- 增加虚拟内存
- 使用64位Python

### 问题3: DLL加载失败

```
Error loading Python DLL
```

**解决方法**:
- 确保使用64位Python
- 检查Windows C++ Redistributable是否安装
- 尝试禁用杀毒软件后重新构建

### 问题4: OpenVINO运行时错误

**构建成功但运行时报错**:

```
ModuleNotFoundError: No module named 'openvino'
```

**解决方法**:
在 `zimage-api.spec` 中添加:

```python
hiddenimports = [
    ...
    'openvino',
    'openvino.runtime',
    'openvino.frontend',
    'openvino.runtime.opset13',
]
```

### 问题5: exe体积过大

**解决方法**:
1. 启用UPX压缩 (`upx=True`)
2. 排除不需要的库
3. 使用虚拟环境，只安装必需依赖

```python
# 在spec文件中排除不需要的库
excludes = [
    'matplotlib',
    'scipy',
    'pandas',
    # 其他不需要的库
]
```

## 优化构建

### 减小文件大小

1. **使用UPX压缩**:
   ```bash
   # 下载UPX
   # https://github.com/upx/upx/releases
   # 将upx.exe放到PATH中
   ```

2. **清理依赖**:
   ```bash
   # 创建干净的虚拟环境
   uv venv --python=3.12 .venv-build
   .venv-build\Scripts\activate

   # 只安装必需依赖
   uv pip install openvino optimum-intel fastapi uvicorn
   ```

3. **使用轻量级Python**:
   - 使用Python embed版本
   - 移除不需要的标准库

### 加快启动速度

1. **使用目录模式** (而非单文件):
   - 已在默认spec中配置

2. **预编译.pyc文件**:
   ```bash
   python -m compileall .
   ```

### 提高稳定性

1. **冻结依赖版本**:
   ```bash
   pip freeze > requirements-lock.txt
   ```

2. **测试多个环境**:
   - 在干净的Windows安装上测试
   - 测试不同的Windows版本

## 分发准备

### 1. 创建安装包 (可选)

使用Inno Setup或NSIS创建安装程序:

**Inno Setup示例** (`setup.iss`):

```iss
[Setup]
AppName=Z-Image-Turbo API
AppVersion=1.0.0
DefaultDirName={autopf}\ZImageTurbo
DefaultGroupName=Z-Image-Turbo
OutputDir=installer
OutputBaseFilename=zimage-turbo-setup

[Files]
Source: "release\zimage-turbo-api\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\Start Server"; Filename: "{app}\start_server.bat"
Name: "{group}\Stop Server"; Filename: "{app}\stop_server.bat"
Name: "{group}\Check Status"; Filename: "{app}\check_status.bat"
```

### 2. 打包为压缩文件

```bash
# ZIP格式
powershell Compress-Archive -Path release\zimage-turbo-api -DestinationPath zimage-turbo-api-v1.0.zip

# 或使用7-Zip (更小)
7z a -tzip zimage-turbo-api-v1.0.zip release\zimage-turbo-api\*
```

### 3. 准备文档

确保包含:
- ✓ DEPLOYMENT.md (部署说明)
- ✓ .env.example (配置模板)
- ✓ README.txt (快速开始)

### 4. 版本管理

在 `VERSION` 文件中记录版本号:

```
1.0.0
```

在构建脚本中包含版本信息:

```python
from pathlib import Path

version = (Path(__file__).parent / "VERSION").read_text().strip()
print(f"Building version {version}")
```

## 持续集成 (可选)

### GitHub Actions 示例

`.github/workflows/build.yml`:

```yaml
name: Build Executable

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: windows-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pyinstaller

    - name: Build executable
      run: python build_exe.py

    - name: Upload artifact
      uses: actions/upload-artifact@v3
      with:
        name: zimage-turbo-api
        path: release/zimage-turbo-api
```

## 维护和更新

### 更新依赖

```bash
# 激活虚拟环境
.venv\Scripts\activate

# 更新依赖
pip install --upgrade openvino optimum-intel fastapi uvicorn

# 重新冻结
pip freeze > requirements.txt

# 重新构建
python build_exe.py --clean
```

### 版本发布检查清单

- [ ] 更新 VERSION 文件
- [ ] 更新 DEPLOYMENT.md 中的变更说明
- [ ] 测试所有主要功能
- [ ] 在干净系统上测试部署
- [ ] 检查文件大小是否合理
- [ ] 创建发布说明
- [ ] 打标签并推送

## 附录

### 构建脚本参数

```bash
python build_exe.py --help
```

```
usage: build_exe.py [-h] [--clean] [--skip-build] [--output-dir OUTPUT_DIR]

Build Z-Image-Turbo API executable

optional arguments:
  -h, --help            显示帮助信息
  --clean               清理PyInstaller缓存
  --skip-build          跳过构建，仅打包
  --output-dir DIR      指定输出目录 (默认: release/)
```

### 相关文件说明

| 文件 | 用途 |
|------|------|
| `build_exe.py` | 主构建脚本 |
| `zimage-api.spec` | PyInstaller配置 (自动生成) |
| `requirements.txt` | Python依赖列表 |
| `dist/` | PyInstaller输出目录 |
| `build/` | PyInstaller临时文件 |
| `release/` | 最终分发包目录 |

### 文件大小参考

典型构建后的文件大小:

| 组件 | 大小 |
|------|------|
| zimage-api.exe | ~50MB |
| _internal/ (依赖) | ~500MB-1GB |
| 模型 (INT4) | ~2-3GB |
| 总计 | ~3-4GB |

### 性能基准

| 配置 | 启动时间 | 首次推理 | 后续推理 |
|------|----------|----------|----------|
| CPU | ~10s | ~15s | ~5s |
| GPU | ~15s | ~8s | ~2s |

*实际性能取决于硬件配置*

## 获取帮助

构建过程遇到问题:
1. 检查本文档的"常见构建问题"章节
2. 查看构建日志输出
3. 在GitHub Issues中搜索类似问题
4. 提交新的Issue并附上详细日志
