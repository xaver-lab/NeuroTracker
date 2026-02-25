"""
Main Window for Neuro-Tracker Application
The primary application window containing all main components
"""

from datetime import date
from typing import Optional

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QMenuBar, QMenu, QAction, QStatusBar, QMessageBox,
    QFileDialog, QLabel, QFrame, QSplitter, QScrollArea,
    QDialog, QCheckBox, QPushButton, QDialogButtonBox,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon

from config import (
    WINDOW_TITLE, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    COLOR_PRIMARY, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    GOOGLE_DRIVE_ENABLED, SYNC_INTERVAL_MINUTES,
    SEVERITY_COLORS, STRESS_COLORS, SLEEP_COLORS, NICKEL_RICH_FOODS,
)
from models.data_manager import DataManager
from models.food_manager import FoodManager
from models.settings_manager import SettingsManager
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
        self.settings_manager = SettingsManager()
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

            # Initial sync on startup (delayed to allow UI to load)
            QTimer.singleShot(1000, self.startup_sync)

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

        # Settings menu
        settings_menu = menubar.addMenu("Einstellungen")

        modules_action = QAction("Tracker-Module aktivieren...", self)
        modules_action.triggered.connect(self.show_module_settings)
        settings_menu.addAction(modules_action)

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
        """Setup the main content area with top (entry+calendar) and bottom (detail)."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        outer_layout = QVBoxLayout(central_widget)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # ── Vertical splitter: top area / bottom detail ────────────────────────
        self.v_splitter = QSplitter(Qt.Vertical)
        self.v_splitter.setHandleWidth(4)
        self.v_splitter.setStyleSheet("""
            QSplitter::handle { background-color: #E0E0E0; }
            QSplitter::handle:hover { background-color: #BDBDBD; }
        """)

        # ── TOP: horizontal splitter (entry panel | calendar) ──────────────────
        self.h_splitter = QSplitter(Qt.Horizontal)
        self.h_splitter.setHandleWidth(4)
        self.h_splitter.setStyleSheet("""
            QSplitter::handle { background-color: #E0E0E0; }
            QSplitter::handle:hover { background-color: #BDBDBD; }
        """)

        # Entry panel (left)
        self.entry_panel = EntryPanel(self.data_manager, self.food_manager, self.settings_manager)
        self.entry_panel.entry_saved.connect(self.on_entry_saved)
        self.entry_panel.entry_deleted.connect(self.on_entry_deleted)
        self.entry_panel.setMinimumWidth(320)
        self.entry_panel.setMaximumWidth(500)

        panel_frame = QFrame()
        panel_frame.setStyleSheet("""
            QFrame { background-color: white; border-right: 1px solid #E0E0E0; }
        """)
        panel_layout = QVBoxLayout(panel_frame)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(self.entry_panel)

        # Calendar (right)
        self.calendar_widget = CalendarWidget(self.data_manager)
        self.calendar_widget.date_selected.connect(self.on_date_selected)

        self.h_splitter.addWidget(panel_frame)
        self.h_splitter.addWidget(self.calendar_widget)
        self.h_splitter.setStretchFactor(0, 0)
        self.h_splitter.setStretchFactor(1, 1)
        self.h_splitter.setSizes([370, 830])

        # ── BOTTOM: detail panel ───────────────────────────────────────────────
        self.detail_panel = self._build_detail_panel()
        self.detail_panel.setMinimumHeight(0)

        self.v_splitter.addWidget(self.h_splitter)
        self.v_splitter.addWidget(self.detail_panel)
        self.v_splitter.setStretchFactor(0, 1)
        self.v_splitter.setStretchFactor(1, 0)
        self.v_splitter.setSizes([600, 200])

        outer_layout.addWidget(self.v_splitter)

    def _build_detail_panel(self) -> QFrame:
        """Build the bottom detail panel that shows all info for the selected day."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame { background-color: white; border-top: 2px solid #E0E0E0; }
        """)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(8)

        # Header
        self.detail_header = QLabel("Kein Tag ausgewählt")
        self.detail_header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.detail_header.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; border: none;")
        layout.addWidget(self.detail_header)

        # Content: horizontal scroll with columns
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        content = QWidget()
        self.detail_content = QHBoxLayout(content)
        self.detail_content.setContentsMargins(0, 0, 0, 0)
        self.detail_content.setSpacing(20)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        return frame

    def _update_detail_panel(self, selected_date):
        """Fill the bottom detail panel with data from the selected entry."""
        weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        months = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]

        self.detail_header.setText(
            f"{weekdays[selected_date.weekday()]}, {selected_date.day}. "
            f"{months[selected_date.month - 1]} {selected_date.year}"
        )

        # Clear existing content
        while self.detail_content.count():
            item = self.detail_content.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        entry = self.data_manager.get_entry(selected_date)
        if not entry:
            lbl = QLabel("Noch kein Eintrag für diesen Tag")
            lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-style: italic; border: none;")
            self.detail_content.addWidget(lbl)
            self.detail_content.addStretch()
            return

        # ── Column: Hautzustand ─────────────────────────────────────────────
        col = self._detail_column("Hautzustand")
        sev = entry.severity or 0
        color = SEVERITY_COLORS.get(sev, "#9E9E9E")
        sev_texts = {1: "Sehr gut", 2: "Gut", 3: "Mittel", 4: "Schlecht", 5: "Sehr schlecht"}
        sev_lbl = QLabel(f"  {sev} — {sev_texts.get(sev, '')}")
        sev_lbl.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 14px; border: none;")
        col.layout().addWidget(sev_lbl)
        if entry.skin_notes:
            n = QLabel(entry.skin_notes)
            n.setWordWrap(True)
            n.setMaximumWidth(200)
            n.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px; border: none;")
            col.layout().addWidget(n)
        col.layout().addStretch()
        self.detail_content.addWidget(col)

        # ── Column: Lebensmittel ────────────────────────────────────────────
        if entry.foods:
            col = self._detail_column("Lebensmittel")
            foods_text = ", ".join(entry.foods)
            f_lbl = QLabel(foods_text)
            f_lbl.setWordWrap(True)
            f_lbl.setMaximumWidth(250)
            f_lbl.setStyleSheet(f"font-size: 12px; border: none;")
            col.layout().addWidget(f_lbl)
            # Count nickel-rich
            nickel = [f for f in entry.foods if f in NICKEL_RICH_FOODS]
            if nickel:
                ni_lbl = QLabel(f"[Ni] {', '.join(nickel)}")
                ni_lbl.setStyleSheet("color: #E65100; font-size: 11px; border: none;")
                ni_lbl.setWordWrap(True)
                ni_lbl.setMaximumWidth(250)
                col.layout().addWidget(ni_lbl)
            if entry.food_notes:
                fn = QLabel(entry.food_notes)
                fn.setWordWrap(True)
                fn.setMaximumWidth(200)
                fn.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px; border: none;")
                col.layout().addWidget(fn)
            col.layout().addStretch()
            self.detail_content.addWidget(col)

        # ── Column: Trigger ─────────────────────────────────────────────────
        triggers = []
        if entry.stress_level is not None:
            sc = STRESS_COLORS.get(entry.stress_level, "#9E9E9E")
            triggers.append(f"<span style='color:{sc}'>😰 Stress: {entry.stress_level}/5</span>")
        if entry.fungal_active:
            triggers.append("<span style='color:#FF9800'>🍄 Zehenpilz aktiv</span>")
        if entry.sleep_quality is not None:
            slc = SLEEP_COLORS.get(entry.sleep_quality, "#9E9E9E")
            triggers.append(f"<span style='color:{slc}'>😴 Schlaf: {entry.sleep_quality}/5</span>")
        if entry.weather:
            triggers.append(f"🌤 {entry.weather}")
        if entry.sweating:
            triggers.append("💧 Starkes Schwitzen")
        if entry.contact_exposures:
            triggers.append(f"🧤 {', '.join(entry.contact_exposures)}")

        if triggers:
            col = self._detail_column("Trigger")
            for t in triggers:
                lbl = QLabel(t)
                lbl.setTextFormat(Qt.RichText)
                lbl.setStyleSheet("font-size: 12px; border: none;")
                col.layout().addWidget(lbl)
            col.layout().addStretch()
            self.detail_content.addWidget(col)

        self.detail_content.addStretch()

    def _detail_column(self, title: str) -> QFrame:
        """Create a titled column for the detail panel."""
        frame = QFrame()
        frame.setMinimumWidth(150)
        frame.setStyleSheet("""
            QFrame {
                background-color: #FAFAFA;
                border: 1px solid #E8E8E8;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        header = QLabel(title)
        header.setFont(QFont("Segoe UI", 11, QFont.Bold))
        header.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; border: none;")
        layout.addWidget(header)
        return frame

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
        self._update_detail_panel(selected_date)
        self.statusBar.showMessage(f"Datum ausgewählt: {selected_date.strftime('%d.%m.%Y')}", 3000)

    def on_entry_saved(self, saved_date: date):
        """Handle entry save"""
        self.calendar_widget.refresh_date(saved_date)
        self._update_detail_panel(saved_date)
        self.update_entry_count()
        self.statusBar.showMessage("Eintrag gespeichert", 3000)

    def on_entry_deleted(self, deleted_date: date):
        """Handle entry deletion"""
        self.calendar_widget.refresh_date(deleted_date)
        self._update_detail_panel(deleted_date)
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

    def startup_sync(self):
        """Sync on application startup"""
        if GOOGLE_DRIVE_ENABLED and self.drive_sync.is_connected():
            self.statusBar.showMessage("Synchronisiere...", 0)
            success, _ = self.drive_sync.sync()
            if success:
                self.calendar_widget.refresh_all()
                self.update_entry_count()
                self.statusBar.showMessage("Startup-Sync erfolgreich", 3000)
            else:
                self.statusBar.showMessage("Startup-Sync fehlgeschlagen", 3000)
            self.update_sync_status()

    def show_sync_status(self):
        """Show sync status dialog"""
        status = self.drive_sync.get_status()

        if status['connected']:
            last_sync = status['last_sync'] or "Nie"
            msg = (
                f"Google Drive Status: Verbunden ✓\n\n"
                f"Ordner: {status['folder']}\n"
                f"Letzter Sync: {last_sync}\n"
                f"Auto-Sync: alle {SYNC_INTERVAL_MINUTES} Minuten"
            )
        else:
            # Show diagnostic info when not connected
            api_status = "✓ Installiert" if status.get('api_available', False) else "✗ Nicht installiert"
            cred_status = "✓ Vorhanden" if status.get('credentials_exist', False) else "✗ Fehlt"

            msg = (
                f"Google Drive Status: Nicht verbunden\n\n"
                f"Google API: {api_status}\n"
                f"Credentials: {cred_status}\n\n"
                f"Verwende 'Google Drive verbinden...' um die Verbindung herzustellen."
            )

        QMessageBox.information(self, "Synchronisations-Status", msg)

    def connect_google_drive(self):
        """Connect to Google Drive"""
        if self.drive_sync.is_connected():
            # Already connected - offer to disconnect
            reply = QMessageBox.question(
                self, "Google Drive",
                "Du bist bereits mit Google Drive verbunden.\n\n"
                "Möchtest du die Verbindung trennen?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                success, message = self.drive_sync.disconnect()
                self.update_sync_status()
                QMessageBox.information(self, "Google Drive", message)
        else:
            # Not connected - start OAuth flow
            reply = QMessageBox.question(
                self, "Google Drive verbinden",
                "Möchtest du dich mit Google Drive verbinden?\n\n"
                "Es öffnet sich ein Browser-Fenster zur Anmeldung.\n"
                "Nach der Verbindung werden deine Daten automatisch synchronisiert.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if reply == QMessageBox.Yes:
                self.statusBar.showMessage("Verbinde mit Google Drive...", 0)
                success, message = self.drive_sync.connect()
                self.update_sync_status()

                if success:
                    QMessageBox.information(self, "Google Drive", message)
                    # Initial sync after connecting
                    self.manual_sync()
                else:
                    QMessageBox.warning(self, "Google Drive Fehler", message)

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

    def show_module_settings(self):
        """Open dialog for enabling/disabling tracker modules."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Tracker-Module")
        dialog.setMinimumWidth(380)
        dialog.setStyleSheet("QDialog { background-color: #FAFAFA; }")

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(24, 24, 24, 16)
        layout.setSpacing(16)

        title = QLabel("Welche Trigger möchtest du erfassen?")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #212121;")
        title.setWordWrap(True)
        layout.addWidget(title)

        hint = QLabel(
            "Aktivierte Module erscheinen im Eingabe-Panel (links). "
            "Du kannst sie jederzeit ein- oder ausschalten."
        )
        hint.setStyleSheet("color: #757575; font-size: 12px;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        from config import TRACKER_MODULES
        checkboxes = {}
        for key, info in TRACKER_MODULES.items():
            cb = QCheckBox(f"{info['icon']}  {info['label']}")
            cb.setChecked(self.settings_manager.is_module_enabled(key))
            cb.setStyleSheet("QCheckBox { font-size: 13px; padding: 4px 0; }")
            layout.addWidget(cb)
            checkboxes[key] = cb

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(dialog.accept)
        btns.rejected.connect(dialog.reject)
        layout.addWidget(btns)

        if dialog.exec_() == QDialog.Accepted:
            for key, cb in checkboxes.items():
                self.settings_manager.set_module_enabled(key, cb.isChecked())
            # Rebuild entry panel trigger sections
            self.entry_panel.rebuild_trigger_sections()
            self.statusBar.showMessage("Einstellungen gespeichert", 2000)

    def closeEvent(self, event):
        """Handle window close"""
        # Save any pending changes
        self.data_manager.save()
        self.food_manager.save()

        # Sync to Google Drive before closing
        if GOOGLE_DRIVE_ENABLED and self.drive_sync.is_connected():
            self.statusBar.showMessage("Synchronisiere vor dem Beenden...", 0)
            self.drive_sync.sync()

        event.accept()
