"""
Entry Panel Widget for Neuro-Tracker Application
Left sidebar with tab navigation: Hautzustand / Lebensmittel / Trigger.
Trigger modules are shown/hidden based on SettingsManager.
"""

from datetime import date
from typing import List, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame, QScrollArea, QMessageBox, QSizePolicy,
    QGridLayout, QCheckBox, QComboBox, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont
import json

from config import (
    SEVERITY_COLORS, MIN_SEVERITY, MAX_SEVERITY,
    COLOR_PRIMARY, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_DANGER, COLOR_SUCCESS, ENTRY_PANEL_WIDTH, FOOD_SUGGESTIONS_FILE,
    STRESS_COLORS, SLEEP_COLORS, WEATHER_OPTIONS, CONTACT_SUGGESTIONS,
    NICKEL_RICH_FOODS,
)
from models.day_entry import DayEntry
from models.data_manager import DataManager
from models.food_manager import FoodManager
from models.settings_manager import SettingsManager


class EntryPanel(QWidget):
    """
    Left panel with tab navigation for day entry editing.
    Tabs: Hautzustand | Lebensmittel | Trigger
    """

    entry_saved = pyqtSignal(date)
    entry_deleted = pyqtSignal(date)

    def __init__(
        self,
        data_manager: DataManager,
        food_manager: FoodManager,
        settings_manager: Optional[SettingsManager] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.data_manager = data_manager
        self.food_manager = food_manager
        self.settings_manager = settings_manager or SettingsManager()
        self.current_date: Optional[date] = None
        self.current_entry: Optional[DayEntry] = None

        self.setFixedWidth(ENTRY_PANEL_WIDTH)
        self.setup_ui()

    # ── Main UI ────────────────────────────────────────────────────────────────

    def setup_ui(self):
        self.setStyleSheet("QWidget { background-color: white; }")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Date header (always visible) ───────────────────────────────────────
        header = QWidget()
        header.setStyleSheet("QWidget { background-color: white; }")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 12)
        header_layout.setSpacing(4)

        self.date_label = QLabel("Datum auswählen")
        self.date_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.date_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")
        header_layout.addWidget(self.date_label)

        self.weekday_label = QLabel("")
        self.weekday_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 14px;")
        header_layout.addWidget(self.weekday_label)

        main_layout.addWidget(header)

        # ── Tab widget ─────────────────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background-color: white;
            }}
            QTabBar::tab {{
                padding: 8px 12px;
                margin: 0 2px;
                background-color: #F5F5F5;
                border: 1px solid #E0E0E0;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 11px;
                font-weight: bold;
            }}
            QTabBar::tab:selected {{
                background-color: white;
                border-bottom: 2px solid {COLOR_PRIMARY};
                color: {COLOR_PRIMARY};
            }}
            QTabBar::tab:!selected {{
                color: {COLOR_TEXT_SECONDARY};
            }}
        """)

        # Tab 1: Hautzustand
        self.skin_tab = self._create_scrollable_tab()
        self._build_severity_section(self.skin_tab.layout())
        self.skin_tab.layout().addStretch()
        self.tabs.addTab(self.skin_tab, "Hautzustand")

        # Tab 2: Lebensmittel
        self.food_tab = self._create_scrollable_tab()
        self._build_food_section(self.food_tab.layout())
        self.food_tab.layout().addStretch()
        self.tabs.addTab(self.food_tab, "Lebensmittel")

        # Tab 3: Trigger (modular)
        self.trigger_tab = self._create_scrollable_tab()
        self._build_trigger_sections()
        self.tabs.addTab(self.trigger_tab, "Trigger")

        main_layout.addWidget(self.tabs, stretch=1)

        # ── Action bar ─────────────────────────────────────────────────────────
        main_layout.addWidget(self._build_action_bar())

        self.current_severity = None
        self.current_stress = None
        self.current_sleep = None
        self.update_severity_buttons()

    def _create_scrollable_tab(self) -> QWidget:
        """Create a scrollable container for a tab."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(16, 12, 16, 12)
        inner_layout.setSpacing(16)

        scroll.setWidget(inner)

        # Wrap scroll area in a QWidget so the tab can hold it
        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addWidget(scroll)

        # Store reference to inner layout
        wrapper._inner_layout = inner_layout
        wrapper.layout = lambda: inner_layout  # convenience accessor

        return wrapper

    # ── Tab 1: Hautzustand ─────────────────────────────────────────────────────

    def _build_severity_section(self, layout):
        header = QLabel("Hautzustand")
        header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(header)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.severity_buttons = []
        for i in range(1, 6):
            btn = QPushButton(str(i))
            btn.setFixedSize(48, 48)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty("severity", i)
            btn.clicked.connect(lambda _, s=i: self.set_severity(s))
            self.severity_buttons.append(btn)
            btn_row.addWidget(btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self.severity_description = QLabel("1 = sehr gut  —  5 = sehr schlecht")
        self.severity_description.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 12px;")
        self.severity_description.setWordWrap(True)
        layout.addWidget(self.severity_description)

        layout.addWidget(self._sep())

        skin_lbl = QLabel("Notizen Hautzustand")
        skin_lbl.setFont(QFont("Segoe UI", 12))
        skin_lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
        layout.addWidget(skin_lbl)

        self.skin_notes_input = QTextEdit()
        self.skin_notes_input.setPlaceholderText("z.B. Rötungen, Juckreiz, Stellen...")
        self.skin_notes_input.setMaximumHeight(80)
        self.skin_notes_input.setStyleSheet(self._input_style())
        layout.addWidget(self.skin_notes_input)

    # ── Tab 2: Lebensmittel ────────────────────────────────────────────────────

    def _build_food_section(self, layout):
        header = QLabel("Lebensmittel")
        header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(header)

        self.fixed_foods = self._load_food_suggestions()
        self.food_checkboxes: dict = {}

        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(4)

        for idx, food in enumerate(self.fixed_foods):
            is_nickel = food in NICKEL_RICH_FOODS
            cb = QCheckBox(food + (" [Ni]" if is_nickel else ""))
            if is_nickel:
                cb.setStyleSheet(self._nickel_checkbox_style())
                cb.setToolTip("Nickelreich — kann Dyshidrosis-Schübe begünstigen")
            else:
                cb.setStyleSheet(self._checkbox_style())
            grid.addWidget(cb, idx // 2, idx % 2)
            self.food_checkboxes[food] = cb

        layout.addWidget(grid_widget)

        layout.addWidget(self._sep())

        food_lbl = QLabel("Notizen Nahrung")
        food_lbl.setFont(QFont("Segoe UI", 12))
        food_lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
        layout.addWidget(food_lbl)

        self.food_notes_input = QTextEdit()
        self.food_notes_input.setPlaceholderText("z.B. Menge, Zubereitung...")
        self.food_notes_input.setMaximumHeight(80)
        self.food_notes_input.setStyleSheet(self._input_style())
        layout.addWidget(self.food_notes_input)

        # Hidden legacy field
        self.notes_input = QTextEdit()
        self.notes_input.setVisible(False)

    # ── Tab 3: Trigger (modular sections) ──────────────────────────────────────

    def _build_trigger_sections(self):
        """Build all enabled trigger modules into the trigger tab."""
        layout = self.trigger_tab.layout()

        # Clear existing
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            if item.spacerItem():
                pass  # spacers get removed automatically

        sm = self.settings_manager
        modules = [
            ("stress",   self._build_stress_section),
            ("fungal",   self._build_fungal_section),
            ("sleep",    self._build_sleep_section),
            ("weather",  self._build_weather_section),
            ("sweating", self._build_sweating_section),
            ("contact",  self._build_contact_section),
        ]

        has_any = False
        for key, builder in modules:
            if sm.is_module_enabled(key):
                widget = builder()
                layout.addWidget(widget)
                layout.addWidget(self._sep())
                has_any = True

        if not has_any:
            hint = QLabel(
                "Keine Trigger-Module aktiv.\n\n"
                "Aktiviere Module über:\nEinstellungen → Tracker-Module"
            )
            hint.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-style: italic; padding: 16px;")
            hint.setWordWrap(True)
            hint.setAlignment(Qt.AlignCenter)
            layout.addWidget(hint)

        layout.addStretch()

    def _build_stress_section(self) -> QWidget:
        section = QWidget()
        lay = QVBoxLayout(section)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        header = QLabel("😰 Stresslevel")
        header.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lay.addWidget(header)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.stress_buttons = []
        for i in range(1, 6):
            btn = QPushButton(str(i))
            btn.setFixedSize(44, 44)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty("stress_val", i)
            btn.clicked.connect(lambda _, s=i: self.set_stress(s))
            self.stress_buttons.append(btn)
            btn_row.addWidget(btn)
        btn_row.addStretch()
        lay.addLayout(btn_row)

        lbl = QLabel("1 = entspannt  —  5 = extremer Stress")
        lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
        lay.addWidget(lbl)

        self.current_stress = getattr(self, 'current_stress', None)
        self.update_stress_buttons()
        return section

    def _build_fungal_section(self) -> QWidget:
        section = QWidget()
        lay = QVBoxLayout(section)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        header = QLabel("🍄 Zehenpilz (Mykose)")
        header.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lay.addWidget(header)

        self.fungal_checkbox = QCheckBox("Zehenpilz aktuell aktiv")
        self.fungal_checkbox.setStyleSheet(f"""
            QCheckBox {{
                font-size: 13px; padding: 6px;
                border: 1px solid #E0E0E0; border-radius: 6px;
            }}
            QCheckBox:checked {{
                background-color: #FFF3E0; border: 2px solid #FF9800; font-weight: bold;
            }}
            QCheckBox::indicator {{ width: 18px; height: 18px; }}
            QCheckBox::indicator:checked {{
                background-color: #FF9800; border: 1px solid #FF9800; border-radius: 3px;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: white; border: 1px solid #BDBDBD; border-radius: 3px;
            }}
        """)
        self.fungal_checkbox.setToolTip(
            "Tinea pedis kann eine Id-Reaktion an den Händen auslösen"
        )
        lay.addWidget(self.fungal_checkbox)

        hint = QLabel("Id-Reaktion: Pilz → Schub an den Händen")
        hint.setStyleSheet("color: #FF9800; font-size: 11px;")
        hint.setWordWrap(True)
        lay.addWidget(hint)
        return section

    def _build_sleep_section(self) -> QWidget:
        section = QWidget()
        lay = QVBoxLayout(section)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        header = QLabel("😴 Schlafqualität")
        header.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lay.addWidget(header)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self.sleep_buttons = []
        for i in range(1, 6):
            btn = QPushButton(str(i))
            btn.setFixedSize(44, 44)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty("sleep_val", i)
            btn.clicked.connect(lambda _, s=i: self.set_sleep(s))
            self.sleep_buttons.append(btn)
            btn_row.addWidget(btn)
        btn_row.addStretch()
        lay.addLayout(btn_row)

        lbl = QLabel("1 = schlecht  —  5 = ausgezeichnet")
        lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
        lay.addWidget(lbl)

        self.current_sleep = getattr(self, 'current_sleep', None)
        self.update_sleep_buttons()
        return section

    def _build_weather_section(self) -> QWidget:
        section = QWidget()
        lay = QVBoxLayout(section)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        header = QLabel("🌤 Wetter / Umgebung")
        header.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lay.addWidget(header)

        self.weather_combo = QComboBox()
        self.weather_combo.addItem("— nicht erfasst —")
        for opt in WEATHER_OPTIONS:
            self.weather_combo.addItem(opt)
        self.weather_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 6px 10px; border: 1px solid #E0E0E0;
                border-radius: 4px; font-size: 12px;
            }}
            QComboBox:focus {{ border: 2px solid {COLOR_PRIMARY}; }}
        """)
        lay.addWidget(self.weather_combo)
        return section

    def _build_sweating_section(self) -> QWidget:
        section = QWidget()
        lay = QVBoxLayout(section)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        header = QLabel("💧 Schwitzen")
        header.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lay.addWidget(header)

        self.sweating_checkbox = QCheckBox("Starkes Schwitzen heute")
        self.sweating_checkbox.setStyleSheet(self._checkbox_style())
        lay.addWidget(self.sweating_checkbox)
        return section

    def _build_contact_section(self) -> QWidget:
        section = QWidget()
        lay = QVBoxLayout(section)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        header = QLabel("🧤 Kontaktexposition")
        header.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lay.addWidget(header)

        self.contact_checkboxes: dict = {}
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(4)
        for idx, item in enumerate(CONTACT_SUGGESTIONS):
            cb = QCheckBox(item)
            cb.setStyleSheet(self._checkbox_style())
            grid.addWidget(cb, idx // 2, idx % 2)
            self.contact_checkboxes[item] = cb
        lay.addWidget(grid_widget)
        return section

    # ── Action bar ─────────────────────────────────────────────────────────────

    def _build_action_bar(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet("""
            QWidget { background-color: white; border-top: 1px solid #E0E0E0; }
        """)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(8)

        self.save_button = QPushButton("Speichern")
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_SUCCESS}; color: white; border: none;
                border-radius: 4px; padding: 8px 16px; font-size: 12px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #388E3C; }}
            QPushButton:disabled {{ background-color: #BDBDBD; }}
        """)
        self.save_button.clicked.connect(self.save_entry)

        self.delete_button = QPushButton("Löschen")
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.setStyleSheet(f"""
            QPushButton {{
                background-color: white; color: {COLOR_DANGER};
                border: 1px solid {COLOR_DANGER}; border-radius: 4px;
                padding: 8px 16px; font-size: 12px;
            }}
            QPushButton:hover {{ background-color: #FFEBEE; }}
        """)
        self.delete_button.clicked.connect(self.delete_entry)
        self.delete_button.setVisible(False)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            f"color: {COLOR_SUCCESS}; font-size: 13px; font-weight: bold; padding: 5px;"
        )
        self.status_label.setVisible(False)

        layout.addWidget(self.save_button)
        layout.addWidget(self.delete_button)
        layout.addStretch()
        layout.addWidget(self.status_label)
        return container

    # ── Style helpers ──────────────────────────────────────────────────────────

    def _sep(self) -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background-color: #E0E0E0;")
        sep.setFixedHeight(1)
        return sep

    def _input_style(self) -> str:
        return f"""
            QTextEdit {{
                border: 1px solid #E0E0E0; border-radius: 4px;
                padding: 8px; font-size: 13px;
            }}
            QTextEdit:focus {{ border: 2px solid {COLOR_PRIMARY}; }}
        """

    def _checkbox_style(self) -> str:
        return f"""
            QCheckBox {{ font-size: 12px; padding: 4px; }}
            QCheckBox::indicator {{ width: 16px; height: 16px; }}
            QCheckBox::indicator:checked {{
                background-color: {COLOR_PRIMARY};
                border: 1px solid {COLOR_PRIMARY}; border-radius: 3px;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: white; border: 1px solid #BDBDBD; border-radius: 3px;
            }}
        """

    def _nickel_checkbox_style(self) -> str:
        return """
            QCheckBox { font-size: 12px; padding: 4px; color: #E65100; }
            QCheckBox::indicator { width: 16px; height: 16px; }
            QCheckBox::indicator:checked {
                background-color: #FF9800;
                border: 1px solid #FF9800; border-radius: 3px;
            }
            QCheckBox::indicator:unchecked {
                background-color: white; border: 1px solid #BDBDBD; border-radius: 3px;
            }
        """

    # ── Data helpers ───────────────────────────────────────────────────────────

    def _load_food_suggestions(self) -> list:
        try:
            with open(FOOD_SUGGESTIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return ["Milch", "Weizen", "Eier", "Nüsse", "Schokolade"]

    def get_selected_foods(self) -> list:
        return [f for f, cb in self.food_checkboxes.items() if cb.isChecked()]

    def set_food_checkboxes(self, foods: list):
        for f, cb in self.food_checkboxes.items():
            cb.setChecked(f in foods)

    def _get_weather_value(self) -> Optional[str]:
        if not hasattr(self, "weather_combo"):
            return None
        idx = self.weather_combo.currentIndex()
        return None if idx == 0 else self.weather_combo.currentText()

    def _set_weather_value(self, value: Optional[str]):
        if not hasattr(self, "weather_combo"):
            return
        if not value:
            self.weather_combo.setCurrentIndex(0)
            return
        for i in range(self.weather_combo.count()):
            if self.weather_combo.itemText(i) == value:
                self.weather_combo.setCurrentIndex(i)
                return

    def _get_contact_exposures(self) -> List[str]:
        if not hasattr(self, "contact_checkboxes"):
            return []
        return [item for item, cb in self.contact_checkboxes.items() if cb.isChecked()]

    def _set_contact_exposures(self, items: List[str]):
        if not hasattr(self, "contact_checkboxes"):
            return
        for item, cb in self.contact_checkboxes.items():
            cb.setChecked(item in items)

    # ── Button group updates ───────────────────────────────────────────────────

    def set_severity(self, severity: int):
        self.current_severity = severity
        self.update_severity_buttons()
        descs = {
            1: "Sehr gut — Haut ist klar",
            2: "Gut — Leichte Rötungen",
            3: "Mittel — Moderate Symptome",
            4: "Schlecht — Deutliche Symptome",
            5: "Sehr schlecht — Starke Symptome",
        }
        self.severity_description.setText(descs.get(severity, ""))

    def update_severity_buttons(self):
        self._update_buttons(
            getattr(self, "severity_buttons", []),
            getattr(self, "current_severity", None),
            SEVERITY_COLORS, "severity",
        )

    def set_stress(self, level: int):
        self.current_stress = level
        self.update_stress_buttons()

    def update_stress_buttons(self):
        self._update_buttons(
            getattr(self, "stress_buttons", []),
            getattr(self, "current_stress", None),
            STRESS_COLORS, "stress_val",
        )

    def set_sleep(self, level: int):
        self.current_sleep = level
        self.update_sleep_buttons()

    def update_sleep_buttons(self):
        self._update_buttons(
            getattr(self, "sleep_buttons", []),
            getattr(self, "current_sleep", None),
            SLEEP_COLORS, "sleep_val",
        )

    def _update_buttons(self, buttons, current, colors, prop):
        for btn in buttons:
            val = btn.property(prop)
            c = colors.get(val, "#9E9E9E")
            if val == current:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {c}; color: white;
                        border: 2px solid {c}; border-radius: 22px;
                        font-weight: bold; font-size: 15px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: white; color: {c};
                        border: 2px solid {c}; border-radius: 22px;
                        font-weight: bold; font-size: 15px;
                    }}
                    QPushButton:hover {{ background-color: {c}20; }}
                """)

    # ── Date / Entry loading ───────────────────────────────────────────────────

    def set_date(self, selected_date: date):
        self.current_date = selected_date
        self.current_entry = self.data_manager.get_entry(selected_date)

        weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        months = ["Januar", "Februar", "März", "April", "Mai", "Juni",
                  "Juli", "August", "September", "Oktober", "November", "Dezember"]

        self.date_label.setText(
            f"{selected_date.day}. {months[selected_date.month - 1]} {selected_date.year}"
        )
        self.weekday_label.setText(weekdays[selected_date.weekday()])

        if self.current_entry:
            e = self.current_entry
            self.set_severity(e.severity)
            self.set_food_checkboxes(e.foods)
            self.skin_notes_input.setText(e.skin_notes or "")
            self.food_notes_input.setText(e.food_notes or "")
            if hasattr(self, "stress_buttons"):
                self.current_stress = e.stress_level
                self.update_stress_buttons()
            if hasattr(self, "fungal_checkbox"):
                self.fungal_checkbox.setChecked(bool(e.fungal_active))
            if hasattr(self, "sleep_buttons"):
                self.current_sleep = e.sleep_quality
                self.update_sleep_buttons()
            self._set_weather_value(e.weather)
            if hasattr(self, "sweating_checkbox"):
                self.sweating_checkbox.setChecked(bool(e.sweating))
            self._set_contact_exposures(e.contact_exposures or [])
            self.delete_button.setVisible(True)
        else:
            self.current_severity = None
            self.current_stress = None
            self.current_sleep = None
            self.set_food_checkboxes([])
            self.skin_notes_input.clear()
            self.food_notes_input.clear()
            if hasattr(self, "fungal_checkbox"):
                self.fungal_checkbox.setChecked(False)
            self._set_weather_value(None)
            if hasattr(self, "sweating_checkbox"):
                self.sweating_checkbox.setChecked(False)
            self._set_contact_exposures([])
            self.delete_button.setVisible(False)

        self.update_severity_buttons()
        if hasattr(self, "stress_buttons"):
            self.update_stress_buttons()
        if hasattr(self, "sleep_buttons"):
            self.update_sleep_buttons()

    # ── Save / Delete ──────────────────────────────────────────────────────────

    def save_entry(self):
        if not self.current_date:
            return
        if self.current_severity is None:
            QMessageBox.warning(self, "Fehler", "Bitte wähle einen Hautzustand aus.")
            return

        entry = DayEntry(
            date=self.current_date.isoformat(),
            severity=self.current_severity,
            foods=self.get_selected_foods(),
            skin_notes=self.skin_notes_input.toPlainText().strip(),
            food_notes=self.food_notes_input.toPlainText().strip(),
            stress_level=getattr(self, "current_stress", None),
            fungal_active=(
                self.fungal_checkbox.isChecked()
                if hasattr(self, "fungal_checkbox") else None
            ),
            sleep_quality=getattr(self, "current_sleep", None),
            weather=self._get_weather_value(),
            sweating=(
                self.sweating_checkbox.isChecked()
                if hasattr(self, "sweating_checkbox") else None
            ),
            contact_exposures=self._get_contact_exposures(),
        )

        self.data_manager.add_or_update_entry(entry)
        self.current_entry = entry
        self.delete_button.setVisible(True)
        self.entry_saved.emit(self.current_date)
        self.show_status_message("✓ Gespeichert")

    def delete_entry(self):
        if not self.current_date or not self.current_entry:
            return
        self.data_manager.delete_entry(self.current_date)
        self.current_entry = None
        self.current_severity = None
        self.current_stress = None
        self.current_sleep = None
        self.set_food_checkboxes([])
        self.skin_notes_input.clear()
        self.food_notes_input.clear()
        if hasattr(self, "fungal_checkbox"):
            self.fungal_checkbox.setChecked(False)
        self._set_weather_value(None)
        if hasattr(self, "sweating_checkbox"):
            self.sweating_checkbox.setChecked(False)
        self._set_contact_exposures([])
        self.delete_button.setVisible(False)
        self.update_severity_buttons()
        if hasattr(self, "stress_buttons"):
            self.update_stress_buttons()
        if hasattr(self, "sleep_buttons"):
            self.update_sleep_buttons()
        self.entry_deleted.emit(self.current_date)
        self.show_status_message("✓ Gelöscht")

    def show_status_message(self, message: str, duration: int = 2000):
        self.status_label.setText(message)
        self.status_label.setVisible(True)
        QTimer.singleShot(duration, lambda: self.status_label.setVisible(False))

    def rebuild_trigger_sections(self):
        """Rebuild trigger tab after module settings change."""
        self._build_trigger_sections()
        if self.current_date:
            self.set_date(self.current_date)

    def clear(self):
        self.current_date = None
        self.current_entry = None
        self.current_severity = None
        self.current_stress = None
        self.current_sleep = None
        self.set_food_checkboxes([])
        self.date_label.setText("Datum auswählen")
        self.weekday_label.setText("")
        self.skin_notes_input.clear()
        self.food_notes_input.clear()
        self.delete_button.setVisible(False)
        self.update_severity_buttons()
