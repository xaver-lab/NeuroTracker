"""
Calendar Screen – modern monthly calendar with color-coded days (KivyMD 1.2.0).
Redesigned with clean monthly view, severity indicators, and smooth navigation.
"""

from datetime import date, timedelta
from calendar import monthrange
from typing import Optional, Dict

from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle, Ellipse

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.behaviors import RectangularRippleBehavior

from config import (
    SEVERITY_COLORS, FIRST_DAY_OF_WEEK, FOOD_EMOJIS,
)


def _hex_to_rgba(hex_color: str) -> list:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255
    return [r, g, b, 1]


def _pastel(hex_color: str, factor: float = 0.25) -> list:
    """Return a soft pastel version of a hex color."""
    rgba = _hex_to_rgba(hex_color)
    return [rgba[0] * factor + (1 - factor),
            rgba[1] * factor + (1 - factor),
            rgba[2] * factor + (1 - factor), 1]


class DayCell(RectangularRippleBehavior, MDBoxLayout):
    """A single day cell in the monthly calendar grid."""

    def __init__(self, display_date: Optional[date], entry=None,
                 on_tap=None, is_today: bool = False, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint=(1 / 7, None),
            height=dp(68),
            padding=[dp(2), dp(4), dp(2), dp(2)],
            **kwargs,
        )
        self.display_date = display_date
        self.entry = entry
        self._on_tap = on_tap
        self._is_today = is_today

        if display_date is None:
            # Empty cell for padding
            return

        # Background color based on entry
        if entry and entry.severity:
            self.md_bg_color = _pastel(
                SEVERITY_COLORS.get(entry.severity, "#E0E0E0"), 0.15
            )
        else:
            self.md_bg_color = [0, 0, 0, 0]

        # Day number
        day_text = str(display_date.day)
        day_color = _hex_to_rgba("#1565C0") if is_today else [0.2, 0.2, 0.2, 1]
        day_font = "Subtitle1" if is_today else "Body2"

        day_label = MDLabel(
            text=day_text,
            halign="center",
            font_style=day_font,
            bold=is_today,
            adaptive_height=True,
            theme_text_color="Custom",
            text_color=day_color,
        )
        self.add_widget(day_label)

        # Severity dot indicator
        if entry and entry.severity:
            sev_color = SEVERITY_COLORS.get(entry.severity, "#9E9E9E")
            dot_row = MDBoxLayout(
                orientation="horizontal",
                adaptive_height=True,
                size_hint_y=None,
                height=dp(14),
            )
            # Centered severity number
            sev_label = MDLabel(
                text=str(entry.severity),
                halign="center",
                font_style="Caption",
                bold=True,
                adaptive_height=True,
                theme_text_color="Custom",
                text_color=_hex_to_rgba(sev_color),
            )
            dot_row.add_widget(sev_label)
            self.add_widget(dot_row)

            # Food emoji indicators (max 2)
            if entry.foods:
                emojis = [FOOD_EMOJIS.get(f, "") for f in entry.foods[:2] if FOOD_EMOJIS.get(f)]
                if emojis:
                    food_label = MDLabel(
                        text="".join(emojis),
                        halign="center",
                        font_style="Caption",
                        adaptive_height=True,
                        size_hint_y=None,
                        height=dp(16),
                    )
                    self.add_widget(food_label)
        else:
            # Empty indicator space
            spacer = MDBoxLayout(size_hint_y=None, height=dp(14))
            self.add_widget(spacer)

        # Today ring indicator
        if is_today:
            with self.canvas.before:
                Color(0.13, 0.59, 0.95, 0.15)
                self._today_bg = RoundedRectangle(
                    pos=self.pos, size=self.size, radius=[dp(8)]
                )
            self.bind(pos=self._update_today_bg, size=self._update_today_bg)

    def _update_today_bg(self, *_):
        if hasattr(self, '_today_bg'):
            self._today_bg.pos = self.pos
            self._today_bg.size = self.size

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and self.display_date and self._on_tap:
            self._on_tap(self.display_date, self.entry)
            return True
        return super().on_touch_up(touch)


class CalendarScreen(MDScreen):
    """Modern monthly calendar view with severity color coding."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        today = date.today()
        self.current_year = today.year
        self.current_month = today.month
        self.day_cells: Dict[date, DayCell] = {}
        Clock.schedule_once(self._build_ui, 0)

    def _build_ui(self, *_):
        from kivymd.app import MDApp
        self.data_manager = MDApp.get_running_app().data_manager

        root = MDBoxLayout(orientation="vertical")

        # ── Month navigation header ──────────────────────────────────────────
        header = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            padding=[dp(8), dp(12), dp(8), dp(4)],
        )

        prev_btn = MDIconButton(
            icon="chevron-left",
            on_release=lambda *_: self._go_previous_month(),
            theme_text_color="Custom",
            text_color=_hex_to_rgba("#424242"),
        )
        next_btn = MDIconButton(
            icon="chevron-right",
            on_release=lambda *_: self._go_next_month(),
            theme_text_color="Custom",
            text_color=_hex_to_rgba("#424242"),
        )
        today_btn = MDFlatButton(
            text="Heute",
            on_release=lambda *_: self._go_today(),
            theme_text_color="Custom",
            text_color=_hex_to_rgba("#1565C0"),
        )

        title_col = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            size_hint_x=1,
        )
        self.month_label = MDLabel(
            text="",
            halign="center",
            font_style="H6",
            bold=True,
            adaptive_height=True,
        )
        self.year_label = MDLabel(
            text="",
            halign="center",
            theme_text_color="Secondary",
            font_style="Caption",
            adaptive_height=True,
        )
        title_col.add_widget(self.month_label)
        title_col.add_widget(self.year_label)

        header.add_widget(prev_btn)
        header.add_widget(title_col)
        header.add_widget(today_btn)
        header.add_widget(next_btn)
        root.add_widget(header)

        # ── Weekday headers ──────────────────────────────────────────────────
        day_names_row = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            padding=[dp(4), dp(8), dp(4), dp(4)],
        )
        day_names = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        day_names = day_names[FIRST_DAY_OF_WEEK:] + day_names[:FIRST_DAY_OF_WEEK]
        for idx, name in enumerate(day_names):
            is_weekend = (idx + FIRST_DAY_OF_WEEK) % 7 >= 5
            lbl = MDLabel(
                text=name,
                halign="center",
                bold=True,
                font_style="Caption",
                adaptive_height=True,
                size_hint_x=1 / 7,
                theme_text_color="Custom",
                text_color=_hex_to_rgba("#9E9E9E") if is_weekend else _hex_to_rgba("#616161"),
            )
            day_names_row.add_widget(lbl)
        root.add_widget(day_names_row)

        # Thin separator
        root.add_widget(MDBoxLayout(
            size_hint_y=None, height=dp(1),
            md_bg_color=_hex_to_rgba("#E0E0E0"),
        ))

        # ── Calendar grid ────────────────────────────────────────────────────
        scroll = ScrollView()
        self.grid_container = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            padding=[dp(4), dp(4), dp(4), dp(4)],
            spacing=dp(2),
        )
        scroll.add_widget(self.grid_container)
        root.add_widget(scroll)

        # ── Legend ───────────────────────────────────────────────────────────
        legend = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            padding=[dp(16), dp(8), dp(16), dp(8)],
            spacing=dp(8),
        )
        severity_labels = {1: "Sehr gut", 2: "Gut", 3: "Mittel", 4: "Schlecht", 5: "S. schlecht"}
        for sev in [1, 3, 5]:
            dot = MDBoxLayout(
                orientation="horizontal",
                adaptive_height=True,
                spacing=dp(4),
                size_hint_x=1,
            )
            color_box = MDCard(
                size_hint=(None, None),
                size=(dp(12), dp(12)),
                md_bg_color=_hex_to_rgba(SEVERITY_COLORS[sev]),
                radius=[dp(6)],
                elevation=0,
            )
            dot.add_widget(color_box)
            dot.add_widget(MDLabel(
                text=severity_labels[sev],
                font_style="Caption",
                theme_text_color="Secondary",
                adaptive_height=True,
            ))
            legend.add_widget(dot)
        root.add_widget(legend)

        self.add_widget(root)
        self._rebuild_grid()

    def _rebuild_grid(self):
        self.grid_container.clear_widgets()
        self.day_cells.clear()
        self._update_title()

        today = date.today()
        year, month = self.current_year, self.current_month
        _, days_in_month = monthrange(year, month)

        # Calculate first day offset
        first_day = date(year, month, 1)
        first_weekday = (first_day.weekday() - FIRST_DAY_OF_WEEK) % 7

        # Load all entries for this month
        start = first_day
        end = date(year, month, days_in_month)
        entries = {}
        for entry in self.data_manager.get_all_entries():
            try:
                entry_date = date.fromisoformat(entry.date)
                if start <= entry_date <= end:
                    entries[entry_date] = entry
            except (ValueError, AttributeError):
                continue

        # Build week rows
        current_day = 1
        week_count = 0
        while current_day <= days_in_month:
            week_row = MDBoxLayout(
                orientation="horizontal",
                adaptive_height=True,
                spacing=dp(1),
            )

            for col in range(7):
                if (week_count == 0 and col < first_weekday) or current_day > days_in_month:
                    # Empty cell
                    cell = DayCell(display_date=None)
                    week_row.add_widget(cell)
                else:
                    d = date(year, month, current_day)
                    entry = entries.get(d)
                    is_today = d == today
                    cell = DayCell(
                        display_date=d,
                        entry=entry,
                        on_tap=self._on_day_tap,
                        is_today=is_today,
                    )
                    self.day_cells[d] = cell
                    week_row.add_widget(cell)
                    current_day += 1

            self.grid_container.add_widget(week_row)
            week_count += 1

    def _update_title(self):
        month_names = [
            "Januar", "Februar", "März", "April", "Mai", "Juni",
            "Juli", "August", "September", "Oktober", "November", "Dezember",
        ]
        self.month_label.text = month_names[self.current_month - 1]
        self.year_label.text = str(self.current_year)

    def _on_day_tap(self, tapped_date: date, entry):
        """Navigate to entry screen for the tapped date."""
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        bottom_nav = app.root.ids.bottom_nav
        entry_screen = app.root.ids.entry_screen

        entry_screen.current_date = tapped_date
        entry_screen._load_date(tapped_date)
        bottom_nav.switch_tab("entry")

    # ── Navigation ───────────────────────────────────────────────────────────

    def _go_previous_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self._rebuild_grid()

    def _go_next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self._rebuild_grid()

    def _go_today(self):
        today = date.today()
        self.current_year = today.year
        self.current_month = today.month
        self._rebuild_grid()

    def on_enter_screen(self):
        self._rebuild_grid()
