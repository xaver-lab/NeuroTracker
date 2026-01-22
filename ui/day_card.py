"""
Day Card Widget for Neuro-Tracker Application
Displays a single day's entry in the calendar view
"""

from datetime import date, datetime
from PyQt5.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QSizePolicy, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QCursor

from config import SEVERITY_COLORS, COLOR_TEXT_SECONDARY, COLOR_PRIMARY
from models.day_entry import DayEntry


class DayCard(QFrame):
    """
    A card widget representing a single day in the calendar.
    Shows date, severity indicator, and food count.
    """

    clicked = pyqtSignal(date)  # Emitted when card is clicked

    def __init__(self, display_date: date, entry: DayEntry = None, parent=None):
        super().__init__(parent)
        self.display_date = display_date
        self.entry = entry
        self._is_selected = False
        self._is_today = display_date == date.today()

        self.setup_ui()
        self.update_style()

    def setup_ui(self):
        """Initialize the UI components"""
        self.setFixedSize(140, 120)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setObjectName("dayCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        # Header with day name and date
        header_layout = QHBoxLayout()

        # Day name (Mo, Di, Mi, etc.)
        day_names = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        day_name = day_names[self.display_date.weekday()]

        self.day_label = QLabel(day_name)
        self.day_label.setFont(QFont("Segoe UI", 10, QFont.Bold))

        # Date number
        self.date_label = QLabel(str(self.display_date.day))
        self.date_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.date_label.setAlignment(Qt.AlignRight)

        header_layout.addWidget(self.day_label)
        header_layout.addStretch()
        header_layout.addWidget(self.date_label)

        layout.addLayout(header_layout)

        # Month indicator (only if not current month)
        if self.display_date.month != date.today().month:
            month_names = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun",
                          "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
            month_label = QLabel(month_names[self.display_date.month - 1])
            month_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
            month_label.setAlignment(Qt.AlignRight)
            layout.addWidget(month_label)

        layout.addStretch()

        # Severity indicator
        self.severity_widget = QWidget()
        severity_layout = QHBoxLayout(self.severity_widget)
        severity_layout.setContentsMargins(0, 0, 0, 0)
        severity_layout.setSpacing(4)

        self.severity_indicator = QLabel()
        self.severity_indicator.setFixedSize(24, 24)
        self.severity_indicator.setAlignment(Qt.AlignCenter)
        self.severity_indicator.setFont(QFont("Segoe UI", 11, QFont.Bold))

        self.severity_text = QLabel()
        self.severity_text.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")

        severity_layout.addWidget(self.severity_indicator)
        severity_layout.addWidget(self.severity_text)
        severity_layout.addStretch()

        layout.addWidget(self.severity_widget)

        # Food count
        self.food_label = QLabel()
        self.food_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
        layout.addWidget(self.food_label)

        self.update_content()

    def update_content(self):
        """Update the card content based on entry data"""
        if self.entry:
            severity = self.entry.severity
            color = SEVERITY_COLORS.get(severity, "#9E9E9E")

            self.severity_indicator.setText(str(severity))
            self.severity_indicator.setStyleSheet(f"""
                background-color: {color};
                color: white;
                border-radius: 12px;
                font-weight: bold;
            """)

            severity_texts = {
                1: "Sehr gut",
                2: "Gut",
                3: "Mittel",
                4: "Schlecht",
                5: "Sehr schlecht"
            }
            self.severity_text.setText(severity_texts.get(severity, ""))

            food_count = len(self.entry.foods)
            if food_count == 0:
                self.food_label.setText("Keine Speisen")
            elif food_count == 1:
                self.food_label.setText("1 Speise")
            else:
                self.food_label.setText(f"{food_count} Speisen")
        else:
            self.severity_indicator.setText("-")
            self.severity_indicator.setStyleSheet(f"""
                background-color: #E0E0E0;
                color: {COLOR_TEXT_SECONDARY};
                border-radius: 12px;
            """)
            self.severity_text.setText("Kein Eintrag")
            self.food_label.setText("")

    def update_style(self):
        """Update the card's visual style"""
        severity = self.entry.severity if self.entry else None
        base_color = SEVERITY_COLORS.get(severity, "#E0E0E0") if severity else "#E0E0E0"

        if self._is_selected:
            border_color = COLOR_PRIMARY
            border_width = "3px"
            bg_color = "#E3F2FD"
        elif self._is_today:
            border_color = "#424242"
            border_width = "2px"
            bg_color = "#FFFFFF"
        else:
            border_color = "#E0E0E0"
            border_width = "1px"
            bg_color = "#FFFFFF"

        self.setStyleSheet(f"""
            QFrame#dayCard {{
                background-color: {bg_color};
                border: {border_width} solid {border_color};
                border-radius: 8px;
                border-left: 4px solid {base_color};
            }}
            QFrame#dayCard:hover {{
                border-color: {COLOR_PRIMARY};
                background-color: #FAFAFA;
            }}
        """)

        # Update date label color for today
        if self._is_today:
            self.date_label.setStyleSheet(f"color: {COLOR_PRIMARY}; font-weight: bold;")

    def set_entry(self, entry: DayEntry):
        """Update the entry for this card"""
        self.entry = entry
        self.update_content()
        self.update_style()

    def set_selected(self, selected: bool):
        """Set the selection state of the card"""
        self._is_selected = selected
        self.update_style()

    def is_selected(self) -> bool:
        """Check if the card is selected"""
        return self._is_selected

    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.display_date)
        super().mousePressEvent(event)


class EmptyDayCard(QFrame):
    """
    A placeholder card for days outside the display range
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(140, 120)
        self.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border: 1px dashed #E0E0E0;
                border-radius: 8px;
            }
        """)
