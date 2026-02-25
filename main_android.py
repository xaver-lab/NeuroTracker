"""
NeuroTracker Android – KivyMD Entry Point
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
from kivy.metrics import dp

from kivymd.app import MDApp

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

# ---------- KV layout ----------
KV = """
#:import NoTransition kivy.uix.screenmanager.NoTransition

MDScreen:
    md_bg_color: app.theme_cls.backgroundColor

    MDBoxLayout:
        orientation: "vertical"

        MDScreenManager:
            id: screen_manager
            transition: NoTransition()

            EntryScreen:
                name: "entry"

            CalendarScreen:
                name: "calendar"

            StatsScreen:
                name: "stats"

        MDNavigationBar:
            on_switch_tabs: app.on_switch_tabs(*args)

            MDNavigationItem:
                MDNavigationItemIcon:
                    icon: "pencil"
                MDNavigationItemLabel:
                    text: "Heute"

            MDNavigationItem:
                MDNavigationItemIcon:
                    icon: "calendar-month"
                MDNavigationItemLabel:
                    text: "Kalender"

            MDNavigationItem:
                MDNavigationItemIcon:
                    icon: "chart-bar"
                MDNavigationItemLabel:
                    text: "Statistiken"
"""


class NeuroTrackerApp(MDApp):
    """KivyMD application for NeuroTracker Android."""

    def build(self):
        self.title = config.APP_NAME

        # Material Design 3 theme
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"

        # Shared data layer (identical to desktop)
        self.data_manager = DataManager()
        self.food_manager = FoodManager()
        self.settings_manager = SettingsManager()

        # Import screens here to avoid circular imports
        from mobile_ui.entry_screen import EntryScreen  # noqa: F401
        from mobile_ui.calendar_screen import CalendarScreen  # noqa: F401
        from mobile_ui.stats_screen import StatsScreen  # noqa: F401

        return Builder.load_string(KV)

    # ---------- Navigation ----------

    _tab_map = {
        "Heute": "entry",
        "Kalender": "calendar",
        "Statistiken": "stats",
    }

    def on_switch_tabs(self, bar, item, item_icon, item_text):
        screen_name = self._tab_map.get(item_text.text, "entry")
        self.root.ids.screen_manager.current = screen_name

        # Refresh screen data when entering
        screen = self.root.ids.screen_manager.get_screen(screen_name)
        if hasattr(screen, "on_enter_screen"):
            screen.on_enter_screen()


if __name__ == "__main__":
    NeuroTrackerApp().run()
