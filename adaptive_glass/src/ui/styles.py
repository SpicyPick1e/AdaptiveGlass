# Modern Dark Theme QSS

DARK_THEME = """
QMainWindow {
    background-color: #2b2b2b;
    color: #ffffff;
}

QWidget {
    background-color: #2b2b2b;
    color: #e0e0e0;
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: 14px;
}

/* GroupBox */
QGroupBox {
    border: 1px solid #3c3f41;
    border-radius: 6px;
    margin-top: 24px;
    padding-top: 10px;
    font-weight: bold;
    color: #a0a0a0;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    left: 10px;
    color: #ffffff;
}

/* Buttons */
QPushButton {
    background-color: #0d6efd;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
    min-height: 24px;
}

QPushButton:hover {
    background-color: #0b5ed7;
}

QPushButton:pressed {
    background-color: #0a58ca;
}

QPushButton:disabled {
    background-color: #444;
    color: #888;
}

/* ComboBox */
QComboBox {
    background-color: #3c3f41;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 4px;
    color: #ffffff;
}

QComboBox:hover {
    border: 1px solid #0d6efd;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left-width: 0px;
    border-top-right-radius: 3px;
    border-bottom-right-radius: 3px;
}

/* Slider */
QSlider {
    min-height: 24px;
}

QSlider::groove:horizontal {
    border: 1px solid #3c3f41;
    height: 6px;
    background: #3c3f41;
    margin: 0px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #0d6efd;
    border: 1px solid #0d6efd;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #0b5ed7;
}

/* LineEdit */
QLineEdit {
    background-color: #3c3f41;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 4px;
    color: #ffffff;
}

QLineEdit:focus {
    border: 1px solid #0d6efd;
}

/* CheckBox & RadioButton */
QCheckBox, QRadioButton {
    spacing: 8px;
}

/* CheckBox Specific */
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #555;
    background-color: #3c3f41;
}

QCheckBox::indicator:checked {
    background-color: #0d6efd;
    border: 1px solid #0d6efd;
    /* Note: Without an icon image, this will be a solid blue square. 
       This is still much clearer than a gray box. */
}

QCheckBox::indicator:unchecked:hover {
    border: 1px solid #0d6efd;
}

/* RadioButton Specific */
QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 1px solid #555;
    background-color: #3c3f41;
}

QRadioButton::indicator:checked {
    background-color: #0d6efd;
    border: 2px solid #ffffff;
}

QRadioButton::indicator:unchecked:hover {
    border: 1px solid #0d6efd;
}

/* Splitter */
QSplitter::handle {
    background-color: #3c3f41;
}

/* StatusBar */
QStatusBar {
    background-color: #1e1e1e;
    color: #888;
}

/* ToolBar */
QToolBar {
    background-color: #1e1e1e;
    border-bottom: 1px solid #3c3f41;
    spacing: 10px;
    padding: 5px;
}

QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 4px;
}

QToolButton:hover {
    background-color: #3c3f41;
    border: 1px solid #555;
}
"""

LIGHT_THEME = """
QMainWindow {
    background-color: #f0f2f5;
    color: #212529;
}

QWidget {
    background-color: #f0f2f5;
    color: #212529;
    font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
    font-size: 14px;
}

/* GroupBox */
QGroupBox {
    border: 1px solid #dee2e6;
    border-radius: 6px;
    margin-top: 24px;
    padding-top: 10px;
    font-weight: bold;
    color: #495057;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    left: 10px;
    color: #212529;
}

/* Buttons */
QPushButton {
    background-color: #0d6efd;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
    min-height: 24px;
}

QPushButton:hover {
    background-color: #0b5ed7;
}

QPushButton:pressed {
    background-color: #0a58ca;
}

QPushButton:disabled {
    background-color: #e9ecef;
    color: #adb5bd;
}

/* ComboBox */
QComboBox {
    background-color: #ffffff;
    border: 1px solid #ced4da;
    border-radius: 4px;
    padding: 4px;
    color: #212529;
}

QComboBox:hover {
    border: 1px solid #0d6efd;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left-width: 0px;
    border-top-right-radius: 3px;
    border-bottom-right-radius: 3px;
}

/* Slider */
QSlider {
    min-height: 24px;
}

QSlider::groove:horizontal {
    border: 1px solid #dee2e6;
    height: 6px;
    background: #e9ecef;
    margin: 0px;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #0d6efd;
    border: 1px solid #0d6efd;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #0b5ed7;
}

/* LineEdit */
QLineEdit {
    background-color: #ffffff;
    border: 1px solid #ced4da;
    border-radius: 4px;
    padding: 4px;
    color: #212529;
}

QLineEdit:focus {
    border: 1px solid #0d6efd;
}

/* CheckBox & RadioButton */
QCheckBox, QRadioButton {
    spacing: 8px;
}

/* CheckBox Specific */
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #ced4da;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #0d6efd;
    border: 1px solid #0d6efd;
}

QCheckBox::indicator:unchecked:hover {
    border: 1px solid #0d6efd;
}

/* RadioButton Specific */
QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 1px solid #ced4da;
    background-color: #ffffff;
}

QRadioButton::indicator:checked {
    background-color: #0d6efd;
    border: 2px solid #ffffff;
}

QRadioButton::indicator:unchecked:hover {
    border: 1px solid #0d6efd;
}

/* Splitter */
QSplitter::handle {
    background-color: #dee2e6;
}

/* StatusBar */
QStatusBar {
    background-color: #e9ecef;
    color: #495057;
}

/* ToolBar */
QToolBar {
    background-color: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
    spacing: 10px;
    padding: 5px;
}

QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 4px;
    color: #212529;
}

QToolButton:hover {
    background-color: #e9ecef;
    border: 1px solid #ced4da;
}
"""
