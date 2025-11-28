from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QComboBox, 
                             QSlider, QRadioButton, QGroupBox, QCheckBox, 
                             QLineEdit, QLabel, QHBoxLayout, QSpinBox, QButtonGroup, 
                             QFileDialog, QPushButton, QMessageBox, QScrollArea)
import os
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from src.core.utils import ProcessingSettings, Ratio, BorderStyle, WatermarkSettings, BlurMode, WatermarkMode, get_resource_path
from src.core.preset_manager import PresetManager

class SettingsPanel(QWidget):
    settingsChanged = pyqtSignal(ProcessingSettings)

    def __init__(self):
        super().__init__()
        self.settings = ProcessingSettings()
        
        # Debounce timer
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.emit_settings_changed)
        
        self.init_ui()
        print("SettingsPanel: Init complete")

    def init_ui(self):
        print("SettingsPanel: Starting init_ui")
        
        # Main Layout (Scroll Area)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Preset Controls
        preset_layout = QHBoxLayout()
        self.btn_save_preset = QPushButton("保存预设")
        self.btn_load_preset = QPushButton("加载预设")
        self.btn_save_preset.clicked.connect(self.save_preset)
        self.btn_load_preset.clicked.connect(self.load_preset)
        preset_layout.addWidget(self.btn_save_preset)
        preset_layout.addWidget(self.btn_load_preset)
        layout.addLayout(preset_layout)
        
        # Ratio Selection
        ratio_group = QGroupBox("目标比例")
        ratio_layout = QFormLayout()
        self.ratio_combo = QComboBox()
        self.ratio_combo.addItem("1:1 (Instagram)", Ratio.R_1_1)
        self.ratio_combo.addItem("4:3", Ratio.R_4_3)
        self.ratio_combo.addItem("3:2 (Full Frame)", Ratio.R_3_2)
        self.ratio_combo.addItem("16:9 (Youtube)", Ratio.R_16_9)
        self.ratio_combo.addItem("9:16 (TikTok)", Ratio.R_9_16)
        self.ratio_combo.addItem("2.35:1 (Cinema)", Ratio.R_2_35_1)
        self.ratio_combo.addItem("原始比例", Ratio.ORIGINAL)
        self.ratio_combo.setCurrentIndex(1) # Default 4:3
        self.ratio_combo.currentIndexChanged.connect(self.update_settings)
        ratio_layout.addRow("选择比例:", self.ratio_combo)
        ratio_group.setLayout(ratio_layout)
        layout.addWidget(ratio_group)

        # Content Scale
        scale_group = QGroupBox("内容缩放")
        scale_layout = QFormLayout()
        self.scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.scale_slider.setRange(50, 100)
        self.scale_slider.setValue(90) # Default 90%
        self.scale_slider.valueChanged.connect(self.update_settings)
        scale_layout.addRow("缩放比例:", self.scale_slider)
        scale_group.setLayout(scale_layout)
        layout.addWidget(scale_group)

        # Blur Settings
        blur_group = QGroupBox("背景模糊")
        blur_layout = QFormLayout()
        self.blur_slider = QSlider(Qt.Orientation.Horizontal)
        self.blur_slider.setRange(0, 50)
        self.blur_slider.setValue(15)
        self.blur_slider.valueChanged.connect(self.update_settings)
        blur_layout.addRow("模糊强度:", self.blur_slider)
        
        # Blur Mode
        self.blur_mode_combo = QComboBox()
        self.blur_mode_combo.addItem("标准模糊", BlurMode.STANDARD)
        self.blur_mode_combo.addItem("暗色玻璃", BlurMode.DARK)
        self.blur_mode_combo.addItem("亮色玻璃", BlurMode.LIGHT)
        self.blur_mode_combo.currentIndexChanged.connect(self.update_settings)
        blur_layout.addRow("模糊风格:", self.blur_mode_combo)
        
        blur_group.setLayout(blur_layout)
        layout.addWidget(blur_group)

        # Helper to create slider with input
        def create_slider_with_input(min_val, max_val, default_val, layout, label_text):
            container = QWidget()
            h_layout = QHBoxLayout(container)
            h_layout.setContentsMargins(0, 0, 0, 0)
            
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(min_val, max_val)
            slider.setValue(default_val)
            
            spinbox = QSpinBox()
            spinbox.setRange(min_val, max_val)
            spinbox.setValue(default_val)
            spinbox.setFixedWidth(60)
            
            # Sync slider and spinbox
            slider.valueChanged.connect(spinbox.setValue)
            spinbox.valueChanged.connect(slider.setValue)
            slider.valueChanged.connect(self.update_settings)
            
            h_layout.addWidget(slider)
            h_layout.addWidget(spinbox)
            
            layout.addRow(label_text, container)
            return slider, spinbox

        # Re-implement sliders using helper
        # Clear existing layouts first if needed? No, we are building fresh.
        # Wait, I need to replace the blocks above.
        # Let's just add the new brightness slider here for now and refactor others later or now?
        # The user asked for "Input Fields: Add numeric input fields next to existing and new sliders."
        # So I should refactor existing sliders.
        
        # Blur Brightness
        self.blur_brightness_slider, self.blur_brightness_spin = create_slider_with_input(-100, 100, 0, blur_layout, "亮度调节:")

        # Border Settings
        border_group = QGroupBox("边框设置")
        border_layout = QFormLayout()
        
        self.border_style = QComboBox()
        self.border_style.addItems(["无", "细边框", "圆角边框"])
        self.border_style.setCurrentIndex(2) # Default Rounded
        self.border_style.currentIndexChanged.connect(self.update_settings)
        
        self.border_width = QSlider(Qt.Orientation.Horizontal)
        self.border_width.setRange(0, 50)
        self.border_width.setValue(0) # Default 0
        self.border_width.valueChanged.connect(self.update_settings)
        
        # Border Color
        self.border_color_layout = QHBoxLayout()
        self.border_color_white = QRadioButton("白色")
        self.border_color_black = QRadioButton("黑色")
        self.border_color_black.setChecked(True) # Default Black
        self.border_color_white.toggled.connect(self.update_settings)
        self.border_color_black.toggled.connect(self.update_settings)
        self.border_color_group = QButtonGroup(self)
        self.border_color_group.addButton(self.border_color_white)
        self.border_color_group.addButton(self.border_color_black)
        
        self.border_color_layout.addWidget(self.border_color_white)
        self.border_color_layout.addWidget(self.border_color_black)
        
        # Corner Radius
        self.corner_radius = QSlider(Qt.Orientation.Horizontal)
        self.corner_radius.setRange(0, 100)
        self.corner_radius.setValue(20)
        self.corner_radius.valueChanged.connect(self.update_settings)
        
        # Shadow Size
        self.shadow_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.shadow_size_slider.setRange(0, 50)
        self.shadow_size_slider.setValue(20)
        self.shadow_size_slider.valueChanged.connect(self.update_settings)
        
        border_layout.addRow("样式:", self.border_style)
        border_layout.addRow("宽度:", self.border_width)
        border_layout.addRow("颜色:", self.border_color_layout)
        border_layout.addRow("圆角:", self.corner_radius)
        border_layout.addRow("阴影:", self.shadow_size_slider)
        border_group.setLayout(border_layout)
        layout.addWidget(border_group)
        
        # Export Settings
        export_group = QGroupBox("导出设置")
        export_layout = QFormLayout()
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(95)
        self.quality_slider.valueChanged.connect(self.update_settings)
        export_layout.addRow("导出质量:", self.quality_slider)
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        # Watermark Settings
        wm_group = QGroupBox("智能水印")
        wm_layout = QFormLayout()
        self.wm_enabled = QCheckBox("启用水印")
        self.wm_enabled.setChecked(True) # Default Enabled
        self.wm_enabled.stateChanged.connect(self.update_settings)
        
        self.wm_text = QLineEdit()
        self.wm_text.setPlaceholderText("留空则使用EXIF信息")
        self.wm_text.textChanged.connect(self.update_settings)
        
        self.wm_opacity = QSlider(Qt.Orientation.Horizontal)
        self.wm_opacity.setRange(0, 100)
        self.wm_opacity.setValue(100)
        self.wm_opacity.valueChanged.connect(self.update_settings)
        
        # Auto Size Checkbox
        self.wm_auto_size = QCheckBox("自动调整大小")
        self.wm_auto_size.setChecked(True)
        self.wm_auto_size.stateChanged.connect(self.update_settings)
        
        # Watermark Color
        self.wm_color_layout = QHBoxLayout()
        self.wm_color_white = QRadioButton("白色")
        self.wm_color_black = QRadioButton("黑色")
        self.wm_color_white.setChecked(True)
        self.wm_color_white.toggled.connect(self.update_settings)
        self.wm_color_black.toggled.connect(self.update_settings)
        self.wm_color_group = QButtonGroup(self)
        self.wm_color_group.addButton(self.wm_color_white)
        self.wm_color_group.addButton(self.wm_color_black)
        
        self.wm_color_layout.addWidget(self.wm_color_white)
        self.wm_color_layout.addWidget(self.wm_color_black)
        
        self.wm_position = QComboBox()
        self.wm_position.addItem("底部居中", "bottom_center")
        self.wm_position.addItem("底部居右", "bottom_right")
        self.wm_position.addItem("底部居左", "bottom_left")
        self.wm_position.addItem("顶部居中", "top_center")
        self.wm_position.addItem("顶部居右", "top_right")
        self.wm_position.addItem("顶部居左", "top_left")
        self.wm_position.addItem("居中", "center")
        self.wm_position.addItem("居中居右", "center_right")
        self.wm_position.addItem("居中居左", "center_left")
        self.set_position_mode(self.settings.watermark.position) # Fix: Init from settings
        self.wm_position.currentIndexChanged.connect(self.update_settings)
        
        # Text Mode
        self.wm_text_mode = QComboBox()
        self.wm_text_mode.addItem("追加模式 (Append)", WatermarkMode.APPEND)
        self.wm_text_mode.addItem("备用模式 (Fallback)", WatermarkMode.FALLBACK)
        self.wm_text_mode.addItem("替换模式 (Replace)", WatermarkMode.REPLACE)
        self.wm_text_mode.currentIndexChanged.connect(self.update_settings)
        
        # Font Selection
        self.font_combo = QComboBox()
        self.font_combo.addItem("Default System Font", None)
        self.load_fonts()
        

        # Try to select SMILETSANS-OBLIQUE.TTF
        idx = self.font_combo.findText("SMILETSANS-OBLIQUE.TTF", Qt.MatchFlag.MatchContains)
        if idx >= 0:
            self.font_combo.setCurrentIndex(idx)
        self.font_combo.currentIndexChanged.connect(self.update_settings)

        # Size Scale Slider (Replaces Manual Size)
        self.wm_size_scale_slider, self.wm_size_scale_spin = create_slider_with_input(50, 200, 100, wm_layout, "字体大小调整 (%):")
        self.wm_size_scale_slider.valueChanged.connect(self.update_settings)

        # Remove old manual size slider code
        # self.wm_manual_size_slider, self.wm_manual_size_spin = create_slider_with_input(10, 400, 20, wm_layout, "手动字号:")
        


        wm_layout.addRow(self.wm_enabled)

        wm_layout.addRow("字体:", self.font_combo)
        # wm_layout.addRow("样式:", style_layout) # Removed
        wm_layout.addRow("自定义文本:", self.wm_text)
        wm_layout.addRow("文本模式:", self.wm_text_mode)

        wm_layout.addRow("颜色:", self.wm_color_layout)
        # wm_layout.addRow(self.wm_auto_size) # Removed auto size checkbox, always auto + scale
        # wm_layout.addRow("大小调整:", self.wm_size_scale) # Replaced by slider with input
        wm_layout.addRow("透明度:", self.wm_opacity)
        wm_layout.addRow("位置:", self.wm_position)
        wm_group.setLayout(wm_layout)
        layout.addWidget(wm_group)

        layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def update_settings(self):
        # Update internal settings object
        self.settings.target_ratio = self.ratio_combo.currentData()
        self.settings.content_scale = self.scale_slider.value()
        self.settings.blur_radius = self.blur_slider.value()
        self.settings.blur_brightness = self.blur_brightness_slider.value()
        self.settings.blur_mode = self.blur_mode_combo.currentData()
        
        idx = self.border_style.currentIndex()
        if idx == 0:
            self.settings.border_style = BorderStyle.NONE
        elif idx == 1:
            self.settings.border_style = BorderStyle.THIN
        elif idx == 2:
            self.settings.border_style = BorderStyle.ROUNDED
            
        self.settings.border_width = self.border_width.value()
        self.settings.border_color = "white" if self.border_color_white.isChecked() else "black"
        self.settings.corner_radius = self.corner_radius.value()
        self.settings.shadow_size = self.shadow_size_slider.value()
        self.settings.export_quality = self.quality_slider.value()
            
        self.settings.watermark.enabled = self.wm_enabled.isChecked()
        self.settings.watermark.text = self.wm_text.text()
        self.settings.watermark.text_mode = self.wm_text_mode.currentData()
        self.settings.watermark.text_color = "white" if self.wm_color_white.isChecked() else "black"
        self.settings.watermark.auto_size = True # Always auto
        self.settings.watermark.opacity = self.wm_opacity.value()
        self.settings.watermark.size_scale = self.wm_size_scale_slider.value() / 100.0
        self.settings.watermark.position = self.wm_position.currentData() # Use data for internal value
        self.settings.watermark.font_path = self.font_combo.currentData()
        # Removed styles and manual size

        
        # Toggle manual size slider based on auto size - REMOVED
        # self.wm_manual_size_slider.setEnabled(not self.wm_auto_size.isChecked())
        # self.wm_manual_size_spin.setEnabled(not self.wm_auto_size.isChecked())
        
        # Debounce emission
        self.debounce_timer.start(300) # 300ms delay

    def emit_settings_changed(self):
        self.settingsChanged.emit(self.settings)

    def set_position_mode(self, mode: str):
        idx = self.wm_position.findData(mode)
        if idx >= 0:
            self.wm_position.setCurrentIndex(idx)

    def load_fonts(self):
        font_dir = get_resource_path(os.path.join("resources", "fonts"))
        print(f"SettingsPanel: Loading fonts from {font_dir}")
        
        if not os.path.exists(font_dir):
            print("SettingsPanel: Font dir not found")
            return
            
        for file in os.listdir(font_dir):
            if file.lower().endswith(('.ttf', '.otf')):
                self.font_combo.addItem(file, os.path.join(font_dir, file))





    def save_preset(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "保存预设", "", "Adaptive Glass Preset (*.agp)")
        if file_path:
            try:
                PresetManager.save_preset(self.settings, file_path)
                QMessageBox.information(self, "成功", "预设已保存")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存预设失败: {e}")

    def load_preset(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "加载预设", "", "Adaptive Glass Preset (*.agp)")
        if file_path:
            try:
                new_settings = PresetManager.load_preset(file_path)
                self.settings = new_settings
                self.apply_settings_to_ui()
                self.update_settings() # Trigger update
                QMessageBox.information(self, "成功", "预设已加载")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载预设失败: {e}")

    def apply_settings_to_ui(self):
        # Update UI elements from self.settings
        # Ratio
        idx = self.ratio_combo.findData(self.settings.target_ratio)
        if idx >= 0: self.ratio_combo.setCurrentIndex(idx)
        
        self.scale_slider.setValue(self.settings.content_scale)
        self.blur_slider.setValue(self.settings.blur_radius)
        self.blur_brightness_slider.setValue(self.settings.blur_brightness)
        
        idx = self.blur_mode_combo.findData(self.settings.blur_mode)
        if idx >= 0: self.blur_mode_combo.setCurrentIndex(idx)
        
        if self.settings.border_style == BorderStyle.NONE: self.border_style.setCurrentIndex(0)
        elif self.settings.border_style == BorderStyle.THIN: self.border_style.setCurrentIndex(1)
        elif self.settings.border_style == BorderStyle.ROUNDED: self.border_style.setCurrentIndex(2)
        
        self.border_width.setValue(self.settings.border_width)
        if self.settings.border_color == "white": self.border_color_white.setChecked(True)
        else: self.border_color_black.setChecked(True)
        
        self.corner_radius.setValue(self.settings.corner_radius)
        self.shadow_size_slider.setValue(self.settings.shadow_size)
        self.quality_slider.setValue(self.settings.export_quality)
        
        # Watermark
        wm = self.settings.watermark
        self.wm_enabled.setChecked(wm.enabled)
        self.wm_text.setText(wm.text)
        
        idx = self.wm_text_mode.findData(wm.text_mode)
        if idx >= 0: self.wm_text_mode.setCurrentIndex(idx)
        
        if wm.text_color == "white": self.wm_color_white.setChecked(True)
        else: self.wm_color_black.setChecked(True)
        
        # self.wm_auto_size.setChecked(wm.auto_size) # Removed
        self.wm_opacity.setValue(wm.opacity)
        self.wm_size_scale_slider.setValue(int(wm.size_scale * 100))
        self.set_position_mode(wm.position)
        
        idx = self.font_combo.findData(wm.font_path)
        if idx >= 0: self.font_combo.setCurrentIndex(idx)
        
        # Removed styles and manual size

        

