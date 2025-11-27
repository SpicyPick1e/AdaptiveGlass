from PIL import Image, ImageDraw, ImageFont, ExifTags
from .utils import WatermarkSettings, WatermarkMode
import os
import piexif

class WatermarkEngine:
    def __init__(self):
        self.font_path = "arial.ttf" # Default system font
        if os.name == 'nt':
            self.font_path = "C:\\Windows\\Fonts\\arial.ttf"

    def get_exif_data(self, image: Image.Image) -> dict:
        """Extract EXIF data using piexif for better compatibility."""
        exif_data = {}
        try:
            if 'exif' not in image.info:
                return exif_data
                
            exif_dict = piexif.load(image.info['exif'])
            
            # Helper to decode bytes to string
            def decode_if_bytes(val):
                if isinstance(val, bytes):
                    try:
                        return val.decode('utf-8').strip('\x00')
                    except:
                        return str(val)
                return val

            # 0th IFD (Image)
            if "0th" in exif_dict:
                for tag, val in exif_dict["0th"].items():
                    tag_name = piexif.TAGS["Image"].get(tag, {}).get("name", tag)
                    if tag_name in ['Make', 'Model']:
                        exif_data[tag_name] = decode_if_bytes(val)

            # Exif IFD (Photo)
            if "Exif" in exif_dict:
                for tag, val in exif_dict["Exif"].items():
                    tag_name = piexif.TAGS["Exif"].get(tag, {}).get("name", tag)
                    
                    if tag_name == 'ISOSpeedRatings':
                        exif_data['ISOSpeedRatings'] = val
                    elif tag_name == 'ExposureTime':
                        # Exposure time is usually a tuple (numerator, denominator)
                        if isinstance(val, tuple) and len(val) == 2:
                            if val[1] == 0: exif_data['ExposureTime'] = "0"
                            elif val[0] >= val[1]: exif_data['ExposureTime'] = str(val[0] / val[1])
                            else: exif_data['ExposureTime'] = f"{val[0]}/{val[1]}"
                        else:
                            exif_data['ExposureTime'] = str(val)
                    elif tag_name == 'FNumber':
                        # FNumber is usually a tuple (numerator, denominator)
                        if isinstance(val, tuple) and len(val) == 2:
                            if val[1] != 0:
                                exif_data['FNumber'] = str(round(val[0] / val[1], 1))
                            else:
                                exif_data['FNumber'] = str(val[0])
                        else:
                            exif_data['FNumber'] = str(val)
                    elif tag_name == 'FocalLength':
                        # FocalLength is usually a tuple
                        if isinstance(val, tuple) and len(val) == 2:
                            if val[1] != 0:
                                exif_data['FocalLength'] = str(round(val[0] / val[1], 1))
                            else:
                                exif_data['FocalLength'] = str(val[0])
                        else:
                            exif_data['FocalLength'] = str(val)

        except Exception as e:
            print(f"Error extracting EXIF with piexif: {e}")
            # Fallback to basic PIL if piexif fails
            try:
                exif = image.getexif()
                if exif:
                    for k, v in exif.items():
                        if k in ExifTags.TAGS:
                            tag = ExifTags.TAGS[k]
                            if tag in ['Make', 'Model', 'ISOSpeedRatings', 'ExposureTime', 'FNumber', 'FocalLength']:
                                exif_data[tag] = v
            except:
                pass
            
        return exif_data

    def _format_template(self, template: str, exif: dict) -> str:
        """Format the template string with EXIF data."""
        context = {
            'Model': str(exif.get('Model', '')),
            'FNumber': f"f/{exif.get('FNumber', '')}" if 'FNumber' in exif else '',
            'ExposureTime': f"{exif.get('ExposureTime', '')}s" if 'ExposureTime' in exif else '',
            'ISO': f"ISO{exif.get('ISOSpeedRatings', '')}" if 'ISOSpeedRatings' in exif else '',
            'FocalLength': f"{exif.get('FocalLength', '')}mm" if 'FocalLength' in exif else '',
            'Make': str(exif.get('Make', ''))
        }
        
        try:
            return template.format(**context)
        except Exception as e:
            print(f"Error formatting template: {e}")
            return template

    def render_watermark(self, image: Image.Image, settings: WatermarkSettings, exif_data: dict = None, layout_info: dict = None) -> Image.Image:
        if not settings.enabled:
            return image
            
        # Create a copy to avoid modifying original
        base_image = image.copy()
        
        # Determine text
        text = settings.text
        
        # If text is empty or contains placeholders, we need EXIF
        if not text or ("{" in text and "}" in text):
            if not exif_data:
                # Try to get from current image if not provided (fallback)
                exif_data = self.get_exif_data(base_image)
            
            if not text:
                # Default template if text is empty
                # Construct a default string from available EXIF
                # New Logic: We want to separate Model and Info for rich rendering
                pass # Logic handled below
            else:
                # Format template
                text = self._format_template(text, exif_data)
        
        # Debug: Print EXIF and Text
        # print(f"[Watermark Debug] EXIF Data: {exif_data}")
        # print(f"[Watermark Debug] Final Text: {text}")

        # Load font
        font_path_to_use = self.font_path
        if settings.font_path and os.path.exists(settings.font_path):
            font_path_to_use = settings.font_path
            
        # Calculate Base Font Size
        base_font_size = settings.font_size
        
        # Adaptive Logic
        bottom_space = 0
        if layout_info and settings.auto_size:
            target_w, target_h = layout_info['target_size']
            cx, cy, cw, ch = layout_info['content_rect']
            
            # Calculate space below content
            bottom_space = target_h - (cy + ch)
            
            if bottom_space > 20: # If there is a meaningful bottom border
                # Set font size to ~35% of bottom space
                base_font_size = int(bottom_space * 0.35)
                # Ensure minimum size
                base_font_size = max(12, base_font_size)
            else:
                # No border or very thin border
                # Set font size relative to width (e.g. 3%)
                base_font_size = int(target_w * 0.03)
                base_font_size = max(12, base_font_size)
        
        # Apply Manual Size Scale
        base_font_size = int(base_font_size * settings.size_scale)
        base_font_size = max(10, base_font_size) # Absolute minimum

        # Prepare Text Parts
        model_text = ""
        info_text = ""
        
        # Get EXIF info first
        exif_model = str(exif_data.get('Model', ''))
        if not exif_model:
            exif_model = str(exif_data.get('Make', '')) # Removed 'Camera' default
        
        info_parts = []
        iso = exif_data.get('ISOSpeedRatings', '')
        if iso: info_parts.append(f"ISO{iso}")
        f_num = exif_data.get('FNumber', '')
        if f_num: info_parts.append(f"f/{f_num}")
        exp_time = exif_data.get('ExposureTime', '')
        if exp_time: info_parts.append(f"{exp_time}s")
        focal = exif_data.get('FocalLength', '')
        if focal: info_parts.append(f"{focal}mm")
        exif_info = "  ".join(info_parts)

        # Determine final text based on mode
        if settings.text_mode == WatermarkMode.REPLACE:
            # Replace: Only show custom text (as Model part), no info
            model_text = text if text else "Custom Text"
            info_text = ""
            
        elif settings.text_mode == WatermarkMode.FALLBACK:
            # Fallback: Show EXIF if available, else Custom Text
            has_exif = bool(exif_model)
            if has_exif:
                model_text = exif_model
                info_text = exif_info
            else:
                model_text = text if text else "No EXIF"
                info_text = ""
                
        elif settings.text_mode == WatermarkMode.APPEND:
            # Append: Show EXIF, and Custom Text.
            # Smart Fallback: If no EXIF, behave like Replace (show custom text as Model)
            
            has_exif = bool(exif_model)
            
            if has_exif:
                model_text = exif_model
                info_text = exif_info
                if text:
                    if info_text:
                        info_text += f"  |  {text}"
                    else:
                        info_text = text
            else:
                # No EXIF: Fallback to showing custom text as Model (Large)
                model_text = text
                info_text = ""
        
        # If both are empty, return original image
        if not model_text and not info_text:
            return image

        # Check for Chinese characters and fallback font
        def has_chinese(s):
            for char in s:
                if '\u4e00' <= char <= '\u9fff':
                    return True
            return False

        current_font_path = font_path_to_use
        if has_chinese(model_text) or has_chinese(info_text):
            # If current font is likely not supporting Chinese (e.g. the default English one)
            # We switch to Microsoft YaHei
            if "SMILETSANS" in current_font_path.upper() or "ARIAL" in current_font_path.upper():
                if os.name == 'nt':
                    msyh = "C:\\Windows\\Fonts\\msyh.ttc"
                    simhei = "C:\\Windows\\Fonts\\simhei.ttf"
                    if os.path.exists(msyh):
                        current_font_path = msyh
                    elif os.path.exists(simhei):
                        current_font_path = simhei

        # Load Fonts
        try:
            font_model = ImageFont.truetype(current_font_path, base_font_size)
        except IOError:
            font_model = ImageFont.load_default()
            
        try:
            # Info font is smaller (e.g. 70%)
            info_font_size = int(base_font_size * 0.7)
            font_info = ImageFont.truetype(current_font_path, info_font_size)
        except IOError:
            font_info = ImageFont.load_default()

        # Measure Text
        draw_temp = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        
        w_model = 0
        h_model = 0
        if model_text:
            bbox_model = draw_temp.textbbox((0, 0), model_text, font=font_model)
            w_model = bbox_model[2] - bbox_model[0]
            h_model = bbox_model[3] - bbox_model[1]
        
        w_info = 0
        h_info = 0
        if info_text:
            bbox_info = draw_temp.textbbox((0, 0), info_text, font=font_info)
            w_info = bbox_info[2] - bbox_info[0]
            h_info = bbox_info[3] - bbox_info[1]
            
        # Layout Calculation
        gap = int(base_font_size * 0.8) if (model_text and info_text) else 0 # Only add gap if both exist
        total_w = w_model + gap + w_info
        max_h = max(h_model, h_info)
        
        # Create a transparent layer for the watermark
        txt_layer = Image.new('RGBA', base_image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        w, h = base_image.size
        padding = 20
        
        # Position
        x, y = 0, 0
        
        # Adaptive Positioning
        if settings.position == "bottom_center" and settings.auto_size and layout_info and bottom_space > 20:
             cx, cy, cw, ch = layout_info['content_rect']
             center_y_of_space = (cy + ch) + (bottom_space / 2)
             
             x = (w - total_w) // 2
             y = int(center_y_of_space - (max_h / 2))
             
             # Ensure it doesn't go off screen
             y = min(y, h - max_h - 5)
             
        elif settings.position == "bottom_right":
            x = w - total_w - padding
            y = h - max_h - padding
        elif settings.position == "bottom_left":
            x = padding
            y = h - max_h - padding
        elif settings.position == "bottom_center":
            x = (w - total_w) // 2
            y = h - max_h - padding
        elif settings.position == "center":
            x = (w - total_w) // 2
            y = (h - max_h) // 2
        elif settings.position == "manual":
            x = settings.custom_x
            y = settings.custom_y
            
        # Draw text
        # Color with opacity
        base_color = (255, 255, 255) if settings.text_color == "white" else (0, 0, 0)
        color = (*base_color, int(255 * (settings.opacity / 100)))
        
        # Shadow
        shadow_rgb = (0, 0, 0) if settings.text_color == "white" else (255, 255, 255)
        shadow_color = (*shadow_rgb, int(128 * (settings.opacity / 100)))
        
        # Draw Model Name
        if model_text:
            y_model = y + (max_h - h_model) // 2
            draw.text((x+1, y_model+1), model_text, font=font_model, fill=shadow_color)
            draw.text((x, y_model), model_text, font=font_model, fill=color)
        
        # Info
        if info_text:
            x_info = x + w_model + gap
            y_info = y + (max_h - h_info) // 2
            # Fine tune y_info to align baselines roughly
            if model_text:
                y_info += int(h_model * 0.1) 
            
            draw.text((x_info+1, y_info+1), info_text, font=font_info, fill=shadow_color)
            draw.text((x_info, y_info), info_text, font=font_info, fill=color)
        
        # Composite
        if base_image.mode != 'RGBA':
            base_image = base_image.convert('RGBA')
            
        return Image.alpha_composite(base_image, txt_layer)
