"""
Main Window for Neuro-Tracker Application
The primary application window containing all main components
"""

from datetime import date
from typing import Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QMenuBar, QMenu, QAction, QStatusBar, QMessageBox,
    QFileDialog, QLabel, QFrame, QSplitter
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon

from config import (
    WINDOW_TITLE, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    COLOR_PRIMARY, COLOR_TEXT_SECONDARY, GOOGLE_DRIVE_ENABLED,
    SYNC_INTERVAL_MINUTES
)
from models.data_manager import DataManager
from models.food_manager import FoodManager
from ui.styles import get_main_stylesheet
from ui.calendar_widget import CalendarWidget
from ui.entry_panel import EntryPanel
from ui.statistics_dialog import StatisticsDialog
from utils.google_drive import GoogleDriveSync
from utils.export import ExportManager


class MainWindow(QMainWindow):
    """
    Main application window.
    Contains the calendar view and entry panel.
    """

    def __init__(self):
        super().__init__()

        # Initialize managers
        self.data_manager = DataManager()
        self.food_manager = FoodManager()
        self.drive_sync = GoogleDriveSync(self.data_manager)
        self.export_manager = ExportManager(self.data_manager)

        # Setup UI
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.setStyleSheet(get_main_stylesheet())

        self.setup_menu_bar()
        self.setup_central_widget()
        self.setup_status_bar()

        # Auto-sync timer
        if GOOGLE_DRIVE_ENABLED:
            self.sync_timer = QTimer(self)
            self.sync_timer.timeout.connect(self.auto_sync)
            self.sync_timer.start(SYNC_INTERVAL_MINUTES * 60 * 1000)

        # Select today by default
        self.calendar_widget.go_today()

    def setup_menu_bar(self):
        """Setup the menu bar"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: white;
                border-bottom: 1px solid #E0E0E0;
                padding: 4px;
            }
            QMenuBar::item {
                padding: 8px 16px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #E3F2FD;
            }
            QMenu {
                background-color: white;
                border: 1px solid #E0E0E0;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #E3F2FD;
            }
            QMenu::separator {
                height: 1px;
                background-color: #E0E0E0;
                margin: 4px 8px;
            }
        """)

        # File menu
        file_menu = menubar.addMenu("Datei")

        export_csv_action = QAction("Als CSV exportieren...", self)
        export_csv_action.setShortcut("Ctrl+E")
        export_csv_action.triggered.connect(self.export_csv)
        file_menu.addAction(export_csv_action)

        export_pdf_action = QAction("Als PDF exportieren...", self)
        export_pdf_action.setShortcut("Ctrl+P")
        export_pdf_action.triggered.connect(self.export_pdf)
        file_menu.addAction(export_pdf_action)

        file_menu.addSeparator()

        import_action = QAction("Daten importieren...", self)
        import_action.triggered.connect(self.import_data)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        exit_action = QAction("Beenden", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("Ansicht")

        today_action = QAction("Zu heute springen", self)
        today_action.setShortcut("Ctrl+T")
        today_action.triggered.connect(self.go_today)
        view_menu.addAction(today_action)

        view_menu.addSeparator()

        stats_action = QAction("Statistiken anzeigen...", self)
        stats_action.setShortcut("Ctrl+S")
        stats_action.triggered.connect(self.show_statistics)
        view_menu.addAction(stats_action)

        # Sync menu
        sync_menu = menubar.addMenu("Synchronisation")

        sync_now_action = QAction("Jetzt synchronisieren", self)
        sync_now_action.setShortcut("Ctrl+R")
        sync_now_action.triggered.connect(self.manual_sync)
        sync_menu.addAction(sync_now_action)

        sync_status_action = QAction("Sync-Status anzeigen", self)
        sync_status_action.triggered.connect(self.show_sync_status)
        sync_menu.addAction(sync_status_action)

        sync_menu.addSeparator()

        connect_drive_action = QAction("Google Drive verbinden...", self)
        connect_drive_action.triggered.connect(self.connect_google_drive)
        sync_menu.addAction(connect_drive_action)

        # Help menu
        help_menu = menubar.addMenu("Hilfe")

        about_action = QAction("Über Neuro-Tracker", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        help_action = QAction("Hilfe", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

    def setup_central_widget(self):
        """Setup the main content area"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Entry panel (left side)
        self.entry_panel = EntryPanel(self.data_manager, self.food_manager)
        self.entry_panel.entry_saved.connect(self.on_entry_saved)
        self.entry_panel.entry_deleted.connect(self.on_entry_deleted)

        # Add left border frame
        panel_frame = QFrame()
        panel_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-right: 1px solid #E0E0E0;
            }
        """)
        panel_layout = QVBoxLayout(panel_frame)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(self.entry_panel)

        # Calendar widget (right side)
        self.calendar_widget = CalendarWidget(self.data_manager)
        self.calendar_widget.date_selected.connect(self.on_date_selected)

        # Use splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(panel_frame)
        splitter.addWidget(self.calendar_widget)
        splitter.setStretchFactor(0, 0)  # Entry panel doesn't stretch
        splitter.setStretchFactor(1, 1)  # Calendar stretches
        splitter.setSizes([350, 850])
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #E0E0E0;
            }
        """)

        main_layout.addWidget(splitter)

    def setup_status_bar(self):
        """Setup the status bar"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.statusBar.setStyleSheet("""
            QStatusBar {
                background-color: white;
                border-top: 1px solid #E0E0E0;
                padding: 4px;
            }
        """)

        # Sync status indicator
        self.sync_status_label = QLabel()
        self.update_sync_status()
        self.statusBar.addPermanentWidget(self.sync_status_label)

        # Entry count
        self.entry_count_label = QLabel()
        self.update_entry_count()
        self.statusBar.addPermanentWidget(self.entry_count_label)

    def on_date_selected(self, selected_date: date):
        """Handle date selection from calendar"""
        self.entry_panel.set_date(selected_date)
        self.statusBar.showMessage(f"Datum ausgewählt: {selected_date.strftime('%d.%m.%Y')}", 3000)

    def on_entry_saved(self, saved_date: date):
        """Handle entry save"""
        self.calendar_widget.refresh_date(saved_date)
        self.update_entry_count()
        self.statusBar.showMessage("Eintrag gespeichert", 3000)

    def on_entry_deleted(self, deleted_date: date):
        """Handle entry deletion"""
        self.calendar_widget.refresh_date(deleted_date)
        self.update_entry_count()
        self.statusBar.showMessage("Eintrag gelöscht", 3000)

    def go_today(self):
        """Navigate to today"""
        self.calendar_widget.go_today()

    def show_statistics(self):
        """Show the statistics dialog"""
        dialog = StatisticsDialog(self.data_manager, self)
        dialog.exec_()

    def export_csv(self):
        """Export data to CSV"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "CSV exportieren",
            f"neuro_tracker_export_{date.today().isoformat()}.csv",
            "CSV Dateien (*.csv)"
        )
        if filename:
            success, message = self.export_manager.export_csv(filename)
            if success:
                QMessageBox.information(self, "Export erfolgreich", message)
            else:
                QMessageBox.warning(self, "Export fehlgeschlagen", message)

    def export_pdf(self):
        """Export data to PDF"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "PDF exportieren",
            f"neuro_tracker_report_{date.today().isoformat()}.pdf",
            "PDF Dateien (*.pdf)"
        )
        if filename:
            success, message = self.export_manager.export_pdf(filename)
            if success:
                QMessageBox.information(self, "Export erfolgreich", message)
            else:
                QMessageBox.warning(self, "Export fehlgeschlagen", message)

    def import_data(self):
        """Import data from CSV"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Daten importieren",
            "",
            "CSV Dateien (*.csv);;JSON Dateien (*.json)"
        )
        if filename:
            success, message = self.export_manager.import_data(filename)
            if success:
                self.calendar_widget.refresh_all()
                self.update_entry_count()
                QMessageBox.information(self, "Import erfolgreich", message)
            else:
                QMessageBox.warning(self, "Import fehlgeschlagen", message)

    def manual_sync(self):
        """Manually trigger sync"""
        self.statusBar.showMessage("Synchronisiere...", 0)
        success, message = self.drive_sync.sync()
        self.update_sync_status()

        if success:
            self.calendar_widget.refresh_all()
            self.update_entry_count()
            self.statusBar.showMessage("Synchronisation erfolgreich", 3000)
        else:
            self.statusBar.showMessage(f"Sync-Fehler: {message}", 5000)

    def auto_sync(self):
        """Auto-sync triggered by timer"""
        if GOOGLE_DRIVE_ENABLED:
            success, _ = self.drive_sync.sync()
            if success:
                self.calendar_widget.refresh_all()
            self.update_sync_status()

    def show_sync_status(self):
        """Show sync status dialog"""
        status = self.drive_sync.get_status()

        if status['connected']:
            last_sync = status['last_sync'] or "Nie"
            msg = f"Google Drive Status: Verbunden\n\nLetzter Sync: {last_sync}\nNächster Sync: in {SYNC_INTERVAL_MINUTES} Minuten"
        else:
            msg = "Google Drive Status: Nicht verbunden\n\nVerbinde Google Drive um deine Daten automatisch zu sichern."

        QMessageBox.information(self, "Synchronisations-Status", msg)

    def connect_google_drive(self):
        """Connect to Google Drive"""
        result = QMessageBox.information(
            self, "Google Drive verbinden",
            "Diese Funktion wird später implementiert.\n\n"
            "Nach der Verbindung werden deine Daten automatisch mit Google Drive synchronisiert.",
            QMessageBox.Ok
        )

    def update_sync_status(self):
        """Update the sync status indicator"""
        status = self.drive_sync.get_status()

        if status['connected']:
            self.sync_status_label.setText("🔗 Sync aktiv")
            self.sync_status_label.setStyleSheet(f"color: #4CAF50; padding: 0 10px;")
        else:
            self.sync_status_label.setText("⚡ Lokal")
            self.sync_status_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; padding: 0 10px;")

    def update_entry_count(self):
        """Update the entry count in status bar"""
        stats = self.data_manager.get_statistics()
        count = stats.get('total_entries', 0)
        self.entry_count_label.setText(f"📊 {count} Einträge")
        self.entry_count_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; padding: 0 10px;")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "Über Neuro-Tracker",
            "<h2>Neuro-Tracker</h2>"
            "<p>Version 1.0.0</p>"
            "<p>Eine Anwendung zur Verfolgung von Neurodermitis-Symptomen "
            "und Identifizierung möglicher Nahrungsmittel-Trigger.</p>"
            "<p>Dokumentiere täglich deinen Hautzustand und deine Ernährung, "
            "um Zusammenhänge zu erkennen.</p>"
            "<hr>"
            "<p><small>Entwickelt mit PyQt5</small></p>"
        )

    def show_help(self):
        """Show help dialog"""
        QMessageBox.information(
            self, "Hilfe",
            "<h3>Neuro-Tracker Hilfe</h3>"
            "<p><b>Tageseintrag erstellen:</b></p>"
            "<ol>"
            "<li>Klicke auf einen Tag im Kalender</li>"
            "<li>Wähle deinen Hautzustand (1-5)</li>"
            "<li>Füge die gegessenen Lebensmittel hinzu</li>"
            "<li>Optional: Notizen hinzufügen</li>"
            "<li>Klicke auf 'Speichern'</li>"
            "</ol>"
            "<p><b>Statistiken:</b></p>"
            "<p>Über Ansicht → Statistiken kannst du Zusammenhänge "
            "zwischen Lebensmitteln und deinem Hautzustand analysieren.</p>"
            "<p><b>Tastaturkürzel:</b></p>"
            "<ul>"
            "<li>Strg+T: Zu heute springen</li>"
            "<li>Strg+S: Statistiken</li>"
            "<li>Strg+E: CSV exportieren</li>"
            "<li>Strg+P: PDF exportieren</li>"
            "</ul>"
        )

    def closeEvent(self, event):
        """Handle window close"""
        # Save any pending changes
        self.data_manager.save()
        self.food_manager.save()
        event.accept()
