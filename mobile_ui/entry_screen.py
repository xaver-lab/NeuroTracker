"""
Entry Screen – daily symptom & food logging (replaces ui/entry_panel.py).
"""

from datetime import date, timedelta
from typing import Optional

from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, ListProperty

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.chip import MDChip, MDChipText
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.divider import MDDivider
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.dialog import (
    MDDialog, MDDialogHeadlineText, MDDialogSupportingText, MDDialogButtonContainer,
)

from config import (
    SEVERITY_COLORS, MIN_SEVERITY, MAX_SEVERITY,
    FOOD_EMOJIS, WEATHER_OPTIONS, CONTACT_SUGGESTIONS,
    NICKEL_RICH_FOODS, TRACKER_MODULES,
)
from models.day_entry import DayEntry


class EntryScreen(MDScreen):
    """Main screen for creating/editing a day entry."""

    current_date_str = StringProperty("")

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
        self.severity_buttons = []
        self.stress_buttons = []
        self.sleep_buttons = []
        self.food_chips = {}
        self.weather_chips = {}
        self.contact_chips = {}

        Clock.schedule_once(self._build_ui, 0)

    # ── Build UI ────────────────────────────────────────────────────────────────

    def _build_ui(self, *_):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        self.data_manager = app.data_manager
        self.food_manager = app.food_manager
        self.settings_manager = app.settings_manager

        root = MDBoxLayout(orientation="vertical")

        # Top bar
        top_bar = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            padding=[dp(16), dp(12), dp(16), dp(4)],
            spacing=dp(8),
        )
        self.prev_day_btn = MDIconButton(
            icon="chevron-left",
            on_release=lambda *_: self._change_day(-1),
        )
        self.next_day_btn = MDIconButton(
            icon="chevron-right",
            on_release=lambda *_: self._change_day(1),
        )
        self.date_label = MDLabel(
            text="",
            halign="center",
            font_style="Title",
            role="medium",
            adaptive_height=True,
        )
        self.weekday_label = MDLabel(
            text="",
            halign="center",
            theme_text_color="Secondary",
            adaptive_height=True,
        )
        date_col = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            size_hint_x=1,
        )
        date_col.add_widget(self.date_label)
        date_col.add_widget(self.weekday_label)

        top_bar.add_widget(self.prev_day_btn)
        top_bar.add_widget(date_col)
        top_bar.add_widget(self.next_day_btn)

        root.add_widget(top_bar)

        # Scrollable content
        scroll = MDScrollView()
        self.content = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            padding=[dp(16), dp(8), dp(16), dp(16)],
            spacing=dp(16),
        )

        # -- Severity section --
        self._build_severity_section()
        self.content.add_widget(MDDivider())

        # -- Food section --
        self._build_food_section()
        self.content.add_widget(MDDivider())

        # -- Trigger sections (modular) --
        self._build_trigger_sections()

        # -- Notes section --
        self._build_notes_section()

        scroll.add_widget(self.content)
        root.add_widget(scroll)

        # -- Action bar --
        action_bar = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            padding=[dp(16), dp(8), dp(16), dp(8)],
            spacing=dp(12),
        )
        save_btn = MDButton(
            MDButtonText(text="Speichern"),
            style="filled",
            on_release=lambda *_: self.save_entry(),
        )
        self.delete_btn = MDButton(
            MDButtonText(text="Löschen"),
            style="outlined",
            on_release=lambda *_: self.delete_entry(),
        )
        self.delete_btn.opacity = 0
        self.delete_btn.disabled = True
        action_bar.add_widget(save_btn)
        action_bar.add_widget(self.delete_btn)
        root.add_widget(action_bar)

        self.add_widget(root)
        self._load_date(self.current_date)

    # ── Severity ────────────────────────────────────────────────────────────────

    def _build_severity_section(self):
        self.content.add_widget(
            MDLabel(text="Hautzustand", font_style="Title", role="small", adaptive_height=True)
        )
        row = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            spacing=dp(8),
        )
        self.severity_buttons = []
        for i in range(1, 6):
            btn = MDButton(
                MDButtonText(text=str(i)),
                style="outlined",
                on_release=lambda _, s=i: self._set_severity(s),
                size_hint=(None, None),
                size=(dp(52), dp(52)),
            )
            self.severity_buttons.append(btn)
            row.add_widget(btn)
        self.content.add_widget(row)

        descs = "1 = sehr gut  —  5 = sehr schlecht"
        self.severity_desc = MDLabel(
            text=descs,
            theme_text_color="Secondary",
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
        for i, btn in enumerate(self.severity_buttons, start=1):
            color = SEVERITY_COLORS.get(i, "#9E9E9E")
            if i == self.current_severity:
                btn.style = "filled"
                btn.md_bg_color = color
            else:
                btn.style = "outlined"
                btn.md_bg_color = [0, 0, 0, 0]

    # ── Food chips ──────────────────────────────────────────────────────────────

    def _build_food_section(self):
        self.content.add_widget(
            MDLabel(text="Lebensmittel", font_style="Title", role="small", adaptive_height=True)
        )
        self.food_flow = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(4),
        )
        foods = self.food_manager.get_all_suggestions()
        row = None
        for idx, food in enumerate(foods):
            if idx % 3 == 0:
                row = MDBoxLayout(
                    orientation="horizontal",
                    adaptive_height=True,
                    spacing=dp(6),
                )
                self.food_flow.add_widget(row)
            emoji = FOOD_EMOJIS.get(food, "")
            is_nickel = food in NICKEL_RICH_FOODS
            label_text = f"{emoji} {food}" + (" [Ni]" if is_nickel else "")

            chip = MDChip(
                MDChipText(text=label_text),
                type="filter",
                on_active=lambda inst, val, f=food: self._toggle_food(f, val),
            )
            self.food_chips[food] = chip
            row.add_widget(chip)

        self.content.add_widget(self.food_flow)

    def _toggle_food(self, food: str, active: bool):
        if active:
            self.selected_foods.add(food)
        else:
            self.selected_foods.discard(food)

    # ── Trigger sections (modular) ──────────────────────────────────────────────

    def _build_trigger_sections(self):
        sm = self.settings_manager

        # Stress
        if sm.is_module_enabled("stress"):
            self.content.add_widget(
                MDLabel(text="😰 Stresslevel", font_style="Title", role="small", adaptive_height=True)
            )
            row = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(8))
            self.stress_buttons = []
            for i in range(1, 6):
                btn = MDButton(
                    MDButtonText(text=str(i)),
                    style="outlined",
                    on_release=lambda _, s=i: self._set_stress(s),
                    size_hint=(None, None),
                    size=(dp(52), dp(52)),
                )
                self.stress_buttons.append(btn)
                row.add_widget(btn)
            self.content.add_widget(row)
            self.content.add_widget(
                MDLabel(
                    text="1 = entspannt — 5 = extremer Stress",
                    theme_text_color="Secondary",
                    adaptive_height=True,
                )
            )
            self.content.add_widget(MDDivider())

        # Fungal
        if sm.is_module_enabled("fungal"):
            self.content.add_widget(
                MDLabel(text="🍄 Zehenpilz (Mykose)", font_style="Title", role="small", adaptive_height=True)
            )
            self.fungal_chip = MDChip(
                MDChipText(text="Zehenpilz aktuell aktiv"),
                type="filter",
                on_active=lambda inst, val: setattr(self, "fungal_active", val),
            )
            self.content.add_widget(self.fungal_chip)
            self.content.add_widget(
                MDLabel(
                    text="Zehenpilz kann Id-Reaktion an den Händen auslösen",
                    theme_text_color="Secondary",
                    adaptive_height=True,
                )
            )
            self.content.add_widget(MDDivider())

        # Sleep
        if sm.is_module_enabled("sleep"):
            self.content.add_widget(
                MDLabel(text="😴 Schlafqualität", font_style="Title", role="small", adaptive_height=True)
            )
            row = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(8))
            self.sleep_buttons = []
            for i in range(1, 6):
                btn = MDButton(
                    MDButtonText(text=str(i)),
                    style="outlined",
                    on_release=lambda _, s=i: self._set_sleep(s),
                    size_hint=(None, None),
                    size=(dp(52), dp(52)),
                )
                self.sleep_buttons.append(btn)
                row.add_widget(btn)
            self.content.add_widget(row)
            self.content.add_widget(
                MDLabel(
                    text="1 = schlecht geschlafen — 5 = ausgezeichnet",
                    theme_text_color="Secondary",
                    adaptive_height=True,
                )
            )
            self.content.add_widget(MDDivider())

        # Weather
        if sm.is_module_enabled("weather"):
            self.content.add_widget(
                MDLabel(text="🌤 Wetter / Umgebung", font_style="Title", role="small", adaptive_height=True)
            )
            weather_flow = MDBoxLayout(
                orientation="vertical",
                adaptive_height=True,
                spacing=dp(4),
            )
            row = None
            for idx, opt in enumerate(WEATHER_OPTIONS):
                if idx % 2 == 0:
                    row = MDBoxLayout(
                        orientation="horizontal",
                        adaptive_height=True,
                        spacing=dp(6),
                    )
                    weather_flow.add_widget(row)
                chip = MDChip(
                    MDChipText(text=opt),
                    type="filter",
                    on_active=lambda inst, val, w=opt: self._toggle_weather(w, val),
                )
                self.weather_chips[opt] = chip
                row.add_widget(chip)
            self.content.add_widget(weather_flow)
            self.content.add_widget(MDDivider())

        # Sweating
        if sm.is_module_enabled("sweating"):
            self.content.add_widget(
                MDLabel(text="💧 Schwitzen", font_style="Title", role="small", adaptive_height=True)
            )
            self.sweating_chip = MDChip(
                MDChipText(text="Starkes Schwitzen heute"),
                type="filter",
                on_active=lambda inst, val: setattr(self, "sweating_active", val),
            )
            self.content.add_widget(self.sweating_chip)
            self.content.add_widget(MDDivider())

        # Contact
        if sm.is_module_enabled("contact"):
            self.content.add_widget(
                MDLabel(text="🧤 Kontaktexposition", font_style="Title", role="small", adaptive_height=True)
            )
            contact_flow = MDBoxLayout(
                orientation="vertical",
                adaptive_height=True,
                spacing=dp(4),
            )
            row = None
            for idx, item in enumerate(CONTACT_SUGGESTIONS):
                if idx % 2 == 0:
                    row = MDBoxLayout(
                        orientation="horizontal",
                        adaptive_height=True,
                        spacing=dp(6),
                    )
                    contact_flow.add_widget(row)
                chip = MDChip(
                    MDChipText(text=item),
                    type="filter",
                    on_active=lambda inst, val, c=item: self._toggle_contact(c, val),
                )
                self.contact_chips[item] = chip
                row.add_widget(chip)
            self.content.add_widget(contact_flow)
            self.content.add_widget(MDDivider())

    def _set_stress(self, level: int):
        self.current_stress = level
        self._update_button_group(self.stress_buttons, level)

    def _set_sleep(self, level: int):
        self.current_sleep = level
        self._update_button_group(self.sleep_buttons, level)

    def _update_button_group(self, buttons, current_val):
        for i, btn in enumerate(buttons, start=1):
            if i == current_val:
                btn.style = "filled"
            else:
                btn.style = "outlined"

    def _toggle_weather(self, weather: str, active: bool):
        if active:
            # Deselect others (single-select behavior)
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

    # ── Notes ───────────────────────────────────────────────────────────────────

    def _build_notes_section(self):
        self.content.add_widget(
            MDLabel(text="Notizen", font_style="Title", role="small", adaptive_height=True)
        )
        self.skin_notes_input = MDTextField(
            mode="outlined",
            size_hint_y=None,
            height=dp(80),
            multiline=True,
        )
        self.skin_notes_input.hint_text = "Hautzustand (z.B. Rötungen, Juckreiz...)"
        self.content.add_widget(self.skin_notes_input)

        self.food_notes_input = MDTextField(
            mode="outlined",
            size_hint_y=None,
            height=dp(80),
            multiline=True,
        )
        self.food_notes_input.hint_text = "Ernährung (z.B. Menge, Zubereitung...)"
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
        # Reset fields
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
        if hasattr(self, "fungal_chip"):
            if self.fungal_chip.active:
                self.fungal_chip.active = False
        if hasattr(self, "sweating_chip"):
            if self.sweating_chip.active:
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

            # Activate trigger chips
            if entry.weather and entry.weather in self.weather_chips:
                self.weather_chips[entry.weather].active = True
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
            MDSnackbar(
                MDSnackbarText(text="Bitte wähle einen Hautzustand aus."),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.9,
            ).open()
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

        MDSnackbar(
            MDSnackbarText(text="✓ Gespeichert"),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
        ).open()

    def delete_entry(self):
        if not self.data_manager.get_entry(self.current_date):
            return

        self.data_manager.delete_entry(self.current_date)
        self._populate_from_entry(None)

        MDSnackbar(
            MDSnackbarText(text="✓ Eintrag gelöscht"),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.9,
        ).open()

    # ── Refresh on tab switch ───────────────────────────────────────────────────

    def on_enter_screen(self):
        self._load_date(self.current_date)
