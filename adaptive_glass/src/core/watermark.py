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
                exif_data = self.get_exif_data(base_image)
            
            if text:
                text = self._format_template(text, exif_data)
        
        # Load font
        font_path_to_use = self.font_path
        if settings.font_path and os.path.exists(settings.font_path):
            font_path_to_use = settings.font_path
            
        # --- 1. Advanced Layout Calculation ---
        
        # Default layout values
        target_w, target_h = base_image.size
        content_rect = (0, 0, target_w, target_h)
        
        border_top = 0
        border_bottom = 0
        border_left = 0
        border_right = 0
        
        if layout_info:
            target_w, target_h = layout_info.get('target_size', base_image.size)
            content_rect = layout_info.get('content_rect', (0, 0, target_w, target_h))
            cx, cy, cw, ch = content_rect
            
            border_top = cy
            border_bottom = target_h - (cy + ch)
            border_left = cx
            border_right = target_w - (cx + cw)

        # --- 2. Adaptive Font Size Calculation ---
        
        base_font_size = settings.font_size
        
        if settings.auto_size:
            pos = settings.position
            
            # Determine if we are in a vertical zone (Top/Bottom) or horizontal/side zone
            is_vertical_zone = "top" in pos or "bottom" in pos
            
            if is_vertical_zone:
                # Use the larger of top/bottom borders as reference if they exist
                # This ensures consistency if top and bottom borders are similar
                ref_border_h = max(border_top, border_bottom)
                
                if ref_border_h > 20:
                    # We have a meaningful border
                    base_font_size = int(ref_border_h * 0.35)
                else:
                    # No border, use width-based fallback
                    base_font_size = int(target_w * 0.03)
            else:
                # Side zones (center_left, center_right) or center
                # Check if we have side borders
                ref_border_w = max(border_left, border_right)
                
                if "left" in pos or "right" in pos:
                    if ref_border_w > 20:
                         # Fit within side border width (conservative)
                         # Assuming text might be long, we limit size based on width but also height to avoid huge text
                         base_font_size = int(ref_border_w * 0.15) # Heuristic
                         # Also clamp by total height to avoid being too huge
                         base_font_size = min(base_font_size, int(target_h * 0.05))
                    else:
                        base_font_size = int(target_w * 0.03)
                else:
                    # Center
                    base_font_size = int(target_w * 0.03)
            
            # Minimum size
            base_font_size = max(12, base_font_size)
        
        # Apply Manual Size Scale
        base_font_size = int(base_font_size * settings.size_scale)
        base_font_size = max(10, base_font_size)

        # --- 3. Text Preparation ---
        model_text = ""
        info_text = ""
        
        exif_model = str(exif_data.get('Model', ''))
        if not exif_model:
            exif_model = str(exif_data.get('Make', ''))
        
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

        if settings.text_mode == WatermarkMode.REPLACE:
            model_text = text if text else "Custom Text"
        elif settings.text_mode == WatermarkMode.FALLBACK:
            if exif_model:
                model_text = exif_model
                info_text = exif_info
            else:
                model_text = text if text else "No EXIF"
        elif settings.text_mode == WatermarkMode.APPEND:
            if exif_model:
                model_text = exif_model
                info_text = exif_info
                if text:
                    if info_text: info_text += f"  |  {text}"
                    else: info_text = text
            else:
                model_text = text
        
        if not model_text and not info_text:
            return image

        # Chinese Font Fallback
        def has_chinese(s):
            return any('\u4e00' <= char <= '\u9fff' for char in s)

        current_font_path = font_path_to_use
        if has_chinese(model_text) or has_chinese(info_text):
            if "SMILETSANS" in current_font_path.upper() or "ARIAL" in current_font_path.upper():
                if os.name == 'nt':
                    msyh = "C:\\Windows\\Fonts\\msyh.ttc"
                    simhei = "C:\\Windows\\Fonts\\simhei.ttf"
                    if os.path.exists(msyh): current_font_path = msyh
                    elif os.path.exists(simhei): current_font_path = simhei

        # Load Fonts
        try:
            font_model = ImageFont.truetype(current_font_path, base_font_size)
            info_font_size = int(base_font_size * 0.7)
            font_info = ImageFont.truetype(current_font_path, info_font_size)
        except IOError:
            font_model = ImageFont.load_default()
            font_info = ImageFont.load_default()

        # Measure Text
        draw_temp = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
        
        def get_size(txt, font):
            if not txt: return 0, 0
            bbox = draw_temp.textbbox((0, 0), txt, font=font)
            return bbox[2] - bbox[0], bbox[3] - bbox[1]
            
        w_model, h_model = get_size(model_text, font_model)
        w_info, h_info = get_size(info_text, font_info)
            
        gap = int(base_font_size * 0.8) if (model_text and info_text) else 0
        total_w = w_model + gap + w_info
        max_h = max(h_model, h_info)
        
        # --- 4. Smart Positioning & Alignment ---
        
        # Create layer
        txt_layer = Image.new('RGBA', base_image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        pos = settings.position
        padding = 20
        x, y = 0, 0
        
        # Smart Y Calculation
        if "top" in pos:
            # Top Zone
            if border_top > 20:
                # Center vertically in top border
                center_y = border_top / 2
                y = int(center_y - (max_h / 2))
            else:
                y = padding
        elif "bottom" in pos:
            # Bottom Zone
            if border_bottom > 20:
                # Center vertically in bottom border
                # Bottom border starts at (cy + ch)
                start_y = content_rect[1] + content_rect[3]
                center_y = start_y + (border_bottom / 2)
                y = int(center_y - (max_h / 2))
            else:
                y = target_h - max_h - padding
        else:
            # Center Y
            y = (target_h - max_h) // 2

        # Smart X Calculation
        if "left" in pos:
            if "center" in pos: # center_left
                if border_left > 20:
                    # Center horizontally in left border
                    center_x = border_left / 2
                    x = int(center_x - (total_w / 2))
                else:
                    x = padding
            else: # top_left, bottom_left
                x = padding
        elif "right" in pos:
            if "center" in pos: # center_right
                if border_right > 20:
                    # Center horizontally in right border
                    # Right border starts at (cx + cw)
                    start_x = content_rect[0] + content_rect[2]
                    center_x = start_x + (border_right / 2)
                    x = int(center_x - (total_w / 2))
                else:
                    x = target_w - total_w - padding
            else: # top_right, bottom_right
                x = target_w - total_w - padding
        else:
            # Center X (top_center, bottom_center, center)
            x = (target_w - total_w) // 2
            
        # --- 5. Fixed Alignment (Bottom Baseline) ---
        
        # Colors
        base_color = (255, 255, 255) if settings.text_color == "white" else (0, 0, 0)
        color = (*base_color, int(255 * (settings.opacity / 100)))
        shadow_rgb = (0, 0, 0) if settings.text_color == "white" else (255, 255, 255)
        shadow_color = (*shadow_rgb, int(128 * (settings.opacity / 100)))
        
        # Draw Model
        if model_text:
            # Always align bottom (Baseline)
            # The text block starts at y and has height max_h.
            # We want the bottom of the text to be at y + max_h.
            # So the top of the text should be at (y + max_h) - h_text.
            
            y_model = y + (max_h - h_model)

            draw.text((x+1, y_model+1), model_text, font=font_model, fill=shadow_color)
            draw.text((x, y_model), model_text, font=font_model, fill=color)
            
        # Draw Info
        if info_text:
            x_info = x + w_model + gap
            
            # Always align bottom (Baseline)
            y_info = y + (max_h - h_info)
            
            draw.text((x_info+1, y_info+1), info_text, font=font_info, fill=shadow_color)
            draw.text((x_info, y_info), info_text, font=font_info, fill=color)
            
        # Composite
        if base_image.mode != 'RGBA':
            base_image = base_image.convert('RGBA')
            
        return Image.alpha_composite(base_image, txt_layer)
