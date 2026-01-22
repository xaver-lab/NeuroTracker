"""
Neuro-Tracker - Eczema and Food Tracking Application
Main entry point for the application
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

import config
from models.data_manager import DataManager
from models.food_manager import FoodManager


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.food_manager = FoodManager()

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(config.WINDOW_TITLE)
        self.setMinimumSize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Temporary welcome message
        welcome_label = QLabel("🩺 Willkommen zu Neuro-Tracker!")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: bold;
                color: {config.COLOR_PRIMARY};
                padding: 50px;
            }}
        """)
        layout.addWidget(welcome_label)

        info_label = QLabel(
            "Die Benutzeroberfläche wird gerade entwickelt.\n\n"
            "Bald verfügbar:\n"
            "• Kalenderansicht mit 2 Wochen\n"
            "• Eingabe-Panel für Schweregrad und Lebensmittel\n"
            "• Bearbeiten bestehender Einträge\n"
            "• Statistiken und Charts\n"
            "• Google Drive Synchronisation"
        )
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                color: {config.COLOR_TEXT_SECONDARY};
                line-height: 1.8;
            }}
        """)
        layout.addWidget(info_label)

        # Load statistics
        stats = self.data_manager.get_statistics()
        stats_text = (
            f"\n\n📊 Aktuelle Statistiken:\n"
            f"Einträge gesamt: {stats['total_entries']}\n"
            f"Einzigartige Lebensmittel: {stats['unique_foods']}\n"
        )
        if stats['total_entries'] > 0:
            stats_text += f"Durchschnittlicher Schweregrad: {stats['avg_severity']:.1f}"

        stats_label = QLabel(stats_text)
        stats_label.setAlignment(Qt.AlignCenter)
        stats_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {config.COLOR_TEXT_PRIMARY};
                padding: 20px;
            }}
        """)
        layout.addWidget(stats_label)

        # Center the window
        self.center_on_screen()

    def center_on_screen(self):
        """Center the window on the screen"""
        screen = QApplication.primaryScreen().geometry()
        window = self.frameGeometry()
        window.moveCenter(screen.center())
        self.move(window.topLeft())


def main():
    """Main application entry point"""
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setApplicationVersion(config.APP_VERSION)

    # Set application style
    app.setStyle('Fusion')

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
