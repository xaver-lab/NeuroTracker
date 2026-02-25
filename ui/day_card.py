"""
Day Card Widget for Neuro-Tracker Application
Displays a single day's entry in the calendar view with trigger indicators.
"""

from datetime import date
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QCursor

from config import SEVERITY_COLORS, COLOR_TEXT_SECONDARY, COLOR_PRIMARY, FOOD_EMOJIS
from models.day_entry import DayEntry


class DayCard(QFrame):
    """
    A card widget representing a single day in the calendar.
    Shows date, severity indicator, foods, trigger icons and notes preview.
    """

    clicked = pyqtSignal(date)

    def __init__(self, display_date: date, entry: DayEntry = None, parent=None):
        super().__init__(parent)
        self.display_date = display_date
        self.entry = entry
        self._is_selected = False
        self._is_today = display_date == date.today()

        self.setup_ui()
        self.update_style()

    def setup_ui(self):
        self.setFixedSize(160, 150)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setObjectName("dayCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        # Header: day name + date number
        header = QHBoxLayout()
        day_names = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        self.day_label = QLabel(day_names[self.display_date.weekday()])
        self.day_label.setFont(QFont("Segoe UI", 10, QFont.Bold))

        self.date_label = QLabel(str(self.display_date.day))
        self.date_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.date_label.setAlignment(Qt.AlignRight)

        header.addWidget(self.day_label)
        header.addStretch()
        header.addWidget(self.date_label)
        layout.addLayout(header)

        # Month indicator (only if not current month)
        if self.display_date.month != date.today().month:
            month_names = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun",
                          "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
            month_lbl = QLabel(month_names[self.display_date.month - 1])
            month_lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
            month_lbl.setAlignment(Qt.AlignRight)
            layout.addWidget(month_lbl)

        layout.addStretch()

        # Severity indicator
        sev_widget = QWidget()
        sev_layout = QHBoxLayout(sev_widget)
        sev_layout.setContentsMargins(0, 0, 0, 0)
        sev_layout.setSpacing(4)

        self.severity_indicator = QLabel()
        self.severity_indicator.setFixedSize(24, 24)
        self.severity_indicator.setAlignment(Qt.AlignCenter)
        self.severity_indicator.setFont(QFont("Segoe UI", 11, QFont.Bold))

        self.severity_text = QLabel()
        self.severity_text.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")

        sev_layout.addWidget(self.severity_indicator)
        sev_layout.addWidget(self.severity_text)
        sev_layout.addStretch()
        layout.addWidget(sev_widget)

        # Trigger icons row
        self.trigger_label = QLabel()
        self.trigger_label.setStyleSheet("font-size: 13px; padding: 0;")
        layout.addWidget(self.trigger_label)

        # Food emojis
        self.food_label = QLabel()
        self.food_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
        layout.addWidget(self.food_label)

        # Notes preview
        self.notes_preview = QLabel()
        self.notes_preview.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 10px;")
        self.notes_preview.setWordWrap(True)
        self.notes_preview.setMaximumHeight(30)
        layout.addWidget(self.notes_preview)

        self.update_content()

    def update_content(self):
        if self.entry:
            severity = self.entry.severity
            color = SEVERITY_COLORS.get(severity, "#9E9E9E")

            self.severity_indicator.setText(str(severity))
            self.severity_indicator.setStyleSheet(f"""
                background-color: {color}; color: white;
                border-radius: 12px; font-weight: bold;
            """)

            sev_texts = {1: "Sehr gut", 2: "Gut", 3: "Mittel", 4: "Schlecht", 5: "Sehr schlecht"}
            self.severity_text.setText(sev_texts.get(severity, ""))

            # Trigger icons
            icons = []
            if self.entry.fungal_active:
                icons.append("🍄")
            if self.entry.stress_level is not None and self.entry.stress_level >= 4:
                icons.append("😰")
            if self.entry.sweating:
                icons.append("💧")
            if self.entry.sleep_quality is not None and self.entry.sleep_quality <= 2:
                icons.append("😴")
            if self.entry.weather and "Trocken" in self.entry.weather:
                icons.append("🏜")
            self.trigger_label.setText(" ".join(icons))

            # Food emojis
            if self.entry.foods:
                emojis = [FOOD_EMOJIS.get(f, "🍽️") for f in self.entry.foods[:5]]
                self.food_label.setText(" ".join(emojis))
                self.food_label.setStyleSheet("font-size: 12px;")
            else:
                self.food_label.setText("")
                self.food_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")

            # Notes preview
            notes = self.entry.skin_notes or self.entry.food_notes or ""
            if notes:
                self.notes_preview.setText(notes[:32] + "..." if len(notes) > 35 else notes)
            else:
                self.notes_preview.setText("")
        else:
            self.severity_indicator.setText("-")
            self.severity_indicator.setStyleSheet(f"""
                background-color: #E0E0E0; color: {COLOR_TEXT_SECONDARY}; border-radius: 12px;
            """)
            self.severity_text.setText("Kein Eintrag")
            self.trigger_label.setText("")
            self.food_label.setText("")
            self.notes_preview.setText("")

    def update_style(self):
        severity = self.entry.severity if self.entry else None
        base_color = SEVERITY_COLORS.get(severity, "#E0E0E0") if severity else "#E0E0E0"

        if self._is_selected:
            border_color, border_width, bg = COLOR_PRIMARY, "3px", "#E3F2FD"
        elif self._is_today:
            border_color, border_width, bg = "#424242", "2px", "#FFFFFF"
        else:
            border_color, border_width, bg = "#E0E0E0", "1px", "#FFFFFF"

        self.setStyleSheet(f"""
            QFrame#dayCard {{
                background-color: {bg};
                border: {border_width} solid {border_color};
                border-radius: 8px;
                border-left: 4px solid {base_color};
            }}
            QFrame#dayCard:hover {{
                border-color: {COLOR_PRIMARY};
                background-color: #FAFAFA;
            }}
        """)
        if self._is_today:
            self.date_label.setStyleSheet(f"color: {COLOR_PRIMARY}; font-weight: bold;")

    def set_entry(self, entry: DayEntry):
        self.entry = entry
        self.update_content()
        self.update_style()

    def set_selected(self, selected: bool):
        self._is_selected = selected
        self.update_style()

    def is_selected(self) -> bool:
        return self._is_selected

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.display_date)
        super().mousePressEvent(event)


class EmptyDayCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(160, 150)
        self.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border: 1px dashed #E0E0E0;
                border-radius: 8px;
            }
        """)
