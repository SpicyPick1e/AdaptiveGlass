import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.ui.main_window import MainWindow
from src.core.utils import get_resource_path

def main():
    print("Creating QApplication...")
    app = QApplication(sys.argv)
    
    # Set application icon
    icon_path = get_resource_path("resources/logos/applogo.png")
    app.setWindowIcon(QIcon(icon_path))
    
    print("Creating MainWindow...")
    window = MainWindow()
    print("Showing MainWindow...")
    window.show()
    print("Starting Event Loop...")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
