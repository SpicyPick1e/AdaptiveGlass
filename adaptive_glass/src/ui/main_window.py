import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QSplitter, 
                             QFileDialog, QMessageBox, QToolBar, QStatusBar)
from PyQt6.QtGui import QAction, QIcon, QDragEnterEvent, QDropEvent
from PyQt6.QtCore import Qt

from src.ui.preview import PreviewWidget
from src.ui.settings import SettingsPanel
from src.ui.workers import ImageWorker, SaveWorker
from src.ui.batch_dialog import BatchDialog
from src.ui.styles import DARK_THEME

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("自适应图片比例处理软件")
        self.resize(1200, 800)
        self.setStyleSheet(DARK_THEME)
        
        self.current_image_path = None
        self.worker = None
        self.save_worker = None
        
        self.init_ui()
        self.setup_actions()
        print("MainWindow: Actions setup complete")
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        print("MainWindow: Initialization complete")

    def init_ui(self):
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Preview
        self.preview = PreviewWidget()
        self.preview.watermarkMoved.connect(self.on_watermark_moved)
        splitter.addWidget(self.preview)
        
        # Settings
        self.settings_panel = SettingsPanel()
        self.settings_panel.settingsChanged.connect(self.on_settings_changed)
        splitter.addWidget(self.settings_panel)
        
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

    def setup_actions(self):
        # Toolbar
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        open_action = QAction("打开图片", self)
        open_action.triggered.connect(self.open_image)
        toolbar.addAction(open_action)
        
        save_action = QAction("导出图片", self)
        save_action.triggered.connect(self.save_image)
        toolbar.addAction(save_action)

        batch_action = QAction("批量处理", self)
        batch_action.triggered.connect(self.open_batch_dialog)
        toolbar.addAction(batch_action)

    def open_batch_dialog(self):
        dialog = BatchDialog(self.settings_panel.settings, self)
        dialog.exec()

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.load_image(file_path)

    def load_image(self, path):
        self.current_image_path = path
        self.status_bar.showMessage(f"已加载: {path}")
        self.process_image()

    def process_image(self):
        if not self.current_image_path:
            return
            
        settings = self.settings_panel.settings
        
        # Cancel previous worker if running
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            
        self.worker = ImageWorker(self.current_image_path, settings)
        self.worker.resultReady.connect(self.on_processing_finished)
        self.worker.start()
        self.status_bar.showMessage("处理中...")

    def on_processing_finished(self, qimage):
        self.preview.set_image(qimage)
        self.status_bar.showMessage("处理完成")

    def on_settings_changed(self, settings):
        self.process_image()

    def on_watermark_moved(self, dx, dy):
        # Update settings with new position
        current_settings = self.settings_panel.settings
        
        if current_settings.watermark.position != "manual":
            self.settings_panel.set_position_mode("manual")
            # We might want to initialize custom_x/y to a reasonable start if they were 0
            # But for now, let's just let them accumulate delta.
            
        current_settings.watermark.custom_x += dx
        current_settings.watermark.custom_y += dy
        
        # Trigger update
        self.process_image()

    def save_image(self):
        if not self.preview.image:
            return
            
        # Default filename logic
        default_path = ""
        if self.current_image_path:
            dir_name = os.path.dirname(self.current_image_path)
            base_name = os.path.basename(self.current_image_path)
            name, ext = os.path.splitext(base_name)
            default_filename = f"{name}_border{ext}"
            default_path = os.path.join(dir_name, default_filename)
        
        # Filters
        filters = "PNG (*.png);;JPEG (*.jpg);;All Files (*)"
        
        # Select initial filter based on extension
        selected_filter = ""
        if default_path.lower().endswith(('.jpg', '.jpeg')):
            selected_filter = "JPEG (*.jpg)"
        elif default_path.lower().endswith('.png'):
            selected_filter = "PNG (*.png)"
            
        file_path, _ = QFileDialog.getSaveFileName(self, "保存图片", default_path, filters, selected_filter)
        
        if file_path:
            quality = self.settings_panel.settings.export_quality
            
            # Disable UI
            self.status_bar.showMessage("正在导出...")
            self.setEnabled(False)
            
            self.save_worker = SaveWorker(self.preview.image, file_path, quality)
            self.save_worker.finished.connect(self.on_save_finished)
            self.save_worker.start()

    def on_save_finished(self, success, message):
        self.setEnabled(True)
        if success:
            self.status_bar.showMessage(f"已保存: {message}")
            QMessageBox.information(self, "成功", f"图片已保存至:\n{message}")
        else:
            self.status_bar.showMessage("保存失败")
            QMessageBox.critical(self, "错误", f"保存失败:\n{message}")

    # Drag and Drop
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.load_image(files[0])

    def showEvent(self, event):
        print("MainWindow: showEvent triggered")
        super().showEvent(event)

    def closeEvent(self, event):
        print("MainWindow: closeEvent triggered")
        super().closeEvent(event)
