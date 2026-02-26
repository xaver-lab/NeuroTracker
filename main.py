"""
Neuro-Tracker - Eczema and Food Tracking Application
Main entry point for the application
"""
import sys
import os

# Add src/ to path so packages (config, ui, models, utils) are found
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

import config
from ui.main_window import MainWindow


def main():
    """Main application entry point"""
    # Enable High DPI scaling (deprecated in Qt 6, but needed for Qt 5)
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # type: ignore
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  # type: ignore

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setApplicationVersion(config.APP_VERSION)

    # Set application style
    app.setStyle('Fusion')

    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
