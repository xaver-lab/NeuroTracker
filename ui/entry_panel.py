"""
Entry Panel Widget for Neuro-Tracker Application
Left sidebar for entering/editing day data
"""

from datetime import date, datetime
from typing import List, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSlider, QLineEdit, QTextEdit, QFrame, QScrollArea,
    QCompleter, QMessageBox, QSizePolicy, QFlowLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QStringListModel
from PyQt5.QtGui import QFont

from config import (
    SEVERITY_COLORS, MIN_SEVERITY, MAX_SEVERITY,
    COLOR_PRIMARY, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_DANGER, COLOR_SUCCESS, ENTRY_PANEL_WIDTH
)
from models.day_entry import DayEntry
from models.data_manager import DataManager
from models.food_manager import FoodManager


class FlowLayout(QVBoxLayout):
    """Simple flow layout simulation using horizontal layouts"""
    pass


class FoodTag(QFrame):
    """A tag/chip widget for displaying a food item"""

    removed = pyqtSignal(str)  # Emitted when tag is removed

    def __init__(self, food: str, parent=None):
        super().__init__(parent)
        self.food = food
        self.setup_ui()

    def setup_ui(self):
        """Initialize the UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 4, 4)
        layout.setSpacing(4)

        label = QLabel(self.food)
        label.setStyleSheet(f"color: {COLOR_PRIMARY}; font-size: 13px;")

        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(20, 20)
        remove_btn.setCursor(Qt.PointingHandCursor)
        remove_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                color: {COLOR_PRIMARY};
                font-weight: bold;
                font-size: 16px;
            }}
            QPushButton:hover {{
                color: {COLOR_DANGER};
            }}
        """)
        remove_btn.clicked.connect(lambda: self.removed.emit(self.food))

        layout.addWidget(label)
        layout.addWidget(remove_btn)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: #E3F2FD;
                border: 1px solid {COLOR_PRIMARY};
                border-radius: 14px;
            }}
        """)


class EntryPanel(QWidget):
    """
    Panel for entering and editing day entries.
    Shows severity slider, food input, and notes.
    """

    entry_saved = pyqtSignal(date)  # Emitted when entry is saved
    entry_deleted = pyqtSignal(date)  # Emitted when entry is deleted

    def __init__(self, data_manager: DataManager, food_manager: FoodManager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.food_manager = food_manager
        self.current_date: Optional[date] = None
        self.current_entry: Optional[DayEntry] = None
        self.food_list: List[str] = []

        self.setFixedWidth(ENTRY_PANEL_WIDTH)
        self.setup_ui()

    def setup_ui(self):
        """Initialize the UI components"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: white;
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(20)

        # Date header
        self.date_label = QLabel("Datum auswählen")
        self.date_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.date_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
        self.content_layout.addWidget(self.date_label)

        self.weekday_label = QLabel("")
        self.weekday_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 14px;")
        self.content_layout.addWidget(self.weekday_label)

        # Separator
        self.content_layout.addWidget(self._create_separator())

        # Severity section
        severity_section = QWidget()
        severity_layout = QVBoxLayout(severity_section)
        severity_layout.setContentsMargins(0, 0, 0, 0)
        severity_layout.setSpacing(12)

        severity_header = QLabel("Hautzustand")
        severity_header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        severity_layout.addWidget(severity_header)

        # Severity buttons
        severity_buttons_layout = QHBoxLayout()
        severity_buttons_layout.setSpacing(8)

        self.severity_buttons = []
        severity_labels = ["1", "2", "3", "4", "5"]

        for i, label in enumerate(severity_labels, start=1):
            btn = QPushButton(label)
            btn.setFixedSize(48, 48)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty("severity", i)
            btn.clicked.connect(lambda checked, s=i: self.set_severity(s))
            self.severity_buttons.append(btn)
            severity_buttons_layout.addWidget(btn)

        severity_buttons_layout.addStretch()
        severity_layout.addLayout(severity_buttons_layout)

        # Severity description
        self.severity_description = QLabel("Wähle den Hautzustand (1=sehr gut, 5=sehr schlecht)")
        self.severity_description.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 12px;")
        self.severity_description.setWordWrap(True)
        severity_layout.addWidget(self.severity_description)

        self.content_layout.addWidget(severity_section)

        # Separator
        self.content_layout.addWidget(self._create_separator())

        # Food section
        food_section = QWidget()
        food_layout = QVBoxLayout(food_section)
        food_layout.setContentsMargins(0, 0, 0, 0)
        food_layout.setSpacing(12)

        food_header = QLabel("Lebensmittel")
        food_header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        food_layout.addWidget(food_header)

        # Food input with autocomplete
        food_input_layout = QHBoxLayout()

        self.food_input = QLineEdit()
        self.food_input.setPlaceholderText("Lebensmittel eingeben...")
        self.food_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLOR_PRIMARY};
            }}
        """)
        self.food_input.returnPressed.connect(self.add_food)

        # Setup autocomplete
        self.food_completer = QCompleter()
        self.food_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.food_completer.setFilterMode(Qt.MatchContains)
        self.food_input.setCompleter(self.food_completer)
        self.update_food_suggestions()

        add_food_btn = QPushButton("+")
        add_food_btn.setFixedSize(40, 40)
        add_food_btn.setCursor(Qt.PointingHandCursor)
        add_food_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
            }}
        """)
        add_food_btn.clicked.connect(self.add_food)

        food_input_layout.addWidget(self.food_input)
        food_input_layout.addWidget(add_food_btn)
        food_layout.addLayout(food_input_layout)

        # Food tags container
        self.food_tags_container = QWidget()
        self.food_tags_layout = QVBoxLayout(self.food_tags_container)
        self.food_tags_layout.setContentsMargins(0, 0, 0, 0)
        self.food_tags_layout.setSpacing(8)

        food_layout.addWidget(self.food_tags_container)

        self.content_layout.addWidget(food_section)

        # Separator
        self.content_layout.addWidget(self._create_separator())

        # Notes section
        notes_section = QWidget()
        notes_layout = QVBoxLayout(notes_section)
        notes_layout.setContentsMargins(0, 0, 0, 0)
        notes_layout.setSpacing(12)

        notes_header = QLabel("Notizen")
        notes_header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        notes_layout.addWidget(notes_header)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Weitere Notizen (z.B. Stress, Schlaf, Wetter...)")
        self.notes_input.setMaximumHeight(100)
        self.notes_input.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }}
            QTextEdit:focus {{
                border: 2px solid {COLOR_PRIMARY};
            }}
        """)
        notes_layout.addWidget(self.notes_input)

        self.content_layout.addWidget(notes_section)

        # Stretch to push buttons to bottom
        self.content_layout.addStretch()

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Action buttons at bottom
        button_container = QWidget()
        button_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-top: 1px solid #E0E0E0;
            }
        """)
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(20, 15, 20, 15)
        button_layout.setSpacing(10)

        self.save_button = QPushButton("Speichern")
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_SUCCESS};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #388E3C;
            }}
            QPushButton:disabled {{
                background-color: #BDBDBD;
            }}
        """)
        self.save_button.clicked.connect(self.save_entry)

        self.delete_button = QPushButton("Eintrag löschen")
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                color: {COLOR_DANGER};
                border: 1px solid {COLOR_DANGER};
                border-radius: 4px;
                padding: 12px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #FFEBEE;
            }}
        """)
        self.delete_button.clicked.connect(self.delete_entry)
        self.delete_button.setVisible(False)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.delete_button)

        main_layout.addWidget(button_container)

        # Initialize severity buttons style
        self.current_severity = None
        self.update_severity_buttons()

    def _create_separator(self) -> QFrame:
        """Create a horizontal separator line"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #E0E0E0;")
        separator.setFixedHeight(1)
        return separator

    def set_date(self, selected_date: date):
        """Set the date to edit"""
        self.current_date = selected_date
        self.current_entry = self.data_manager.get_entry(selected_date)

        # Update date display
        weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        months = ["Januar", "Februar", "März", "April", "Mai", "Juni",
                 "Juli", "August", "September", "Oktober", "November", "Dezember"]

        self.date_label.setText(f"{selected_date.day}. {months[selected_date.month - 1]} {selected_date.year}")
        self.weekday_label.setText(weekdays[selected_date.weekday()])

        # Load entry data
        if self.current_entry:
            self.set_severity(self.current_entry.severity)
            self.food_list = list(self.current_entry.foods)
            self.notes_input.setText(self.current_entry.notes or "")
            self.delete_button.setVisible(True)
        else:
            self.current_severity = None
            self.food_list = []
            self.notes_input.clear()
            self.delete_button.setVisible(False)

        self.update_severity_buttons()
        self.update_food_tags()

    def set_severity(self, severity: int):
        """Set the current severity level"""
        self.current_severity = severity
        self.update_severity_buttons()

        severity_descriptions = {
            1: "Sehr gut - Haut ist klar und gesund",
            2: "Gut - Leichte Rötungen möglich",
            3: "Mittel - Moderate Symptome",
            4: "Schlecht - Deutliche Symptome",
            5: "Sehr schlecht - Starke Symptome"
        }
        self.severity_description.setText(severity_descriptions.get(severity, ""))

    def update_severity_buttons(self):
        """Update the style of severity buttons"""
        for btn in self.severity_buttons:
            severity = btn.property("severity")
            color = SEVERITY_COLORS.get(severity, "#9E9E9E")

            if severity == self.current_severity:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {color};
                        color: white;
                        border: 2px solid {color};
                        border-radius: 24px;
                        font-weight: bold;
                        font-size: 16px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: white;
                        color: {color};
                        border: 2px solid {color};
                        border-radius: 24px;
                        font-weight: bold;
                        font-size: 16px;
                    }}
                    QPushButton:hover {{
                        background-color: {color}20;
                    }}
                """)

    def update_food_suggestions(self):
        """Update the food autocomplete suggestions"""
        all_foods = set(self.food_manager.get_all_suggestions())
        all_foods.update(self.data_manager.get_all_foods())

        model = QStringListModel(sorted(all_foods))
        self.food_completer.setModel(model)

    def add_food(self):
        """Add a food item from the input"""
        food = self.food_input.text().strip()
        if food and food not in self.food_list:
            self.food_list.append(food)
            self.food_manager.add_food(food)
            self.update_food_tags()
            self.update_food_suggestions()
        self.food_input.clear()

    def remove_food(self, food: str):
        """Remove a food item"""
        if food in self.food_list:
            self.food_list.remove(food)
            self.update_food_tags()

    def update_food_tags(self):
        """Update the food tags display"""
        # Clear existing tags
        while self.food_tags_layout.count():
            item = self.food_tags_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.food_list:
            empty_label = QLabel("Noch keine Lebensmittel hinzugefügt")
            empty_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-style: italic;")
            self.food_tags_layout.addWidget(empty_label)
            return

        # Create rows of tags (flow layout simulation)
        row_layout = None
        row_width = 0
        max_width = ENTRY_PANEL_WIDTH - 60  # Account for padding

        for food in self.food_list:
            tag = FoodTag(food)
            tag.removed.connect(self.remove_food)

            # Estimate tag width (rough calculation)
            tag_width = len(food) * 8 + 50

            if row_layout is None or row_width + tag_width > max_width:
                row_layout = QHBoxLayout()
                row_layout.setSpacing(8)
                row_layout.setAlignment(Qt.AlignLeft)
                self.food_tags_layout.addLayout(row_layout)
                row_width = 0

            row_layout.addWidget(tag)
            row_width += tag_width

    def save_entry(self):
        """Save the current entry"""
        if not self.current_date:
            return

        if self.current_severity is None:
            QMessageBox.warning(self, "Fehler", "Bitte wähle einen Hautzustand aus.")
            return

        entry = DayEntry(
            date=self.current_date.isoformat(),
            severity=self.current_severity,
            foods=self.food_list,
            notes=self.notes_input.toPlainText().strip() or None
        )

        self.data_manager.add_or_update_entry(entry)
        self.current_entry = entry
        self.delete_button.setVisible(True)

        self.entry_saved.emit(self.current_date)

        QMessageBox.information(self, "Gespeichert", "Eintrag wurde erfolgreich gespeichert.")

    def delete_entry(self):
        """Delete the current entry"""
        if not self.current_date or not self.current_entry:
            return

        reply = QMessageBox.question(
            self, "Löschen bestätigen",
            f"Möchtest du den Eintrag vom {self.date_label.text()} wirklich löschen?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.data_manager.delete_entry(self.current_date)
            self.current_entry = None
            self.current_severity = None
            self.food_list = []
            self.notes_input.clear()
            self.delete_button.setVisible(False)

            self.update_severity_buttons()
            self.update_food_tags()

            self.entry_deleted.emit(self.current_date)

            QMessageBox.information(self, "Gelöscht", "Eintrag wurde gelöscht.")

    def clear(self):
        """Clear the panel"""
        self.current_date = None
        self.current_entry = None
        self.current_severity = None
        self.food_list = []

        self.date_label.setText("Datum auswählen")
        self.weekday_label.setText("")
        self.notes_input.clear()
        self.delete_button.setVisible(False)

        self.update_severity_buttons()
        self.update_food_tags()
