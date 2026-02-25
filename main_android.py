"""
NeuroTracker Android – KivyMD 1.2.0 Entry Point
Shares models/ and utils/ with the PyQt5 desktop version.
"""

import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so shared modules resolve
sys.path.insert(0, str(Path(__file__).parent))

from kivy.core.window import Window
from kivy.utils import platform
from kivy.lang import Builder

import config
from models.data_manager import DataManager
from models.food_manager import FoodManager
from models.settings_manager import SettingsManager

# ---------- Android storage path adjustment ----------
if platform == "android":
    try:
        from android.storage import app_storage_path  # type: ignore
        config.DATA_DIR = Path(app_storage_path()) / "data"
        config.ENTRIES_FILE = config.DATA_DIR / "entries.json"
        config.FOOD_SUGGESTIONS_FILE = config.DATA_DIR / "food_suggestions.json"
        config.SETTINGS_FILE = config.DATA_DIR / "settings.json"
        config.SYNC_STATUS_FILE = config.DATA_DIR / "sync_status.json"
        config.GOOGLE_TOKEN_FILE = config.DATA_DIR / "token.json"
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    except ImportError:
        pass
else:
    # Desktop preview – simulate mobile dimensions
    Window.size = (400, 720)

# ---------- Import screens before KV so classes are registered ----------
from mobile_ui.entry_screen import EntryScreen  # noqa: F401
from mobile_ui.calendar_screen import CalendarScreen  # noqa: F401
from mobile_ui.stats_screen import StatsScreen  # noqa: F401

# ---------- KV layout ----------
KV = """
MDBoxLayout:
    orientation: "vertical"

    MDBottomNavigation:
        id: bottom_nav
        panel_color: app.theme_cls.bg_dark
        selected_color_background: app.theme_cls.primary_light
        text_color_active: app.theme_cls.primary_color

        MDBottomNavigationItem:
            name: "entry"
            text: "Heute"
            icon: "pencil"
            on_tab_press: app.on_tab_switch("entry")

            EntryScreen:
                id: entry_screen

        MDBottomNavigationItem:
            name: "calendar"
            text: "Kalender"
            icon: "calendar-month"
            on_tab_press: app.on_tab_switch("calendar")

            CalendarScreen:
                id: calendar_screen

        MDBottomNavigationItem:
            name: "stats"
            text: "Statistiken"
            icon: "chart-bar"
            on_tab_press: app.on_tab_switch("stats")

            StatsScreen:
                id: stats_screen
"""


from kivymd.app import MDApp


class NeuroTrackerApp(MDApp):
    """KivyMD 1.2.0 application for NeuroTracker Android."""

    def build(self):
        self.title = config.APP_NAME

        # Material Design theme (KivyMD 1.2.0)
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Amber"
        self.theme_cls.material_style = "M3"

        # Shared data layer (identical to desktop)
        self.data_manager = DataManager()
        self.food_manager = FoodManager()
        self.settings_manager = SettingsManager()

        return Builder.load_string(KV)

    def on_tab_switch(self, tab_name: str):
        """Refresh screen data when tab is selected."""
        root = self.root
        if tab_name == "entry" and hasattr(root.ids, "entry_screen"):
            root.ids.entry_screen.on_enter_screen()
        elif tab_name == "calendar" and hasattr(root.ids, "calendar_screen"):
            root.ids.calendar_screen.on_enter_screen()
        elif tab_name == "stats" and hasattr(root.ids, "stats_screen"):
            root.ids.stats_screen.on_enter_screen()


if __name__ == "__main__":
    NeuroTrackerApp().run()
