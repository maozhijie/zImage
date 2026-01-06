#!/usr/bin/env python
"""
独立的Z-Image-Turbo API测试客户端
可以独立运行，测试API的各种功能
"""
import argparse
import json
import time
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("错误: 需要安装 requests 库")
    print("请运行: pip install requests")
    exit(1)


class ZImageClient:
    """Z-Image-Turbo API客户端"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')

    def health_check(self) -> bool:
        """检查服务器健康状态"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"健康检查失败: {e}")
            return False

    def get_info(self) -> Optional[dict]:
        """获取API信息"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"获取API信息失败: {e}")
            return None

    def generate_image_file(
        self,
        prompt: str,
        output_path: str = "output.png",
        height: int = 512,
        width: int = 512,
        steps: int = 9,
        guidance_scale: float = 0.0,
        seed: Optional[int] = None
    ) -> bool:
        """生成图像并保存到文件"""
        payload = {
            "prompt": prompt,
            "height": height,
            "width": width,
            "num_inference_steps": steps,
            "guidance_scale": guidance_scale,
        }

        if seed is not None:
            payload["seed"] = seed

        try:
            print(f"生成图像...")
            print(f"  提示词: {prompt}")
            print(f"  尺寸: {width}x{height}")
            print(f"  步数: {steps}")
            if seed is not None:
                print(f"  种子: {seed}")

            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/generate/file",
                json=payload,
                timeout=300  # 5分钟超时
            )
            response.raise_for_status()
            elapsed = time.time() - start_time

            # 保存图像
            output_file = Path(output_path)
            output_file.write_bytes(response.content)

            print(f"\n✓ 图像生成成功!")
            print(f"  耗时: {elapsed:.2f}秒")
            print(f"  文件大小: {len(response.content) / 1024:.2f} KB")
            print(f"  保存路径: {output_file.absolute()}")

            return True

        except requests.exceptions.Timeout:
            print("\n✗ 请求超时，图像生成时间过长")
            return False
        except requests.exceptions.RequestException as e:
            print(f"\n✗ 请求失败: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    print(f"  错误详情: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
                except:
                    print(f"  响应内容: {e.response.text[:200]}")
            return False
        except Exception as e:
            print(f"\n✗ 发生错误: {e}")
            return False

    def generate_image_url(
        self,
        prompt: str,
        height: int = 512,
        width: int = 512,
        steps: int = 9,
        guidance_scale: float = 0.0,
        seed: Optional[int] = None
    ) -> Optional[dict]:
        """生成图像并返回URL"""
        payload = {
            "prompt": prompt,
            "height": height,
            "width": width,
            "num_inference_steps": steps,
            "guidance_scale": guidance_scale,
        }

        if seed is not None:
            payload["seed"] = seed

        try:
            print(f"生成图像...")
            print(f"  提示词: {prompt}")
            print(f"  尺寸: {width}x{height}")
            print(f"  步数: {steps}")
            if seed is not None:
                print(f"  种子: {seed}")

            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/generate/url",
                json=payload,
                timeout=300
            )
            response.raise_for_status()
            elapsed = time.time() - start_time

            result = response.json()

            print(f"\n✓ 请求成功!")
            print(f"  耗时: {elapsed:.2f}秒")
            print(f"  成功: {result.get('success')}")
            print(f"  消息: {result.get('message')}")

            if result.get('success'):
                print(f"  图像URL: {result.get('image_url')}")
                print(f"  预览URL: {result.get('preview_url')}")
                print(f"  文件名: {result.get('filename')}")

            return result

        except Exception as e:
            print(f"\n✗ 发生错误: {e}")
            return None

    def download_image_from_url(self, image_url: str, output_path: str) -> bool:
        """从URL下载图像"""
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            output_file = Path(output_path)
            output_file.write_bytes(response.content)

            print(f"✓ 图像已下载到: {output_file.absolute()}")
            return True

        except Exception as e:
            print(f"✗ 下载失败: {e}")
            return False


def interactive_mode(client: ZImageClient):
    """交互式模式"""
    print("\n" + "=" * 60)
    print("Z-Image-Turbo API 交互式客户端")
    print("=" * 60)
    print("输入 'quit' 或 'exit' 退出")
    print()

    while True:
        try:
            prompt = input("\n请输入提示词: ").strip()

            if prompt.lower() in ['quit', 'exit', 'q']:
                print("再见!")
                break

            if not prompt:
                print("提示词不能为空")
                continue

            # 询问参数
            try:
                width = input("宽度 [512]: ").strip()
                width = int(width) if width else 512

                height = input("高度 [512]: ").strip()
                height = int(height) if height else 512

                steps = input("步数 [9]: ").strip()
                steps = int(steps) if steps else 9

                seed_input = input("种子 (可选): ").strip()
                seed = int(seed_input) if seed_input else None

                output = input("输出文件名 [output.png]: ").strip()
                output = output if output else "output.png"

            except ValueError as e:
                print(f"输入错误: {e}")
                continue

            # 生成图像
            client.generate_image_file(
                prompt=prompt,
                output_path=output,
                width=width,
                height=height,
                steps=steps,
                seed=seed
            )

        except KeyboardInterrupt:
            print("\n\n中断，再见!")
            break
        except Exception as e:
            print(f"错误: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Z-Image-Turbo API 测试客户端",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 健康检查
  python client_test.py --check

  # 生成图像
  python client_test.py --prompt "A beautiful sunset" --output sunset.png

  # 使用自定义参数
  python client_test.py --prompt "A cat" --width 768 --height 768 --steps 12 --seed 42

  # 交互式模式
  python client_test.py --interactive

  # 指定API地址
  python client_test.py --url http://192.168.1.100:8000 --check
        """
    )

    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="API服务器地址 (默认: http://localhost:8000)"
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="检查服务器健康状态"
    )

    parser.add_argument(
        "--info",
        action="store_true",
        help="获取API信息"
    )

    parser.add_argument(
        "--prompt",
        type=str,
        help="图像生成提示词"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="output.png",
        help="输出文件路径 (默认: output.png)"
    )

    parser.add_argument(
        "--width",
        type=int,
        default=512,
        help="图像宽度 (默认: 512)"
    )

    parser.add_argument(
        "--height",
        type=int,
        default=512,
        help="图像高度 (默认: 512)"
    )

    parser.add_argument(
        "--steps",
        type=int,
        default=9,
        help="推理步数 (默认: 9)"
    )

    parser.add_argument(
        "--guidance-scale",
        type=float,
        default=0.0,
        help="引导比例 (默认: 0.0)"
    )

    parser.add_argument(
        "--seed",
        type=int,
        help="随机种子 (可选)"
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        help="交互式模式"
    )

    parser.add_argument(
        "--method",
        choices=["file", "url"],
        default="file",
        help="生成方法: file=直接返回文件, url=返回URL (默认: file)"
    )

    args = parser.parse_args()

    # 创建客户端
    client = ZImageClient(args.url)

    print("=" * 60)
    print("Z-Image-Turbo API 测试客户端")
    print("=" * 60)
    print(f"API地址: {args.url}")
    print()

    # 交互式模式
    if args.interactive:
        interactive_mode(client)
        return 0

    # 健康检查
    if args.check:
        print("执行健康检查...")
        if client.health_check():
            print("✓ 服务器运行正常")
            return 0
        else:
            print("✗ 服务器无响应")
            return 1

    # 获取信息
    if args.info:
        print("获取API信息...")
        info = client.get_info()
        if info:
            print(json.dumps(info, indent=2, ensure_ascii=False))
            return 0
        else:
            return 1

    # 生成图像
    if args.prompt:
        # 先检查服务器是否可用
        if not client.health_check():
            print("✗ 服务器无响应，请先启动服务器")
            return 1

        if args.method == "file":
            success = client.generate_image_file(
                prompt=args.prompt,
                output_path=args.output,
                width=args.width,
                height=args.height,
                steps=args.steps,
                guidance_scale=args.guidance_scale,
                seed=args.seed
            )
            return 0 if success else 1

        elif args.method == "url":
            result = client.generate_image_url(
                prompt=args.prompt,
                width=args.width,
                height=args.height,
                steps=args.steps,
                guidance_scale=args.guidance_scale,
                seed=args.seed
            )

            if result and result.get('success'):
                # 询问是否下载
                try:
                    download = input("\n是否下载图像? [Y/n]: ").strip().lower()
                    if download != 'n':
                        client.download_image_from_url(
                            result['image_url'],
                            args.output
                        )
                except KeyboardInterrupt:
                    print("\n跳过下载")

                return 0
            else:
                return 1

    # 没有指定操作，显示帮助
    parser.print_help()
    return 0


if __name__ == "__main__":
    exit(main())
