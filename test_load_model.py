import logging
import torch
from pathlib import Path
from optimum.intel import OVZImagePipeline

# 配置简单的日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def test_pipeline_loading():
   
    model_dir = Path("C:\\Users\\flowy\\Desktop\\zImage\\zImage\\model") 
    device = "GPU"  

    logger.info(f"Loading OpenVINO model from {model_dir}")
    logger.info(f"Using device: {device}")

    try:
        pipeline = OVZImagePipeline.from_pretrained(
            str(model_dir),
            device=device
        )
        
        if pipeline:
            logger.info("Model loaded successfully")
            print("\n测试通过！pipeline 对象已创建。")

            # 开始生成图片
            logger.info("开始生成图片...")
            prompt = "Young Chinese woman in red Hanfu, intricate embroidery. Impeccable makeup, red floral forehead pattern. Elaborate high bun, golden phoenix headdress, red flowers, beads. Holds round folding fan with lady, trees, bird. Neon lightning-bolt lamp (⚡️), bright yellow glow, above extended left palm. Soft-lit outdoor night background, silhouetted tiered pagoda (西安大雁塔), blurred colorful distant lights."
            
            image = pipeline( 
                prompt=prompt, 
                height=512, 
                width=512, 
                num_inference_steps=9,   # This actually results in 8 DiT forwards 
                guidance_scale=0.0,   # Guidance should be 0 for the Turbo models 
                generator=torch.Generator("GPU").manual_seed(42), 
            ).images[0]

            output_file = "test_output.png"
            image.save(output_file)
            logger.info(f"图片已生成并保存为: {output_file}")

        else:
            logger.error("Pipeline 创建失败")

    except Exception as e:
        logger.error(f"加载过程中发生错误: {e}")

if __name__ == "__main__":
    test_pipeline_loading()
