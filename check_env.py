#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple .env file checker (no dependencies required)
"""
import os
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def parse_env_file(filepath):
    """Parse .env file manually"""
    env_vars = {}
    if not filepath.exists():
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                env_vars[key] = value
            else:
                print(f"⚠️  Line {line_num}: Invalid format: {line}")

    return env_vars

def main():
    project_root = Path(__file__).parent
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"

    print("=" * 70)
    print("Z-Image-Turbo .env Configuration Checker")
    print("=" * 70)

    print(f"\nProject Root: {project_root}")
    print(f".env file path: {env_file}")
    print(f".env exists: {env_file.exists()}")

    if not env_file.exists():
        print("\n" + "=" * 70)
        print("❌ ERROR: .env file not found!")
        print("=" * 70)
        print("\nThe .env file must be in the project root directory.")

        if env_example.exists():
            print(f"\n✓ Found .env.example at: {env_example}")
            print("\nTo fix this, run:")
            print(f"  cp .env.example .env")
            print("  # or on Windows:")
            print(f"  copy .env.example .env")
            print("\nThen edit .env with your settings.")
        else:
            print("\n⚠️  .env.example also not found!")
            print("\nCreate .env manually with the following content:")
            print("-" * 70)
            print("""# Model settings
# 直接指定 OpenVINO 模型的路径（例如: models/Z-Image-Turbo/INT4）
MODEL_PATH=models/Z-Image-Turbo/INT4
DEVICE=GPU

# API settings
API_HOST=0.0.0.0
API_PORT=8000

# Image storage
OUTPUT_DIR=generated_images
MAX_STORED_IMAGES=1000

# Generation defaults
DEFAULT_HEIGHT=512
DEFAULT_WIDTH=512
DEFAULT_STEPS=9
DEFAULT_GUIDANCE_SCALE=0.0""")
            print("-" * 70)

        return 1

    # Parse .env file
    print("\n" + "=" * 70)
    print(".env File Content")
    print("=" * 70)

    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
        print(content)

    # Parse environment variables
    env_vars = parse_env_file(env_file)

    print("\n" + "=" * 70)
    print("Parsed Configuration Values")
    print("=" * 70)

    if env_vars:
        for key, value in env_vars.items():
            print(f"  {key} = {value}")
    else:
        print("  (No valid configuration found)")

    # Validation
    print("\n" + "=" * 70)
    print("Configuration Validation")
    print("=" * 70)

    checks = []

    # Check required fields
    required_fields = [
        'MODEL_PATH',
        'DEVICE',
        'API_HOST',
        'API_PORT'
    ]

    for field in required_fields:
        if field in env_vars:
            checks.append((True, f"✓ {field} is set: {env_vars[field]}", field, env_vars[field]))
        else:
            checks.append((False, f"✗ {field} is MISSING", field, None))

    # Print all checks
    for success, message, field, value in checks:
        print(f"  {message}")

    # Specific validations
    print("\n" + "=" * 70)
    print("Value Validations")
    print("=" * 70)

    warnings = []

    # Check DEVICE
    if 'DEVICE' in env_vars:
        device = env_vars['DEVICE']
        valid_devices = ['CPU', 'GPU', 'AUTO']
        if device in valid_devices:
            print(f"  ✓ DEVICE={device} (valid)")
        else:
            warnings.append(f"  ⚠️  DEVICE={device} (should be one of: {', '.join(valid_devices)})")

    # Check API_PORT
    if 'API_PORT' in env_vars:
        try:
            port = int(env_vars['API_PORT'])
            if 1 <= port <= 65535:
                print(f"  ✓ API_PORT={port} (valid)")
            else:
                warnings.append(f"  ⚠️  API_PORT={port} (should be 1-65535)")
        except ValueError:
            warnings.append(f"  ⚠️  API_PORT={env_vars['API_PORT']} (should be a number)")

    # Check MODEL_PATH
    if 'MODEL_PATH' in env_vars:
        model_path_value = env_vars['MODEL_PATH']
        # Support both absolute and relative paths
        if Path(model_path_value).is_absolute():
            model_path = Path(model_path_value)
        else:
            model_path = project_root / model_path_value

        if model_path.exists():
            print(f"  ✓ MODEL_PATH exists: {model_path}")
        else:
            warnings.append(f"  ⚠️  MODEL_PATH does not exist: {model_path}")
            print(f"  ℹ️  Please ensure your OpenVINO model is placed at: {model_path}")

    # Print warnings
    if warnings:
        print("\n" + "=" * 70)
        print("Warnings")
        print("=" * 70)
        for warning in warnings:
            print(warning)

    # Final summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    all_required_present = all(check[0] for check in checks)

    if all_required_present and not warnings:
        print("✅ Configuration looks good!")
        print("\nNext steps:")
        print("  1. Install dependencies: ./start.sh (or start.bat)")
        print("  2. Or run: python main.py")
        return 0
    elif all_required_present:
        print("⚠️  Configuration is present but has warnings.")
        print("Please review the warnings above.")
        return 0
    else:
        print("❌ Configuration has errors.")
        print("Please fix the issues above.")
        return 1

if __name__ == "__main__":
    exit(main())
