from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QPen
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QSize

class PreviewWidget(QWidget):
    watermarkMoved = pyqtSignal(int, int) # Emits new x, y

    def __init__(self):
        super().__init__()
        self.image = None
        self.pixmap = None
        self.scaled_pixmap = None
        self.scale_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        # Dragging state
        self.dragging = False
        self.last_mouse_pos = QPoint()
        
        self.init_ui()

    def init_ui(self):
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("background-color: #2b2b2b;")

    def set_image(self, image):
        """Set the QImage to display."""
        self.image = image
        if self.image:
            self.pixmap = QPixmap.fromImage(self.image)
            self.update_scaled_pixmap()
        else:
            self.pixmap = None
            self.scaled_pixmap = None
        self.update()

    def update_scaled_pixmap(self):
        if not self.pixmap:
            return
            
        # Scale pixmap to fit widget while maintaining aspect ratio
        w = self.width()
        h = self.height()
        
        if w <= 0 or h <= 0:
            return
            
        self.scaled_pixmap = self.pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        # Calculate offset to center
        self.offset_x = (w - self.scaled_pixmap.width()) // 2
        self.offset_y = (h - self.scaled_pixmap.height()) // 2
        
        # Calculate scale factor (original -> displayed)
        self.scale_factor = self.scaled_pixmap.width() / self.pixmap.width()

    def resizeEvent(self, event):
        self.update_scaled_pixmap()
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        
        if self.scaled_pixmap:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            painter.drawPixmap(self.offset_x, self.offset_y, self.scaled_pixmap)
        else:
            painter.setPen(QColor(100, 100, 100))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "拖入图片或点击打开")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging and self.scale_factor > 0:
            delta = event.pos() - self.last_mouse_pos
            self.last_mouse_pos = event.pos()
            
            # Convert delta to original image coordinates
            dx = int(delta.x() / self.scale_factor)
            dy = int(delta.y() / self.scale_factor)
            
            # Emit signal to update watermark position
            # Note: This assumes the parent will handle the logic of "current pos + delta"
            # But since we don't store the absolute watermark pos here, we might need to change logic.
            # For now, let's just emit the delta and let the main window handle it?
            # Or better, emit a signal that we are dragging.
            
            self.watermarkMoved.emit(dx, dy)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
