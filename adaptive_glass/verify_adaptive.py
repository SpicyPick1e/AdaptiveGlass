import sys
import os
from PIL import Image
from src.core.processor import ImageProcessor
from src.core.utils import ProcessingSettings, Ratio

def create_test_image(width, height, name):
    img = Image.new('RGB', (width, height), color='blue')
    return img

def verify_adaptive():
    processor = ImageProcessor()
    settings = ProcessingSettings()
    
    print("开始验证自适应比例处理...")
    
    # Case 1: Original Wider than Target (e.g. 16:9 input -> 1:1 target)
    # Should fill vertically (top/bottom)
    print("\n测试用例 1: 原图宽于目标 (16:9 -> 1:1)")
    img_wide = create_test_image(1600, 900, "wide")
    settings.target_ratio = Ratio.R_1_1
    res_wide = processor.process(img_wide, settings)
    
    expected_size = (1600, 1600)
    if res_wide.size == expected_size:
        print(f"PASS: 尺寸正确 {res_wide.size}")
    else:
        print(f"FAIL: 尺寸错误 {res_wide.size}, 期望 {expected_size}")
        
    # Check if original image is centered (simple check of pixel at center vs edge)
    # Center should be blue (original), top edge should be blurred (background)
    # Since we don't have easy way to check "blurred", we check if it's NOT blue at the very top
    # But wait, create_test_image makes a solid blue image.
    # The background generation scales it down and blurs it. So background will also be blue-ish.
    # To distinguish, let's make original image red, and check if size is correct first.
    # The requirement is mainly about the "Logic" of expansion.
    
    # Case 2: Original Narrower than Target (e.g. 4:3 input -> 16:9 target)
    # Should fill horizontally (left/right)
    print("\n测试用例 2: 原图窄于目标 (4:3 -> 16:9)")
    img_narrow = create_test_image(800, 600, "narrow")
    settings.target_ratio = Ratio.R_16_9
    res_narrow = processor.process(img_narrow, settings)
    
    # 600 height -> width should be 600 * 16/9 = 1066.66 -> 1066
    expected_w = int(600 * 16 / 9)
    expected_size_2 = (expected_w, 600)
    
    if res_narrow.size == expected_size_2:
        print(f"PASS: 尺寸正确 {res_narrow.size}")
    else:
        print(f"FAIL: 尺寸错误 {res_narrow.size}, 期望 {expected_size_2}")

    # Case 3: 9:16 Target
    print("\n测试用例 3: 目标 9:16")
    settings.target_ratio = Ratio.R_9_16
    # Input 1:1 (800x800) -> Should become 9:16?
    # 800 width -> height 800 * 16/9 = 1422
    img_square = create_test_image(800, 800, "square")
    res_vertical = processor.process(img_square, settings)
    
    expected_h = int(800 * 16 / 9)
    expected_size_3 = (800, expected_h)
    
    if res_vertical.size == expected_size_3:
        print(f"PASS: 尺寸正确 {res_vertical.size}")
    else:
        print(f"FAIL: 尺寸错误 {res_vertical.size}, 期望 {expected_size_3}")

if __name__ == "__main__":
    verify_adaptive()
