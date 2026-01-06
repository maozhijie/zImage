"""
Test script for Z-Image-Turbo API
"""
import argparse
import time
from pathlib import Path

import requests


def test_health(base_url: str):
    """Test health check endpoint"""
    print("\n" + "=" * 60)
    print("Testing Health Check Endpoint")
    print("=" * 60)

    url = f"{base_url}/health"
    print(f"GET {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_generate_file(base_url: str, prompt: str, output_path: str = "test_image.png"):
    """Test generate file endpoint"""
    print("\n" + "=" * 60)
    print("Testing Generate File Endpoint")
    print("=" * 60)

    url = f"{base_url}/generate/file"
    print(f"POST {url}")
    print(f"Prompt: {prompt}")

    payload = {
        "prompt": prompt,
        "height": 512,
        "width": 512,
        "num_inference_steps": 9,
        "seed": 42
    }

    try:
        print("\nGenerating image (this may take a while)...")
        start_time = time.time()

        response = requests.post(url, json=payload)
        response.raise_for_status()

        elapsed_time = time.time() - start_time

        # Save image
        output_file = Path(output_path)
        output_file.write_bytes(response.content)

        print(f"\nStatus: {response.status_code}")
        print(f"Generation time: {elapsed_time:.2f} seconds")
        print(f"Image saved to: {output_file.absolute()}")
        print(f"File size: {len(response.content) / 1024:.2f} KB")

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_generate_url(base_url: str, prompt: str):
    """Test generate URL endpoint"""
    print("\n" + "=" * 60)
    print("Testing Generate URL Endpoint")
    print("=" * 60)

    url = f"{base_url}/generate/url"
    print(f"POST {url}")
    print(f"Prompt: {prompt}")

    payload = {
        "prompt": prompt,
        "height": 512,
        "width": 512,
        "num_inference_steps": 9,
        "seed": 42
    }

    try:
        print("\nGenerating image (this may take a while)...")
        start_time = time.time()

        response = requests.post(url, json=payload)
        response.raise_for_status()

        elapsed_time = time.time() - start_time
        result = response.json()

        print(f"\nStatus: {response.status_code}")
        print(f"Generation time: {elapsed_time:.2f} seconds")
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        print(f"Image URL: {result.get('image_url')}")
        print(f"Preview URL: {result.get('preview_url')}")
        print(f"Filename: {result.get('filename')}")

        # Test preview endpoint
        if result.get('success') and result.get('image_url'):
            print("\nTesting preview endpoint...")
            preview_response = requests.get(result['image_url'])
            preview_response.raise_for_status()
            print(f"Preview endpoint status: {preview_response.status_code}")
            print(f"Image size: {len(preview_response.content) / 1024:.2f} KB")

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test Z-Image-Turbo API")
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="A beautiful sunset over mountains, photorealistic",
        help="Text prompt for image generation"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="test_image.png",
        help="Output path for test image (default: test_image.png)"
    )
    parser.add_argument(
        "--test",
        type=str,
        choices=["health", "file", "url", "all"],
        default="all",
        help="Which test to run (default: all)"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Z-Image-Turbo API Test")
    print("=" * 60)
    print(f"API URL: {args.url}")
    print(f"Test: {args.test}")

    results = {}

    if args.test in ["health", "all"]:
        results["health"] = test_health(args.url)

    if args.test in ["file", "all"]:
        results["file"] = test_generate_file(args.url, args.prompt, args.output)

    if args.test in ["url", "all"]:
        results["url"] = test_generate_url(args.url, args.prompt)

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, success in results.items():
        status = "PASSED" if success else "FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())
    print("\n" + ("All tests passed!" if all_passed else "Some tests failed!"))
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
