"""
Calendar Screen – 2-week calendar view with color-coded day cards.
Replaces ui/calendar_widget.py + ui/day_card.py.
"""

from datetime import date, timedelta
from typing import Optional, Dict

from kivy.metrics import dp
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import MDGridLayout

from config import (
    SEVERITY_COLORS, WEEKS_TO_DISPLAY, FIRST_DAY_OF_WEEK,
    FOOD_EMOJIS,
)


class DayCardWidget(MDCard):
    """A single day card in the calendar grid."""

    def __init__(self, display_date: date, entry=None, on_tap=None, **kwargs):
        super().__init__(
            style="elevated",
            size_hint=(None, None),
            size=(dp(48), dp(90)),
            padding=[dp(4), dp(4), dp(4), dp(4)],
            **kwargs,
        )
        self.display_date = display_date
        self.entry = entry
        self._on_tap = on_tap
        self._is_today = display_date == date.today()

        self.orientation = "vertical"
        self.md_bg_color = self._card_bg_color()

        # Day number
        self.day_label = MDLabel(
            text=str(display_date.day),
            halign="center",
            font_style="Title",
            role="small",
            adaptive_height=True,
            bold=self._is_today,
        )
        if self._is_today:
            self.day_label.theme_text_color = "Custom"
            self.day_label.text_color = get_color_from_hex("#2196F3")
        self.add_widget(self.day_label)

        # Severity indicator
        self.severity_label = MDLabel(
            text="",
            halign="center",
            adaptive_height=True,
        )
        self.add_widget(self.severity_label)

        # Food emoji preview
        self.food_label = MDLabel(
            text="",
            halign="center",
            adaptive_height=True,
            font_style="Body",
            role="small",
        )
        self.add_widget(self.food_label)

        self._update_content()

        self.bind(on_release=self._handle_tap)

    def _handle_tap(self, *_):
        if self._on_tap:
            self._on_tap(self.display_date, self.entry)

    def _card_bg_color(self):
        if self.entry and self.entry.severity:
            hex_color = SEVERITY_COLORS.get(self.entry.severity, "#E0E0E0")
            rgba = get_color_from_hex(hex_color)
            # Make it lighter (pastel) for card background
            return [rgba[0] * 0.3 + 0.7, rgba[1] * 0.3 + 0.7, rgba[2] * 0.3 + 0.7, 1]
        return get_color_from_hex("#F5F5F5")

    def _update_content(self):
        if self.entry and self.entry.severity:
            self.severity_label.text = str(self.entry.severity)
            color = SEVERITY_COLORS.get(self.entry.severity, "#9E9E9E")
            self.severity_label.theme_text_color = "Custom"
            self.severity_label.text_color = get_color_from_hex(color)
            self.severity_label.bold = True

            if self.entry.foods:
                emojis = [FOOD_EMOJIS.get(f, "") for f in self.entry.foods[:3]]
                self.food_label.text = "".join(emojis)
        else:
            self.severity_label.text = "-"
            self.severity_label.theme_text_color = "Secondary"
            self.food_label.text = ""

    def set_entry(self, entry):
        self.entry = entry
        self.md_bg_color = self._card_bg_color()
        self._update_content()


class CalendarScreen(MDScreen):
    """2-week calendar grid view."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_start_date = self._calculate_start_date()
        self.day_cards: Dict[date, DayCardWidget] = {}
        Clock.schedule_once(self._build_ui, 0)

    def _calculate_start_date(self) -> date:
        today = date.today()
        days_since_week_start = (today.weekday() - FIRST_DAY_OF_WEEK) % 7
        week_start = today - timedelta(days=days_since_week_start)
        return week_start - timedelta(weeks=WEEKS_TO_DISPLAY - 1)

    def _build_ui(self, *_):
        from kivymd.app import MDApp
        self.data_manager = MDApp.get_running_app().data_manager

        root = MDBoxLayout(orientation="vertical")

        # Navigation header
        header = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            padding=[dp(8), dp(8), dp(8), dp(0)],
        )
        prev_btn = MDIconButton(
            icon="chevron-left",
            on_release=lambda *_: self._go_previous(),
        )
        self.title_label = MDLabel(
            text="",
            halign="center",
            font_style="Title",
            role="medium",
            adaptive_height=True,
        )
        today_btn = MDIconButton(
            icon="calendar-today",
            on_release=lambda *_: self._go_today(),
        )
        next_btn = MDIconButton(
            icon="chevron-right",
            on_release=lambda *_: self._go_next(),
        )
        header.add_widget(prev_btn)
        header.add_widget(self.title_label)
        header.add_widget(today_btn)
        header.add_widget(next_btn)
        root.add_widget(header)

        # Day name headers
        day_names_row = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            padding=[dp(4), dp(4), dp(4), dp(4)],
        )
        day_names = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        day_names = day_names[FIRST_DAY_OF_WEEK:] + day_names[:FIRST_DAY_OF_WEEK]
        for name in day_names:
            lbl = MDLabel(
                text=name,
                halign="center",
                theme_text_color="Secondary",
                adaptive_height=True,
                bold=True,
                size_hint_x=1,
            )
            day_names_row.add_widget(lbl)
        root.add_widget(day_names_row)

        # Calendar grid container
        scroll = MDScrollView()
        self.grid_container = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            padding=[dp(4), dp(4), dp(4), dp(4)],
            spacing=dp(6),
        )
        scroll.add_widget(self.grid_container)
        root.add_widget(scroll)

        self.add_widget(root)
        self._rebuild_grid()

    def _rebuild_grid(self):
        self.grid_container.clear_widgets()
        self.day_cards.clear()
        self._update_title()

        current_date = self.current_start_date
        for week in range(WEEKS_TO_DISPLAY):
            week_row = MDBoxLayout(
                orientation="horizontal",
                adaptive_height=True,
                spacing=dp(4),
            )
            for day in range(7):
                entry = self.data_manager.get_entry(current_date)
                card = DayCardWidget(
                    current_date,
                    entry=entry,
                    on_tap=self._on_card_tap,
                )
                self.day_cards[current_date] = card
                week_row.add_widget(card)
                current_date += timedelta(days=1)
            self.grid_container.add_widget(week_row)

    def _update_title(self):
        end_date = self.current_start_date + timedelta(weeks=WEEKS_TO_DISPLAY) - timedelta(days=1)
        month_names = [
            "Januar", "Februar", "März", "April", "Mai", "Juni",
            "Juli", "August", "September", "Oktober", "November", "Dezember",
        ]
        if self.current_start_date.month == end_date.month:
            title = (
                f"{self.current_start_date.day}. - {end_date.day}. "
                f"{month_names[end_date.month - 1]} {end_date.year}"
            )
        else:
            title = (
                f"{self.current_start_date.day}. {month_names[self.current_start_date.month - 1]} - "
                f"{end_date.day}. {month_names[end_date.month - 1]} {end_date.year}"
            )
        self.title_label.text = title

    def _on_card_tap(self, tapped_date: date, entry):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()

        if entry:
            # Navigate to day detail screen
            from mobile_ui.day_detail_screen import DayDetailScreen
            sm = app.root.ids.screen_manager

            # Remove previous detail screen if exists
            existing = sm.get_screen("day_detail") if sm.has_screen("day_detail") else None
            if existing:
                sm.remove_widget(existing)

            detail = DayDetailScreen(
                display_date=tapped_date,
                entry=entry,
                name="day_detail",
            )
            sm.add_widget(detail)
            sm.current = "day_detail"
        else:
            # Navigate to entry screen for this date
            sm = app.root.ids.screen_manager
            entry_screen = sm.get_screen("entry")
            entry_screen.current_date = tapped_date
            entry_screen._load_date(tapped_date)
            sm.current = "entry"

    # ── Navigation ──────────────────────────────────────────────────────────────

    def _go_previous(self):
        self.current_start_date -= timedelta(weeks=WEEKS_TO_DISPLAY)
        self._rebuild_grid()

    def _go_next(self):
        self.current_start_date += timedelta(weeks=WEEKS_TO_DISPLAY)
        self._rebuild_grid()

    def _go_today(self):
        self.current_start_date = self._calculate_start_date()
        self._rebuild_grid()

    def on_enter_screen(self):
        self._rebuild_grid()
