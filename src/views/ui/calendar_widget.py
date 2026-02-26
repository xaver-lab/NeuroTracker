"""
Calendar Widget for Neuro-Tracker Application
Displays a 2-week calendar view with day cards
"""

from datetime import date, timedelta
from typing import Dict, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
    QPushButton, QScrollArea, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from config import (
    WEEKS_TO_DISPLAY, FIRST_DAY_OF_WEEK,
    COLOR_PRIMARY, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY
)
from models.day_entry import DayEntry
from models.data_manager import DataManager
from views.ui.day_card import DayCard


class CalendarWidget(QWidget):
    """
    A calendar widget showing multiple weeks of day cards.
    Allows navigation and selection of days.
    """

    date_selected = pyqtSignal(date)  # Emitted when a date is selected

    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.selected_date: Optional[date] = date.today()
        self.day_cards: Dict[date, DayCard] = {}
        self.current_start_date = self._calculate_start_date()

        self.setup_ui()
        self.load_entries()

    def _calculate_start_date(self) -> date:
        """Calculate the start date for the calendar view"""
        today = date.today()
        # Go back to the start of the current week
        days_since_week_start = (today.weekday() - FIRST_DAY_OF_WEEK) % 7
        week_start = today - timedelta(days=days_since_week_start)
        # Go back additional weeks
        return week_start - timedelta(weeks=WEEKS_TO_DISPLAY - 1)

    def setup_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Header with navigation
        header_layout = QHBoxLayout()

        # Navigation buttons
        self.prev_button = QPushButton("◀ Früher")
        self.prev_button.setFixedWidth(100)
        self.prev_button.clicked.connect(self.go_previous)
        self.prev_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #2196F3;
                border: 1px solid #2196F3;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #E3F2FD;
            }
        """)

        # Title showing date range
        self.title_label = QLabel()
        self.title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")

        self.next_button = QPushButton("Später ▶")
        self.next_button.setFixedWidth(100)
        self.next_button.clicked.connect(self.go_next)
        self.next_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #2196F3;
                border: 1px solid #2196F3;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #E3F2FD;
            }
        """)

        # Today button
        self.today_button = QPushButton("Heute")
        self.today_button.setFixedWidth(80)
        self.today_button.clicked.connect(self.go_today)
        self.today_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)

        header_layout.addWidget(self.prev_button)
        header_layout.addStretch()
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.today_button)
        header_layout.addWidget(self.next_button)

        layout.addLayout(header_layout)

        # Day name headers
        day_names_layout = QHBoxLayout()
        day_names_layout.setSpacing(8)

        day_names = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        # Reorder based on first day of week
        day_names = day_names[FIRST_DAY_OF_WEEK:] + day_names[:FIRST_DAY_OF_WEEK]

        for name in day_names:
            label = QLabel(name)
            label.setAlignment(Qt.AlignCenter)
            label.setFixedWidth(140)
            label.setFont(QFont("Segoe UI", 11, QFont.Bold))
            label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
            day_names_layout.addWidget(label)

        day_names_layout.addStretch()
        layout.addLayout(day_names_layout)

        # Calendar grid in scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.calendar_container = QWidget()
        self.calendar_layout = QVBoxLayout(self.calendar_container)
        self.calendar_layout.setSpacing(8)
        self.calendar_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area.setWidget(self.calendar_container)
        layout.addWidget(scroll_area)

        self.update_title()
        self.create_day_cards()

    def update_title(self):
        """Update the title to show current date range"""
        end_date = self.current_start_date + timedelta(weeks=WEEKS_TO_DISPLAY) - timedelta(days=1)

        month_names = ["Januar", "Februar", "März", "April", "Mai", "Juni",
                      "Juli", "August", "September", "Oktober", "November", "Dezember"]

        if self.current_start_date.month == end_date.month:
            title = f"{self.current_start_date.day}. - {end_date.day}. {month_names[end_date.month - 1]} {end_date.year}"
        elif self.current_start_date.year == end_date.year:
            title = f"{self.current_start_date.day}. {month_names[self.current_start_date.month - 1]} - {end_date.day}. {month_names[end_date.month - 1]} {end_date.year}"
        else:
            title = f"{self.current_start_date.day}. {month_names[self.current_start_date.month - 1]} {self.current_start_date.year} - {end_date.day}. {month_names[end_date.month - 1]} {end_date.year}"

        self.title_label.setText(title)

    def create_day_cards(self):
        """Create day cards for the current view"""
        # Clear existing cards
        self.day_cards.clear()

        # Clear layout
        while self.calendar_layout.count():
            item = self.calendar_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

        # Create week rows
        current_date = self.current_start_date

        for week in range(WEEKS_TO_DISPLAY):
            week_layout = QHBoxLayout()
            week_layout.setSpacing(8)

            # Week number label
            week_num = current_date.isocalendar()[1]
            week_label = QLabel(f"KW {week_num}")
            week_label.setFixedWidth(50)
            week_label.setAlignment(Qt.AlignCenter)
            week_label.setStyleSheet(f"""
                color: {COLOR_TEXT_SECONDARY};
                font-size: 11px;
                font-weight: bold;
            """)

            for day in range(7):
                entry = self.data_manager.get_entry(current_date)
                card = DayCard(current_date, entry)
                card.clicked.connect(self.on_card_clicked)

                if current_date == self.selected_date:
                    card.set_selected(True)

                self.day_cards[current_date] = card
                week_layout.addWidget(card)
                current_date += timedelta(days=1)

            week_layout.addStretch()
            self.calendar_layout.addLayout(week_layout)

        self.calendar_layout.addStretch()

    def _clear_layout(self, layout):
        """Recursively clear a layout"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def load_entries(self):
        """Load entries for the current view"""
        end_date = self.current_start_date + timedelta(weeks=WEEKS_TO_DISPLAY)
        entries = self.data_manager.get_entries_in_range(self.current_start_date, end_date)

        for entry in entries:
            entry_date = date.fromisoformat(entry.date)
            if entry_date in self.day_cards:
                self.day_cards[entry_date].set_entry(entry)

    def on_card_clicked(self, clicked_date: date):
        """Handle card click"""
        # Deselect previous
        if self.selected_date and self.selected_date in self.day_cards:
            self.day_cards[self.selected_date].set_selected(False)

        # Select new
        self.selected_date = clicked_date
        if clicked_date in self.day_cards:
            self.day_cards[clicked_date].set_selected(True)

        self.date_selected.emit(clicked_date)

    def go_previous(self):
        """Go to previous weeks"""
        self.current_start_date -= timedelta(weeks=WEEKS_TO_DISPLAY)
        self.update_title()
        self.create_day_cards()
        self.load_entries()

        # Re-select the selected date if visible
        if self.selected_date in self.day_cards:
            self.day_cards[self.selected_date].set_selected(True)

    def go_next(self):
        """Go to next weeks"""
        self.current_start_date += timedelta(weeks=WEEKS_TO_DISPLAY)
        self.update_title()
        self.create_day_cards()
        self.load_entries()

        # Re-select the selected date if visible
        if self.selected_date in self.day_cards:
            self.day_cards[self.selected_date].set_selected(True)

    def go_today(self):
        """Jump to today"""
        self.current_start_date = self._calculate_start_date()
        self.update_title()
        self.create_day_cards()
        self.load_entries()

        # Select today
        today = date.today()
        if self.selected_date and self.selected_date in self.day_cards:
            self.day_cards[self.selected_date].set_selected(False)
        self.selected_date = today
        if today in self.day_cards:
            self.day_cards[today].set_selected(True)
        self.date_selected.emit(today)

    def refresh_date(self, refresh_date: date):
        """Refresh a specific date's card"""
        if refresh_date in self.day_cards:
            entry = self.data_manager.get_entry(refresh_date)
            self.day_cards[refresh_date].set_entry(entry)

    def refresh_all(self):
        """Refresh all cards"""
        self.load_entries()

    def select_date(self, select_date: date):
        """Programmatically select a date"""
        # Check if date is in view
        end_date = self.current_start_date + timedelta(weeks=WEEKS_TO_DISPLAY)
        if not (self.current_start_date <= select_date < end_date):
            # Navigate to show the date
            days_diff = (select_date - date.today()).days
            weeks_diff = days_diff // 7
            self.current_start_date = self._calculate_start_date() + timedelta(weeks=weeks_diff)
            self.update_title()
            self.create_day_cards()
            self.load_entries()

        self.on_card_clicked(select_date)
