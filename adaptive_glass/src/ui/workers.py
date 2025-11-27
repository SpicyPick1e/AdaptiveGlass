from PyQt6.QtCore import QThread, pyqtSignal
import os
from PyQt6.QtGui import QImage
from PIL import Image
from src.core.processor import ImageProcessor
from src.core.watermark import WatermarkEngine
from src.core.utils import ProcessingSettings

class ImageWorker(QThread):
    resultReady = pyqtSignal(QImage)
    
    def __init__(self, image_path, settings):
        super().__init__()
        self.image_path = image_path
        self.settings = settings
        self.processor = ImageProcessor()
        self.watermarker = WatermarkEngine()
        self.loaded_image = None

    def run(self):
        if not self.loaded_image and self.image_path:
            self.loaded_image = self.processor.load_image(self.image_path)
            
        if self.loaded_image:
            # 1. Process (Resize + Blur + Border)
            processed, layout_info = self.processor.process(self.loaded_image, self.settings)
            
            # 2. Watermark
            if self.settings.watermark.enabled:
                # Extract EXIF from ORIGINAL image
                exif_data = self.watermarker.get_exif_data(self.loaded_image)
                processed = self.watermarker.render_watermark(processed, self.settings.watermark, exif_data, layout_info)
            
            # Convert to QImage
            # Ensure we have RGBA for consistency
            if processed.mode != "RGBA":
                processed = processed.convert("RGBA")
                
            data = processed.tobytes("raw", "BGRA")
            # Create QImage from data. IMPORTANT: Must .copy() to ensure QImage owns the data
            # because 'data' is a local variable and will be garbage collected.
            qim = QImage(data, processed.width, processed.height, QImage.Format.Format_ARGB32).copy()
            
            self.resultReady.emit(qim)

    def update_settings(self, settings):
        self.settings = settings
        self.start()

class SaveWorker(QThread):
    finished = pyqtSignal(bool, str) # success, message
    
    def __init__(self, image, file_path, quality=95):
        super().__init__()
        self.image = image
        self.file_path = file_path
        self.quality = quality
        
    def run(self):
        try:
            ext = os.path.splitext(self.file_path)[1].lower()
            if ext in ['.jpg', '.jpeg']:
                self.image.save(self.file_path, quality=self.quality)
            else:
                self.image.save(self.file_path)
            self.finished.emit(True, self.file_path)
        except Exception as e:
            self.finished.emit(False, str(e))
