import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QListWidget, QFileDialog, QLabel, QProgressBar, QMessageBox,
                             QGroupBox, QFormLayout, QLineEdit, QComboBox)
from src.core.utils import Ratio, BorderStyle
from PyQt6.QtCore import QThread, pyqtSignal
from src.core.processor import ImageProcessor
from src.core.watermark import WatermarkEngine
from PIL import Image

class BatchWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    
    def __init__(self, file_paths, output_dir, settings, suffix="_processed", out_format="Auto"):
        super().__init__()
        self.file_paths = file_paths
        self.output_dir = output_dir
        self.settings = settings
        self.suffix = suffix
        self.out_format = out_format
        self.processor = ImageProcessor()
        self.watermarker = WatermarkEngine()
        self.running = True

    def run(self):
        total = len(self.file_paths)
        for i, path in enumerate(self.file_paths):
            if not self.running:
                break
                
            try:
                # Load
                img = self.processor.load_image(path)
                if not img:
                    continue
                    
                # Process
                processed, layout_info = self.processor.process(img, self.settings)
                
                # Watermark
                if self.settings.watermark.enabled:
                    # Fix: Extract EXIF from ORIGINAL image
                    exif_data = self.watermarker.get_exif_data(img)
                    processed = self.watermarker.render_watermark(processed, self.settings.watermark, exif_data, layout_info)
                
                # Save
                filename = os.path.basename(path)
                name, ext = os.path.splitext(filename)
                
                # Determine output format and extension
                save_ext = ext
                if self.out_format == "PNG":
                    save_ext = ".png"
                elif self.out_format == "JPG":
                    save_ext = ".jpg"
                
                save_name = f"{name}{self.suffix}{save_ext}"
                save_path = os.path.join(self.output_dir, save_name)
                
                if save_ext.lower() in ['.jpg', '.jpeg']:
                    if processed.mode == 'RGBA':
                        processed = processed.convert('RGB')
                    processed.save(save_path, quality=self.settings.export_quality)
                else:
                    processed.save(save_path)
                
            except Exception as e:
                print(f"Error processing {path}: {e}")
            
            self.progress.emit(int((i + 1) / total * 100))
            
        self.finished.emit()

    def stop(self):
        self.running = False

class BatchDialog(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("批量处理")
        self.resize(600, 500)
        self.settings = settings
        self.worker = None
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Settings Summary
        summary_group = QGroupBox("当前设置摘要")
        summary_layout = QFormLayout()
        
        # Create summary text
        summary = f"目标比例: {self.settings.target_ratio.name}\n"
        summary += f"内容缩放: {self.settings.content_scale}%\n"
        summary += f"模糊强度: {self.settings.blur_radius} (风格: {self.settings.blur_mode.value})\n"
        
        border_text = self.settings.border_style.value
        if self.settings.border_style != BorderStyle.NONE:
            border_text += f" (宽: {self.settings.border_width}, 圆角: {self.settings.corner_radius}, 阴影: {self.settings.shadow_size})"
        summary += f"边框样式: {border_text}\n"
        summary += f"边框颜色: {self.settings.border_color}\n"
        
        wm_status = "启用" if self.settings.watermark.enabled else "禁用"
        if self.settings.watermark.enabled:
            wm_status += f" (模式: {self.settings.watermark.text_mode.value})"
            if self.settings.watermark.text:
                wm_status += f" [自定义: {self.settings.watermark.text}]"
        summary += f"水印状态: {wm_status}\n"
        
        summary += f"导出质量: {self.settings.export_quality}"
        
        self.summary_label = QLabel(summary)
        summary_layout.addRow(self.summary_label)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # File List
        self.file_list = QListWidget()
        layout.addWidget(QLabel("待处理文件:"))
        layout.addWidget(self.file_list)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("添加文件")
        self.add_btn.clicked.connect(self.add_files)
        self.clear_btn = QPushButton("清空列表")
        self.clear_btn.clicked.connect(self.file_list.clear)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.clear_btn)
        layout.addLayout(btn_layout)
        
        # Output Options
        opts_group = QGroupBox("输出选项")
        opts_layout = QFormLayout()
        
        self.suffix_edit = QLineEdit("_processed")
        opts_layout.addRow("文件名后缀:", self.suffix_edit)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Auto (原格式)", "PNG", "JPG"])
        opts_layout.addRow("输出格式:", self.format_combo)
        
        opts_group.setLayout(opts_layout)
        layout.addWidget(opts_group)
        
        # Output Dir
        out_layout = QHBoxLayout()
        self.out_label = QLabel("输出目录: 未选择")
        self.out_btn = QPushButton("选择输出目录")
        self.out_btn.clicked.connect(self.select_output_dir)
        out_layout.addWidget(self.out_label)
        out_layout.addWidget(self.out_btn)
        layout.addLayout(out_layout)
        
        # Progress
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Action Buttons
        action_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始处理")
        self.start_btn.clicked.connect(self.start_processing)
        self.start_btn.setEnabled(False)
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        action_layout.addWidget(self.start_btn)
        action_layout.addWidget(self.close_btn)
        layout.addLayout(action_layout)
        
        self.setLayout(layout)
        self.output_dir = None

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择图片", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if files:
            self.file_list.addItems(files)
            self.check_ready()

    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if dir_path:
            self.output_dir = dir_path
            self.out_label.setText(f"输出目录: {dir_path}")
            self.check_ready()

    def check_ready(self):
        if self.file_list.count() > 0 and self.output_dir:
            self.start_btn.setEnabled(True)
        else:
            self.start_btn.setEnabled(False)

    def start_processing(self):
        files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        suffix = self.suffix_edit.text()
        fmt_text = self.format_combo.currentText()
        out_format = "Auto"
        if "PNG" in fmt_text: out_format = "PNG"
        elif "JPG" in fmt_text: out_format = "JPG"
        
        self.worker = BatchWorker(files, self.output_dir, self.settings, suffix, out_format)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_finished)
        
        self.start_btn.setEnabled(False)
        self.add_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        self.out_btn.setEnabled(False)
        self.suffix_edit.setEnabled(False)
        self.format_combo.setEnabled(False)
        
        self.worker.start()

    def on_finished(self):
        QMessageBox.information(self, "完成", "批量处理已完成！")
        self.start_btn.setEnabled(True)
        self.add_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        self.out_btn.setEnabled(True)
        self.suffix_edit.setEnabled(True)
        self.format_combo.setEnabled(True)
        self.progress_bar.setValue(0)
