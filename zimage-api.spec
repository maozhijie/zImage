# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_all

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

# Collect all OpenVINO components
tmp_ret = collect_all('openvino')
datas += tmp_ret[0]
binaries = tmp_ret[1]
hiddenimports += tmp_ret[2]

a = Analysis(
    ['main.py'],
        pathex=[],
        binaries=binaries,
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
