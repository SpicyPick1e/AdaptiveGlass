from PIL import Image, ImageFilter, ImageOps, ImageDraw
from .utils import ProcessingSettings, Ratio, BorderStyle, BlurMode

class ImageProcessor:
    def load_image(self, path: str) -> Image.Image:
        """Load an image from path."""
        try:
            return Image.open(path)
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            return None

    def process(self, image: Image.Image, settings: ProcessingSettings) -> tuple[Image.Image, dict]:
        """Main processing pipeline. Returns (image, layout_info)."""
        if not image:
            return None, {}

        # 1. Calculate target dimensions
        target_w, target_h = self._calculate_target_size(image.size, settings.target_ratio)
        
        # 2. Create background (Frosted Glass)
        background = self._create_background(image, target_w, target_h, settings)
        
        # 3. Resize original image to fit within target dimensions (maintain aspect ratio)
        img_w, img_h = image.size
        scale = min(target_w / img_w, target_h / img_h)
        
        # Apply Content Scale
        if settings.content_scale < 100:
            scale = scale * (settings.content_scale / 100.0)
            
        new_w, new_h = int(img_w * scale), int(img_h * scale)
        
        # High quality resize
        resized_img = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # 4. Apply border to the resized image BEFORE pasting
        if settings.border_style != BorderStyle.NONE:
            resized_img = self._apply_border(resized_img, settings)

        # 5. Composite
        # Center the image
        x = (target_w - new_w) // 2
        y = (target_h - new_h) // 2
        
        final_image = background.copy()
        
        # Apply Shadow
        # Apply Shadow
        if settings.shadow_size > 0:
            # Optimization: Create shadow only for the area needed
            # Make a shadow layer slightly larger than image
            s_padding = settings.shadow_size * 3
            s_w = new_w + s_padding * 2
            s_h = new_h + s_padding * 2
            
            shadow_layer = Image.new('RGBA', (s_w, s_h), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_layer)
            
            # Draw black rectangle in center of shadow layer
            # If rounded, draw rounded
            if settings.border_style == BorderStyle.ROUNDED:
                shadow_draw.rounded_rectangle([s_padding, s_padding, s_padding+new_w, s_padding+new_h], 
                                            radius=settings.corner_radius, fill=(0, 0, 0, 180)) # Semi-transparent black
            else:
                shadow_draw.rectangle([s_padding, s_padding, s_padding+new_w, s_padding+new_h], fill=(0, 0, 0, 180))
            
            # Blur shadow
            shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(settings.shadow_size))
            
            # Paste shadow onto background
            # Offset to center shadow layer
            sx = x - s_padding
            sy = y - s_padding
            
            final_image.paste(shadow_layer, (sx, sy), shadow_layer)

        final_image.paste(resized_img, (x, y), resized_img if resized_img.mode == 'RGBA' else None)
        
        layout_info = {
            'target_size': (target_w, target_h),
            'content_rect': (x, y, new_w, new_h),
            'content_scale': settings.content_scale
        }
        
        return final_image, layout_info

    def _calculate_target_size(self, original_size: tuple, ratio: Ratio) -> tuple:
        w, h = original_size
        if ratio == Ratio.ORIGINAL:
            return w, h
        
        rw, rh = ratio.value
        # Determine which dimension is the limiting factor
        # We want to expand the canvas, so we take the larger dimension required
        
        # Try matching width
        target_h_by_w = int(w * (rh / rw))
        if target_h_by_w >= h:
            return w, target_h_by_w
        
        # Match height
        target_w_by_h = int(h * (rw / rh))
        return target_w_by_h, h

    def _create_background(self, image: Image.Image, target_w: int, target_h: int, settings: ProcessingSettings) -> Image.Image:
        # Optimization: Process background at a lower resolution
        # This significantly reduces memory usage and improves speed for large images
        # The blur effect hides the loss of detail from downscaling
        
        downscale_factor = 4 # Process at 1/4 resolution (1/16th pixels)
        small_w = max(1, target_w // downscale_factor)
        small_h = max(1, target_h // downscale_factor)
        
        # Calculate scale to fill the SMALL target
        img_w, img_h = image.size
        scale = max(small_w / img_w, small_h / img_h)
        new_w, new_h = int(img_w * scale), int(img_h * scale)
        
        # Resize input image to the small size directly
        # Use Bilinear for speed, we are going to blur it anyway
        bg_small = image.resize((new_w, new_h), Image.Resampling.BILINEAR)
        
        # Crop to center (small)
        left = (new_w - small_w) // 2
        top = (new_h - small_h) // 2
        right = left + small_w
        bottom = top + small_h
        bg_small = bg_small.crop((left, top, right, bottom))
        
        # Apply blur (scale radius down too)
        # We need to adjust blur radius because we are working on a smaller image.
        # If we downscale by 4, effective blur radius should be divided by 4 to look similar?
        # No, if we blur by R on small image, and upscale by 4, the blur looks like 4*R.
        # So we should divide radius by downscale_factor.
        effective_radius = max(1, settings.blur_radius / downscale_factor)
        bg_small = bg_small.filter(ImageFilter.GaussianBlur(effective_radius))
        
        # Upscale back to target size
        # Use Bicubic or Lanczos for smoother upscale
        bg_final = bg_small.resize((target_w, target_h), Image.Resampling.BICUBIC)
        


        # Apply overlay based on mode
        if settings.blur_mode == BlurMode.DARK:
            overlay = Image.new('RGBA', bg_final.size, (0, 0, 0, 100)) # Black with ~40% opacity
            bg_final.paste(overlay, (0, 0), overlay)
        elif settings.blur_mode == BlurMode.LIGHT:
            overlay = Image.new('RGBA', bg_final.size, (255, 255, 255, 80)) # White with ~30% opacity
            bg_final.paste(overlay, (0, 0), overlay)
            
        return bg_final

    def _apply_border(self, image: Image.Image, settings: ProcessingSettings) -> Image.Image:
        if settings.border_style == BorderStyle.NONE:
            return image
            
        w, h = image.size
        
        # Convert to RGBA for transparency support
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
            
        if settings.border_style == BorderStyle.THIN:
            # Draw a rectangle border
            draw = ImageDraw.Draw(image)
            bw = settings.border_width
            draw.rectangle([0, 0, w-1, h-1], outline=settings.border_color, width=bw)
            return image
            
        elif settings.border_style == BorderStyle.ROUNDED:
            # Create a mask for rounded corners
            radius = settings.corner_radius
            mask = Image.new('L', (w, h), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle([0, 0, w, h], radius=radius, fill=255)
            
            # Apply mask
            output = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            output.paste(image, (0, 0), mask)
            
            # Draw border outline if needed
            if settings.border_width > 0:
                draw_out = ImageDraw.Draw(output)
                draw_out.rounded_rectangle([0, 0, w-1, h-1], radius=radius, outline=settings.border_color, width=settings.border_width)
            
            return output
            
        return image
