"""
Entry Screen – daily symptom & food logging (KivyMD 1.2.0).
Replaces ui/entry_panel.py.
"""

from datetime import date, timedelta
from typing import Optional, List

from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.chip import MDChip
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDSeparator
from kivymd.uix.snackbar import Snackbar

from config import (
    SEVERITY_COLORS, MIN_SEVERITY, MAX_SEVERITY,
    FOOD_EMOJIS, WEATHER_OPTIONS, CONTACT_SUGGESTIONS,
    NICKEL_RICH_FOODS, TRACKER_MODULES,
)
from models.day_entry import DayEntry


def _hex_to_rgba(hex_color: str) -> list:
    """Convert hex color string to RGBA list (0-1 range)."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255
    return [r, g, b, 1]


class EntryScreen(MDScreen):
    """Main screen for creating/editing a day entry."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_date: date = date.today()
        self.current_severity: Optional[int] = None
        self.current_stress: Optional[int] = None
        self.current_sleep: Optional[int] = None
        self.selected_foods: set = set()
        self.selected_contacts: set = set()
        self.fungal_active: bool = False
        self.sweating_active: bool = False
        self.selected_weather: Optional[str] = None

        self.severity_buttons: list = []
        self.stress_buttons: list = []
        self.sleep_buttons: list = []
        self.food_chips: dict = {}
        self.weather_chips: dict = {}
        self.contact_chips: dict = {}

        Clock.schedule_once(self._build_ui, 0)

    # ── Build UI ────────────────────────────────────────────────────────────────

    def _build_ui(self, *_):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        self.data_manager = app.data_manager
        self.food_manager = app.food_manager
        self.settings_manager = app.settings_manager

        root = MDBoxLayout(orientation="vertical")

        # ── Top bar: date navigation ────────────────────────────────────────────
        top_bar = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            padding=[dp(8), dp(8), dp(8), dp(0)],
            spacing=dp(4),
        )
        prev_btn = MDIconButton(
            icon="chevron-left",
            on_release=lambda *_: self._change_day(-1),
        )
        next_btn = MDIconButton(
            icon="chevron-right",
            on_release=lambda *_: self._change_day(1),
        )
        date_col = MDBoxLayout(orientation="vertical", adaptive_height=True, size_hint_x=1)
        self.date_label = MDLabel(
            text="", halign="center", font_style="H6", adaptive_height=True,
        )
        self.weekday_label = MDLabel(
            text="", halign="center",
            theme_text_color="Secondary", font_style="Caption",
            adaptive_height=True,
        )
        date_col.add_widget(self.date_label)
        date_col.add_widget(self.weekday_label)

        top_bar.add_widget(prev_btn)
        top_bar.add_widget(date_col)
        top_bar.add_widget(next_btn)
        root.add_widget(top_bar)

        # ── Scrollable content ──────────────────────────────────────────────────
        scroll = ScrollView()
        self.content = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            padding=[dp(16), dp(8), dp(16), dp(16)],
            spacing=dp(12),
        )

        self._build_severity_section()
        self.content.add_widget(MDSeparator(height=dp(1)))
        self._build_food_section()
        self.content.add_widget(MDSeparator(height=dp(1)))
        self._build_trigger_sections()
        self._build_notes_section()

        scroll.add_widget(self.content)
        root.add_widget(scroll)

        # ── Action bar ──────────────────────────────────────────────────────────
        action_bar = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            padding=[dp(16), dp(8), dp(16), dp(8)],
            spacing=dp(12),
        )
        save_btn = MDRaisedButton(
            text="Speichern",
            md_bg_color=_hex_to_rgba("#4CAF50"),
            on_release=lambda *_: self.save_entry(),
        )
        self.delete_btn = MDFlatButton(
            text="Löschen",
            text_color=_hex_to_rgba("#F44336"),
            on_release=lambda *_: self.delete_entry(),
        )
        self.delete_btn.opacity = 0
        self.delete_btn.disabled = True

        action_bar.add_widget(save_btn)
        action_bar.add_widget(self.delete_btn)
        root.add_widget(action_bar)

        self.add_widget(root)
        self._load_date(self.current_date)

    # ── Severity section ────────────────────────────────────────────────────────

    def _build_severity_section(self):
        self.content.add_widget(
            MDLabel(text="Hautzustand", font_style="Subtitle1", bold=True, adaptive_height=True)
        )
        row = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(8))
        self.severity_buttons = []
        for i in range(1, 6):
            btn = MDRaisedButton(
                text=str(i),
                size_hint=(None, None),
                size=(dp(52), dp(52)),
                md_bg_color=_hex_to_rgba("#E0E0E0"),
                on_release=lambda _, s=i: self._set_severity(s),
            )
            btn._sev_value = i
            self.severity_buttons.append(btn)
            row.add_widget(btn)
        self.content.add_widget(row)

        self.severity_desc = MDLabel(
            text="1 = sehr gut  —  5 = sehr schlecht",
            theme_text_color="Secondary",
            font_style="Caption",
            adaptive_height=True,
        )
        self.content.add_widget(self.severity_desc)

    def _set_severity(self, level: int):
        self.current_severity = level
        self._update_severity_buttons()
        descs = {
            1: "Sehr gut — Haut ist klar und gesund",
            2: "Gut — Leichte Rötungen möglich",
            3: "Mittel — Moderate Symptome",
            4: "Schlecht — Deutliche Symptome",
            5: "Sehr schlecht — Starke Symptome",
        }
        self.severity_desc.text = descs.get(level, "")

    def _update_severity_buttons(self):
        for btn in self.severity_buttons:
            i = btn._sev_value
            color_hex = SEVERITY_COLORS.get(i, "#9E9E9E")
            if i == self.current_severity:
                btn.md_bg_color = _hex_to_rgba(color_hex)
                btn.text_color = [1, 1, 1, 1]
            else:
                btn.md_bg_color = _hex_to_rgba("#E0E0E0")
                btn.text_color = _hex_to_rgba(color_hex)

    # ── Food section ────────────────────────────────────────────────────────────

    def _build_food_section(self):
        self.content.add_widget(
            MDLabel(text="Lebensmittel", font_style="Subtitle1", bold=True, adaptive_height=True)
        )
        food_flow = MDBoxLayout(
            orientation="vertical", adaptive_height=True, spacing=dp(4),
        )
        foods = self.food_manager.get_all_suggestions()
        row = None
        for idx, food in enumerate(foods):
            if idx % 3 == 0:
                row = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(4))
                food_flow.add_widget(row)
            emoji = FOOD_EMOJIS.get(food, "")
            is_nickel = food in NICKEL_RICH_FOODS
            label = f"{emoji} {food}" + (" [Ni]" if is_nickel else "")

            chip = MDChip(
                text=label,
                type="filter",
                active=False,
                on_active=lambda inst, val, f=food: self._toggle_food(f, val),
            )
            self.food_chips[food] = chip
            row.add_widget(chip)
        self.content.add_widget(food_flow)

    def _toggle_food(self, food: str, active: bool):
        if active:
            self.selected_foods.add(food)
        else:
            self.selected_foods.discard(food)

    # ── Trigger sections ────────────────────────────────────────────────────────

    def _build_trigger_sections(self):
        sm = self.settings_manager

        # Stress
        if sm.is_module_enabled("stress"):
            self.content.add_widget(
                MDLabel(text="😰 Stresslevel", font_style="Subtitle1", bold=True, adaptive_height=True)
            )
            row = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(8))
            self.stress_buttons = []
            for i in range(1, 6):
                btn = MDRaisedButton(
                    text=str(i),
                    size_hint=(None, None),
                    size=(dp(52), dp(52)),
                    md_bg_color=_hex_to_rgba("#E0E0E0"),
                    on_release=lambda _, s=i: self._set_stress(s),
                )
                btn._val = i
                self.stress_buttons.append(btn)
                row.add_widget(btn)
            self.content.add_widget(row)
            self.content.add_widget(MDLabel(
                text="1 = entspannt — 5 = extremer Stress",
                theme_text_color="Secondary", font_style="Caption", adaptive_height=True,
            ))
            self.content.add_widget(MDSeparator(height=dp(1)))

        # Fungal
        if sm.is_module_enabled("fungal"):
            self.content.add_widget(
                MDLabel(text="🍄 Zehenpilz (Mykose)", font_style="Subtitle1", bold=True, adaptive_height=True)
            )
            self.fungal_chip = MDChip(
                text="Zehenpilz aktuell aktiv",
                type="filter",
                active=False,
                on_active=lambda inst, val: setattr(self, "fungal_active", val),
            )
            self.content.add_widget(self.fungal_chip)
            self.content.add_widget(MDLabel(
                text="Zehenpilz kann Id-Reaktion an den Händen auslösen",
                theme_text_color="Secondary", font_style="Caption", adaptive_height=True,
            ))
            self.content.add_widget(MDSeparator(height=dp(1)))

        # Sleep
        if sm.is_module_enabled("sleep"):
            self.content.add_widget(
                MDLabel(text="😴 Schlafqualität", font_style="Subtitle1", bold=True, adaptive_height=True)
            )
            row = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(8))
            self.sleep_buttons = []
            for i in range(1, 6):
                btn = MDRaisedButton(
                    text=str(i),
                    size_hint=(None, None),
                    size=(dp(52), dp(52)),
                    md_bg_color=_hex_to_rgba("#E0E0E0"),
                    on_release=lambda _, s=i: self._set_sleep(s),
                )
                btn._val = i
                self.sleep_buttons.append(btn)
                row.add_widget(btn)
            self.content.add_widget(row)
            self.content.add_widget(MDLabel(
                text="1 = schlecht geschlafen — 5 = ausgezeichnet",
                theme_text_color="Secondary", font_style="Caption", adaptive_height=True,
            ))
            self.content.add_widget(MDSeparator(height=dp(1)))

        # Weather
        if sm.is_module_enabled("weather"):
            self.content.add_widget(
                MDLabel(text="🌤 Wetter / Umgebung", font_style="Subtitle1", bold=True, adaptive_height=True)
            )
            weather_flow = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(4))
            row = None
            for idx, opt in enumerate(WEATHER_OPTIONS):
                if idx % 2 == 0:
                    row = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(4))
                    weather_flow.add_widget(row)
                chip = MDChip(
                    text=opt,
                    type="filter",
                    active=False,
                    on_active=lambda inst, val, w=opt: self._toggle_weather(w, val),
                )
                self.weather_chips[opt] = chip
                row.add_widget(chip)
            self.content.add_widget(weather_flow)
            self.content.add_widget(MDSeparator(height=dp(1)))

        # Sweating
        if sm.is_module_enabled("sweating"):
            self.content.add_widget(
                MDLabel(text="💧 Schwitzen", font_style="Subtitle1", bold=True, adaptive_height=True)
            )
            self.sweating_chip = MDChip(
                text="Starkes Schwitzen heute",
                type="filter",
                active=False,
                on_active=lambda inst, val: setattr(self, "sweating_active", val),
            )
            self.content.add_widget(self.sweating_chip)
            self.content.add_widget(MDSeparator(height=dp(1)))

        # Contact
        if sm.is_module_enabled("contact"):
            self.content.add_widget(
                MDLabel(text="🧤 Kontaktexposition", font_style="Subtitle1", bold=True, adaptive_height=True)
            )
            contact_flow = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(4))
            row = None
            for idx, item in enumerate(CONTACT_SUGGESTIONS):
                if idx % 2 == 0:
                    row = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(4))
                    contact_flow.add_widget(row)
                chip = MDChip(
                    text=item,
                    type="filter",
                    active=False,
                    on_active=lambda inst, val, c=item: self._toggle_contact(c, val),
                )
                self.contact_chips[item] = chip
                row.add_widget(chip)
            self.content.add_widget(contact_flow)
            self.content.add_widget(MDSeparator(height=dp(1)))

    def _set_stress(self, level: int):
        self.current_stress = level
        self._update_button_group(self.stress_buttons, level)

    def _set_sleep(self, level: int):
        self.current_sleep = level
        self._update_button_group(self.sleep_buttons, level)

    def _update_button_group(self, buttons, current_val):
        for btn in buttons:
            i = btn._val
            if i == current_val:
                btn.md_bg_color = _hex_to_rgba("#2196F3")
                btn.text_color = [1, 1, 1, 1]
            else:
                btn.md_bg_color = _hex_to_rgba("#E0E0E0")
                btn.text_color = [0, 0, 0, 0.87]

    def _toggle_weather(self, weather: str, active: bool):
        if active:
            for w, chip in self.weather_chips.items():
                if w != weather and chip.active:
                    chip.active = False
            self.selected_weather = weather
        else:
            if self.selected_weather == weather:
                self.selected_weather = None

    def _toggle_contact(self, item: str, active: bool):
        if active:
            self.selected_contacts.add(item)
        else:
            self.selected_contacts.discard(item)

    # ── Notes section ───────────────────────────────────────────────────────────

    def _build_notes_section(self):
        self.content.add_widget(
            MDLabel(text="Notizen", font_style="Subtitle1", bold=True, adaptive_height=True)
        )
        self.skin_notes_input = MDTextField(
            hint_text="Hautzustand (z.B. Rötungen, Juckreiz...)",
            mode="rectangle",
            multiline=True,
            size_hint_y=None,
            height=dp(80),
        )
        self.content.add_widget(self.skin_notes_input)

        self.food_notes_input = MDTextField(
            hint_text="Ernährung (z.B. Menge, Zubereitung...)",
            mode="rectangle",
            multiline=True,
            size_hint_y=None,
            height=dp(80),
        )
        self.content.add_widget(self.food_notes_input)

    # ── Date navigation ─────────────────────────────────────────────────────────

    def _change_day(self, delta: int):
        self.current_date += timedelta(days=delta)
        self._load_date(self.current_date)

    def _load_date(self, d: date):
        self.current_date = d
        weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        months = [
            "Januar", "Februar", "März", "April", "Mai", "Juni",
            "Juli", "August", "September", "Oktober", "November", "Dezember",
        ]
        self.date_label.text = f"{d.day}. {months[d.month - 1]} {d.year}"
        self.weekday_label.text = weekdays[d.weekday()]

        entry = self.data_manager.get_entry(d)
        self._populate_from_entry(entry)

    def _populate_from_entry(self, entry: Optional[DayEntry]):
        # Reset all state
        self.current_severity = None
        self.current_stress = None
        self.current_sleep = None
        self.selected_foods.clear()
        self.selected_contacts.clear()
        self.fungal_active = False
        self.sweating_active = False
        self.selected_weather = None
        self.skin_notes_input.text = ""
        self.food_notes_input.text = ""

        # Reset chips
        for chip in self.food_chips.values():
            if chip.active:
                chip.active = False
        for chip in self.weather_chips.values():
            if chip.active:
                chip.active = False
        for chip in self.contact_chips.values():
            if chip.active:
                chip.active = False
        if hasattr(self, "fungal_chip") and self.fungal_chip.active:
            self.fungal_chip.active = False
        if hasattr(self, "sweating_chip") and self.sweating_chip.active:
            self.sweating_chip.active = False

        if entry:
            self.current_severity = entry.severity
            self.current_stress = entry.stress_level
            self.current_sleep = entry.sleep_quality
            self.selected_foods = set(entry.foods)
            self.selected_contacts = set(entry.contact_exposures or [])
            self.fungal_active = bool(entry.fungal_active)
            self.sweating_active = bool(entry.sweating)
            self.selected_weather = entry.weather
            self.skin_notes_input.text = entry.skin_notes or ""
            self.food_notes_input.text = entry.food_notes or ""

            # Activate food chips
            for food in entry.foods:
                if food in self.food_chips:
                    self.food_chips[food].active = True
            # Weather
            if entry.weather and entry.weather in self.weather_chips:
                self.weather_chips[entry.weather].active = True
            # Contact
            for c in (entry.contact_exposures or []):
                if c in self.contact_chips:
                    self.contact_chips[c].active = True
            if hasattr(self, "fungal_chip") and entry.fungal_active:
                self.fungal_chip.active = True
            if hasattr(self, "sweating_chip") and entry.sweating:
                self.sweating_chip.active = True

            self.delete_btn.opacity = 1
            self.delete_btn.disabled = False
        else:
            self.delete_btn.opacity = 0
            self.delete_btn.disabled = True

        self._update_severity_buttons()
        self._update_button_group(self.stress_buttons, self.current_stress)
        self._update_button_group(self.sleep_buttons, self.current_sleep)

    # ── Save / Delete ───────────────────────────────────────────────────────────

    def save_entry(self):
        if self.current_severity is None:
            Snackbar(text="Bitte wähle einen Hautzustand aus.").open()
            return

        entry = DayEntry(
            date=self.current_date.isoformat(),
            severity=self.current_severity,
            foods=sorted(self.selected_foods),
            skin_notes=self.skin_notes_input.text.strip(),
            food_notes=self.food_notes_input.text.strip(),
            stress_level=self.current_stress,
            fungal_active=self.fungal_active if hasattr(self, "fungal_chip") else None,
            sleep_quality=self.current_sleep,
            weather=self.selected_weather,
            sweating=self.sweating_active if hasattr(self, "sweating_chip") else None,
            contact_exposures=sorted(self.selected_contacts),
        )
        self.data_manager.add_or_update_entry(entry)

        self.delete_btn.opacity = 1
        self.delete_btn.disabled = False
        Snackbar(text="✓ Gespeichert").open()

    def delete_entry(self):
        if not self.data_manager.get_entry(self.current_date):
            return
        self.data_manager.delete_entry(self.current_date)
        self._populate_from_entry(None)
        Snackbar(text="✓ Eintrag gelöscht").open()

    # ── Refresh on tab switch ───────────────────────────────────────────────────

    def on_enter_screen(self):
        self._load_date(self.current_date)
