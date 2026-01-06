#!/usr/bin/env python
"""
Test script to verify .env configuration is loaded correctly
"""
from config import settings, PROJECT_ROOT

print("=" * 60)
print("Configuration Test")
print("=" * 60)

print(f"\nProject Root: {PROJECT_ROOT}")
print(f"\n.env file location: {PROJECT_ROOT / '.env'}")
print(f".env exists: {(PROJECT_ROOT / '.env').exists()}")

print("\n" + "=" * 60)
print("Model Settings")
print("=" * 60)
print(f"MODEL_ID: {settings.MODEL_ID}")
print(f"MODEL_BASE_DIR: {settings.MODEL_BASE_DIR}")
print(f"Model absolute path: {settings.get_model_base_dir()}")
print(f"USE_INT4_COMPRESSION: {settings.USE_INT4_COMPRESSION}")
print(f"DEVICE: {settings.DEVICE}")

print("\n" + "=" * 60)
print("API Settings")
print("=" * 60)
print(f"API_HOST: {settings.API_HOST}")
print(f"API_PORT: {settings.API_PORT}")

print("\n" + "=" * 60)
print("Storage Settings")
print("=" * 60)
print(f"OUTPUT_DIR: {settings.OUTPUT_DIR}")
print(f"Output absolute path: {settings.get_output_dir()}")
print(f"MAX_STORED_IMAGES: {settings.MAX_STORED_IMAGES}")

print("\n" + "=" * 60)
print("Generation Defaults")
print("=" * 60)
print(f"DEFAULT_HEIGHT: {settings.DEFAULT_HEIGHT}")
print(f"DEFAULT_WIDTH: {settings.DEFAULT_WIDTH}")
print(f"DEFAULT_STEPS: {settings.DEFAULT_STEPS}")
print(f"DEFAULT_GUIDANCE_SCALE: {settings.DEFAULT_GUIDANCE_SCALE}")

print("\n" + "=" * 60)
print("Expected Values from .env")
print("=" * 60)

env_file = PROJECT_ROOT / ".env"
if env_file.exists():
    print("\n.env file contents:")
    print("-" * 60)
    print(env_file.read_text(encoding="utf-8"))
    print("-" * 60)
else:
    print("\n⚠️  WARNING: .env file not found!")
    print("Create .env from .env.example:")
    print(f"  cp {PROJECT_ROOT / '.env.example'} {env_file}")

print("\n" + "=" * 60)
print("Verification")
print("=" * 60)

# Check if settings match expected values
checks = []

if env_file.exists():
    env_content = env_file.read_text()

    if "DEVICE=GPU" in env_content:
        if settings.DEVICE == "GPU":
            checks.append(("✓", "DEVICE is GPU (from .env)"))
        else:
            checks.append(("✗", f"DEVICE is {settings.DEVICE} (expected GPU from .env)"))

    if "USE_INT4_COMPRESSION=true" in env_content:
        if settings.USE_INT4_COMPRESSION:
            checks.append(("✓", "USE_INT4_COMPRESSION is True (from .env)"))
        else:
            checks.append(("✗", "USE_INT4_COMPRESSION is False (expected True from .env)"))

    if "MODEL_BASE_DIR=models" in env_content:
        if settings.MODEL_BASE_DIR == "models":
            checks.append(("✓", "MODEL_BASE_DIR is 'models' (from .env)"))
        else:
            checks.append(("✗", f"MODEL_BASE_DIR is {settings.MODEL_BASE_DIR} (expected 'models' from .env)"))

    for symbol, message in checks:
        print(f"{symbol} {message}")

    if all(check[0] == "✓" for check in checks):
        print("\n✅ All configuration values loaded correctly from .env!")
    else:
        print("\n❌ Some configuration values not loaded correctly!")
        print("\nTroubleshooting:")
        print("1. Make sure .env file is in the project root directory")
        print("2. Check .env file has correct format (KEY=value, no spaces)")
        print("3. Restart the application after modifying .env")
else:
    print("❌ .env file not found. Configuration using default values.")

print("=" * 60)
