import sys
import os
from PIL import Image, ImageDraw
from src.core.processor import ImageProcessor
from src.core.watermark import WatermarkEngine
from src.core.utils import ProcessingSettings, Ratio, BorderStyle, BlurMode, WatermarkSettings

def create_dummy_image(path):
    img = Image.new('RGB', (800, 600), color = 'red')
    d = ImageDraw.Draw(img)
    d.text((10,10), "Hello World", fill=(255,255,0))
    img.save(path)
    return path

def test_processor():
    print("Testing ImageProcessor...")
    dummy_path = "test_image.jpg"
    create_dummy_image(dummy_path)
    
    processor = ImageProcessor()
    img = processor.load_image(dummy_path)
    if not img:
        print("FAIL: Could not load image")
        return
        
    settings = ProcessingSettings()
    settings.target_ratio = Ratio.R_1_1 # 1:1
    settings.blur_radius = 10
    
    result, _ = processor.process(img, settings)
    if result.size != (800, 800): # Should be square, based on max dimension (800)
        print(f"FAIL: Result size {result.size} != (800, 800)")
    else:
        print("PASS: 1:1 Ratio processing")
        
    # Test 16:9
    settings.target_ratio = Ratio.R_16_9
    result, _ = processor.process(img, settings)
    # 800 width -> height should be 800 * 9/16 = 450. But 600 height > 450.
    # So height 600 -> width should be 600 * 16/9 = 1066.
    # So target should be (1066, 600)
    expected_w = int(600 * 16 / 9)
    if result.size != (expected_w, 600):
        print(f"FAIL: Result size {result.size} != ({expected_w}, 600)")
    else:
        print("PASS: 16:9 Ratio processing")
        
    os.remove(dummy_path)
    
    # Test Blur Modes
    print("Testing Blur Modes...")
    settings.blur_mode = BlurMode.DARK
    res_dark, _ = processor.process(img, settings)
    if res_dark:
        print("PASS: Dark Blur Mode processed")
        
    settings.blur_mode = BlurMode.LIGHT
    res_light, _ = processor.process(img, settings)
    if res_light:
        print("PASS: Light Blur Mode processed")
        
    # Test Shadow
    print("Testing Shadow...")
    settings.shadow_size = 20
    res_shadow, _ = processor.process(img, settings)
    if res_shadow:
        print("PASS: Shadow processed")

    # Test Content Scale
    print("Testing Content Scale...")
    settings.target_ratio = Ratio.R_1_1
    settings.content_scale = 80
    res_scale, _ = processor.process(img, settings)
    # Check if image content is smaller than canvas
    # Hard to check programmatically without complex analysis, 
    # but we can check if it runs without error and returns correct size
    if res_scale and res_scale.size == (800, 800): # Should still be target size
        print("PASS: Content Scale processed")

    # Test Border Color and Radius
    settings.border_style = BorderStyle.ROUNDED
    settings.border_color = "black"
    settings.corner_radius = 15
    processed, _ = processor.process(img, settings)
    print("PASS: Border Color and Radius processed")

    # Test WatermarkEngine
    print("Testing WatermarkEngine...")
    wm_engine = WatermarkEngine()
    
    # Test EXIF extraction (Mocking piexif behavior requires an image with real EXIF, 
    # but we can test if the function runs without error on a blank image)
    exif = wm_engine.get_exif_data(img)
    print(f"PASS: EXIF extraction ran (Empty result expected for blank image: {exif})")

    wm_settings = WatermarkSettings(enabled=True, text="Test", position="bottom_right")
    res = wm_engine.render_watermark(processed, wm_settings)
    if res:
        print("PASS: Watermark rendering ran")
        
    wm_settings.position = "bottom_center"
    res = wm_engine.render_watermark(processed, wm_settings)
    if res:
        print("PASS: Watermark bottom_center ran")

    # Test Watermark Color
    wm_settings.text_color = "black"
    res_color = wm_engine.render_watermark(processed, wm_settings)
    if res_color:
        print("PASS: Watermark black color ran")

    # Test Adaptive Sizing
    # Need layout info
    layout_info = {
        'target_size': (800, 800),
        'content_rect': (0, 100, 800, 600), # 100px top/bottom border
        'content_scale': 100
    }
    wm_settings.auto_size = True
    wm_settings.position = "bottom_center"
    res_adaptive = wm_engine.render_watermark(processed, wm_settings, layout_info=layout_info)
    if res_adaptive:
        print("PASS: Adaptive Watermark ran")
    
    # Test Templates
    print("Testing Watermark Templates...")
    wm_settings.text = "Model: {Model} | ISO: {ISO}"
    # We need an image with EXIF for real test, but dummy image has no EXIF.
    # It should handle missing EXIF gracefully (empty strings).
    res_tmpl = wm_engine.render_watermark(img, wm_settings)
    if res_tmpl:
        print("PASS: Watermark Template rendering ran")

if __name__ == "__main__":
    test_processor()
