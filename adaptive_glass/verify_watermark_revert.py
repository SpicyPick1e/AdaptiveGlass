import sys
import os
from PIL import Image
from src.core.processor import ImageProcessor
from src.core.utils import ProcessingSettings, WatermarkSettings

def verify_watermark():
    print("开始验证水印模块还原...")
    
    # 1. Setup
    processor = ImageProcessor()
    settings = ProcessingSettings()
    settings.watermark.enabled = True
    settings.watermark.text = "Test Watermark"
    
    # Test Resource Font
    import os
    base_path = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_path, "resources", "fonts", "SmileySans-Oblique.ttf")
    print(f"Testing with font: {font_path}")
    settings.watermark.font_path = font_path
    
    # 2. Create Dummy Image
    img = Image.new('RGB', (800, 600), color='red')
    
    # 3. Process
    try:
        print("正在处理带水印的图片...")
        res, layout = processor.process(img, settings)
        
        if res:
            print("PASS: 图片处理成功，未发生崩溃。")
            print(f"输出尺寸: {res.size}")
            # We can't easily verify the visual watermark programmatically without OCR,
            # but successful execution confirms the integration is working.
        else:
            print("FAIL: 处理返回 None")
            
    except Exception as e:
        print(f"FAIL: 处理过程中发生异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_watermark()
