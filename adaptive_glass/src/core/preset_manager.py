import json
import os
from dataclasses import asdict
from .utils import ProcessingSettings, Ratio, BorderStyle, BlurMode, WatermarkMode, WatermarkSettings

class PresetManager:
    @staticmethod
    def save_preset(settings: ProcessingSettings, filepath: str):
        data = asdict(settings)
        # Convert Enums to values/names
        data['target_ratio'] = settings.target_ratio.name
        data['blur_mode'] = settings.blur_mode.value
        data['border_style'] = settings.border_style.value
        data['watermark']['text_mode'] = settings.watermark.text_mode.value
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def load_preset(filepath: str) -> ProcessingSettings:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        settings = ProcessingSettings()
        
        # Restore Enums
        if 'target_ratio' in data:
            try:
                settings.target_ratio = Ratio[data['target_ratio']]
            except:
                pass
                
        if 'blur_mode' in data:
            settings.blur_mode = BlurMode(data['blur_mode'])
            
        if 'border_style' in data:
            settings.border_style = BorderStyle(data['border_style'])
            
        # Restore other fields
        settings.blur_radius = data.get('blur_radius', 15)
        settings.blur_brightness = data.get('blur_brightness', 0)
        settings.border_color = data.get('border_color', 'black')
        settings.border_width = data.get('border_width', 0)
        settings.corner_radius = data.get('corner_radius', 20)
        settings.shadow_size = data.get('shadow_size', 20)
        settings.content_scale = data.get('content_scale', 90)
        settings.export_quality = data.get('export_quality', 95)
        
        # Restore Watermark
        wm_data = data.get('watermark', {})
        wm = settings.watermark
        wm.enabled = wm_data.get('enabled', True)
        wm.text = wm_data.get('text', "")
        if 'text_mode' in wm_data:
            wm.text_mode = WatermarkMode(wm_data['text_mode'])
        wm.text_color = wm_data.get('text_color', 'white')
        wm.font_size = wm_data.get('font_size', 20)
        wm.auto_size = wm_data.get('auto_size', True)
        wm.opacity = wm_data.get('opacity', 100)
        wm.position = wm_data.get('position', 'bottom_center')
        wm.custom_x = wm_data.get('custom_x', 0)
        wm.custom_y = wm_data.get('custom_y', 0)
        wm.font_path = wm_data.get('font_path', "SMILETSANS-OBLIQUE.TTF")
        wm.use_exif = wm_data.get('use_exif', True)
        wm.logo_path = wm_data.get('logo_path', None)
        wm.logo_auto = wm_data.get('logo_auto', False)
        wm.size_scale = wm_data.get('size_scale', 1.0)
        wm.font_bold = wm_data.get('font_bold', False)
        wm.font_italic = wm_data.get('font_italic', False)
        wm.font_underline = wm_data.get('font_underline', False)
        wm.manual_font_size = wm_data.get('manual_font_size', 14)
        wm.use_two_line = wm_data.get('use_two_line', False)
        wm.show_date = wm_data.get('show_date', False)
        
        return settings
