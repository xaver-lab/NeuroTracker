"""
Settings Screen – module toggles, app info, data management (KivyMD 1.2.0).
Allows users to enable/disable tracker modules and manage app settings.
"""

from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.card import MDCard, MDSeparator
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.snackbar import Snackbar

from config import TRACKER_MODULES, APP_NAME, APP_VERSION, APP_AUTHOR


def _hex_to_rgba(hex_color: str) -> list:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255
    return [r, g, b, 1]


class _ModuleToggleCard(MDCard):
    """A card with icon, label, description, and toggle switch for a module."""

    def __init__(self, module_key: str, module_info: dict, enabled: bool,
                 on_toggle=None, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(72),
            padding=[dp(16), dp(12), dp(16), dp(12)],
            radius=[dp(12)],
            elevation=1,
            md_bg_color=_hex_to_rgba("#FFFFFF"),
            ripple_behavior=True,
            **kwargs,
        )
        self.module_key = module_key
        self._on_toggle = on_toggle

        # Left: icon + text
        left = MDBoxLayout(orientation="horizontal", spacing=dp(12), size_hint_x=0.8)

        icon_label = MDLabel(
            text=module_info.get("icon", ""),
            font_style="H5",
            size_hint=(None, None),
            size=(dp(40), dp(40)),
            halign="center",
            valign="middle",
        )
        left.add_widget(icon_label)

        text_col = MDBoxLayout(orientation="vertical", adaptive_height=True)
        text_col.add_widget(MDLabel(
            text=module_info.get("label", module_key),
            font_style="Subtitle1",
            bold=True,
            adaptive_height=True,
        ))
        descriptions = {
            "stress": "Tägliches Stresslevel (1-5)",
            "fungal": "Zehenpilz-Aktivität tracken",
            "sleep": "Schlafqualität bewerten",
            "weather": "Wetter & Umgebung erfassen",
            "sweating": "Starkes Schwitzen dokumentieren",
            "contact": "Kontakt mit Allergenen",
        }
        desc_text = descriptions.get(module_key, "")
        if desc_text:
            text_col.add_widget(MDLabel(
                text=desc_text,
                theme_text_color="Secondary",
                font_style="Caption",
                adaptive_height=True,
            ))
        left.add_widget(text_col)
        self.add_widget(left)

        # Right: toggle switch
        switch_container = MDBoxLayout(
            size_hint_x=0.2,
            adaptive_height=False,
            padding=[dp(0), dp(10), dp(0), dp(0)],
        )
        self.switch = MDSwitch(active=enabled)
        self.switch.bind(active=self._on_switch_change)
        switch_container.add_widget(self.switch)
        self.add_widget(switch_container)

    def _on_switch_change(self, instance, value):
        if self._on_toggle:
            self._on_toggle(self.module_key, value)


class SettingsScreen(MDScreen):
    """Settings screen with module toggles and app information."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._module_cards = {}
        Clock.schedule_once(self._build_ui, 0)

    def _build_ui(self, *_):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        self.settings_manager = app.settings_manager

        root = MDBoxLayout(orientation="vertical")

        # Title bar
        title_bar = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            padding=[dp(20), dp(16), dp(20), dp(8)],
        )
        title_bar.add_widget(MDLabel(
            text="Einstellungen",
            font_style="H5",
            bold=True,
            adaptive_height=True,
        ))
        root.add_widget(title_bar)

        # Scrollable content
        scroll = ScrollView()
        self.content = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            padding=[dp(16), dp(0), dp(16), dp(24)],
            spacing=dp(8),
        )

        self._build_modules_section()
        self._build_data_section()
        self._build_about_section()

        scroll.add_widget(self.content)
        root.add_widget(scroll)
        self.add_widget(root)

    # ── Module Toggles ───────────────────────────────────────────────────────

    def _build_modules_section(self):
        # Section header
        header = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            padding=[dp(4), dp(8), dp(4), dp(4)],
        )
        header.add_widget(MDLabel(
            text="Tracker-Module",
            font_style="H6",
            bold=True,
            adaptive_height=True,
        ))
        self.content.add_widget(header)

        self.content.add_widget(MDLabel(
            text="Aktiviere oder deaktiviere Module für den Tageseintrag.",
            theme_text_color="Secondary",
            font_style="Caption",
            adaptive_height=True,
            padding=[dp(4), dp(0), dp(4), dp(8)],
        ))

        all_modules = self.settings_manager.get_all_modules()
        for key in TRACKER_MODULES:
            info = TRACKER_MODULES[key]
            enabled = all_modules.get(key, info["enabled"])
            card = _ModuleToggleCard(
                module_key=key,
                module_info=info,
                enabled=enabled,
                on_toggle=self._on_module_toggle,
            )
            self._module_cards[key] = card
            self.content.add_widget(card)

        self.content.add_widget(MDLabel(
            text="Änderungen werden nach dem nächsten Öffnen des Eintrags-Tabs wirksam.",
            theme_text_color="Secondary",
            font_style="Caption",
            adaptive_height=True,
            padding=[dp(4), dp(4), dp(4), dp(16)],
        ))

    def _on_module_toggle(self, module_key: str, enabled: bool):
        self.settings_manager.set_module_enabled(module_key, enabled)
        state_text = "aktiviert" if enabled else "deaktiviert"
        info = TRACKER_MODULES.get(module_key, {})
        label = info.get("label", module_key)
        Snackbar(text=f"{info.get('icon', '')} {label} {state_text}").open()

    # ── Data Management ──────────────────────────────────────────────────────

    def _build_data_section(self):
        self.content.add_widget(MDSeparator(height=dp(1)))

        header = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            padding=[dp(4), dp(16), dp(4), dp(8)],
        )
        header.add_widget(MDLabel(
            text="Daten",
            font_style="H6",
            bold=True,
            adaptive_height=True,
        ))
        self.content.add_widget(header)

        # Data info card
        data_card = MDCard(
            orientation="vertical",
            size_hint=(1, None),
            height=dp(100),
            padding=[dp(16), dp(12), dp(16), dp(12)],
            radius=[dp(12)],
            elevation=1,
            md_bg_color=_hex_to_rgba("#F5F5F5"),
        )

        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        total = len(app.data_manager.get_all_entries())
        food_count = len(app.food_manager.get_all_suggestions())

        info_row = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(16))
        info_row.add_widget(self._stat_mini("Einträge", str(total)))
        info_row.add_widget(self._stat_mini("Lebensmittel", str(food_count)))

        modules = self.settings_manager.get_all_modules()
        active_count = sum(1 for v in modules.values() if v)
        info_row.add_widget(self._stat_mini("Module aktiv", f"{active_count}/{len(modules)}"))

        data_card.add_widget(info_row)
        self.content.add_widget(data_card)

    def _stat_mini(self, title: str, value: str) -> MDBoxLayout:
        col = MDBoxLayout(orientation="vertical", adaptive_height=True, size_hint_x=1)
        col.add_widget(MDLabel(
            text=value,
            font_style="H6",
            bold=True,
            halign="center",
            adaptive_height=True,
        ))
        col.add_widget(MDLabel(
            text=title,
            theme_text_color="Secondary",
            font_style="Caption",
            halign="center",
            adaptive_height=True,
        ))
        return col

    # ── About Section ────────────────────────────────────────────────────────

    def _build_about_section(self):
        self.content.add_widget(MDSeparator(height=dp(1)))

        header = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            padding=[dp(4), dp(16), dp(4), dp(8)],
        )
        header.add_widget(MDLabel(
            text="Über die App",
            font_style="H6",
            bold=True,
            adaptive_height=True,
        ))
        self.content.add_widget(header)

        about_card = MDCard(
            orientation="vertical",
            size_hint=(1, None),
            height=dp(120),
            padding=[dp(16), dp(16), dp(16), dp(16)],
            radius=[dp(12)],
            elevation=1,
            md_bg_color=_hex_to_rgba("#F5F5F5"),
        )

        about_card.add_widget(MDLabel(
            text=f"{APP_NAME}",
            font_style="H6",
            bold=True,
            adaptive_height=True,
        ))
        about_card.add_widget(MDLabel(
            text=f"Version {APP_VERSION}",
            theme_text_color="Secondary",
            adaptive_height=True,
        ))
        about_card.add_widget(MDLabel(
            text=f"Entwickelt von {APP_AUTHOR}",
            theme_text_color="Secondary",
            font_style="Caption",
            adaptive_height=True,
        ))
        about_card.add_widget(MDLabel(
            text="Tracke Hautzustand, Trigger & Ernährung",
            theme_text_color="Secondary",
            font_style="Caption",
            adaptive_height=True,
        ))

        self.content.add_widget(about_card)

    # ── Refresh on tab switch ────────────────────────────────────────────────

    def on_enter_screen(self):
        """Refresh data counts when entering the settings tab."""
        pass
