from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, Optional
import sys
import os

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # In dev mode, we are in src/core/utils.py
        # We want to go up to adaptive_glass root
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    return os.path.join(base_path, relative_path)

class Ratio(Enum):
    R_1_1 = (1, 1)
    R_4_3 = (4, 3)
    R_16_9 = (16, 9)
    R_9_16 = (9, 16)
    ORIGINAL = (0, 0)

class BorderStyle(Enum):
    NONE = "none"
    THIN = "thin"
    ROUNDED = "rounded"

class BlurMode(Enum):
    STANDARD = "standard"
    DARK = "dark"
    LIGHT = "light"

class WatermarkMode(Enum):
    REPLACE = "replace"
    FALLBACK = "fallback"
    APPEND = "append"

@dataclass
class WatermarkSettings:
    enabled: bool = True
    text: str = ""
    text_mode: WatermarkMode = WatermarkMode.APPEND
    text_color: str = "white" # white, black
    font_size: int = 20
    auto_size: bool = True
    opacity: int = 100  # 0-100
    position: str = "bottom_center" # bottom_right, bottom_left, center, manual
    custom_x: int = 0
    custom_y: int = 0
    font_path: str = "SMILETSANS-OBLIQUE.TTF"
    use_exif: bool = True
    logo_path: Optional[str] = None
    size_scale: float = 1.0

@dataclass
class ProcessingSettings:
    target_ratio: Ratio = Ratio.R_4_3
    blur_mode: BlurMode = BlurMode.STANDARD
    blur_radius: int = 15
    border_style: BorderStyle = BorderStyle.ROUNDED
    border_color: str = "black" # white, black
    border_width: int = 0
    corner_radius: int = 20
    shadow_size: int = 20
    content_scale: int = 90 # 50-100%
    export_quality: int = 95
    watermark: WatermarkSettings = field(default_factory=WatermarkSettings)
