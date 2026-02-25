"""
Day Detail Screen – read-only detail view for a single day's entry.
Replaces ui/day_card.py DayDetailDialog.
"""

from datetime import date

from kivy.metrics import dp
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.divider import MDDivider
from kivymd.uix.chip import MDChip, MDChipText

from config import SEVERITY_COLORS, FOOD_EMOJIS
from models.day_entry import DayEntry


class DayDetailScreen(MDScreen):
    """Shows full details for a day entry (read-only)."""

    def __init__(self, display_date: date, entry: DayEntry, **kwargs):
        super().__init__(**kwargs)
        self.display_date = display_date
        self.entry = entry
        Clock.schedule_once(self._build_ui, 0)

    def _build_ui(self, *_):
        root = MDBoxLayout(orientation="vertical")

        # Top bar with back button
        top_bar = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            padding=[dp(4), dp(8), dp(16), dp(4)],
        )
        back_btn = MDIconButton(
            icon="arrow-left",
            on_release=lambda *_: self._go_back(),
        )
        edit_btn = MDIconButton(
            icon="pencil",
            on_release=lambda *_: self._go_edit(),
        )
        weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        title = MDLabel(
            text=f"{weekdays[self.display_date.weekday()]}, {self.display_date.strftime('%d.%m.%Y')}",
            font_style="Title",
            role="medium",
            adaptive_height=True,
        )
        top_bar.add_widget(back_btn)
        top_bar.add_widget(title)
        top_bar.add_widget(edit_btn)
        root.add_widget(top_bar)

        # Scrollable content
        scroll = MDScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            padding=[dp(16), dp(8), dp(16), dp(16)],
            spacing=dp(16),
        )

        if self.entry:
            # Severity card
            severity = self.entry.severity
            severity_texts = {
                1: "Sehr gut", 2: "Gut", 3: "Mittel", 4: "Schlecht", 5: "Sehr schlecht",
            }
            color_hex = SEVERITY_COLORS.get(severity, "#9E9E9E")
            color = get_color_from_hex(color_hex)

            sev_card = MDCard(
                style="filled",
                md_bg_color=[color[0] * 0.3 + 0.7, color[1] * 0.3 + 0.7, color[2] * 0.3 + 0.7, 1],
                padding=[dp(16), dp(12), dp(16), dp(12)],
                size_hint_y=None,
                height=dp(80),
            )
            sev_card.orientation = "vertical"
            sev_card.add_widget(MDLabel(
                text="Hautzustand",
                theme_text_color="Secondary",
                adaptive_height=True,
            ))
            sev_card.add_widget(MDLabel(
                text=f"{severity} — {severity_texts.get(severity, '')}",
                font_style="Headline",
                role="small",
                theme_text_color="Custom",
                text_color=color,
                adaptive_height=True,
                bold=True,
            ))
            content.add_widget(sev_card)

            # Skin notes
            if self.entry.skin_notes:
                content.add_widget(MDLabel(
                    text="Notizen Hautzustand",
                    font_style="Title",
                    role="small",
                    adaptive_height=True,
                ))
                content.add_widget(self._note_card(self.entry.skin_notes))

            # Foods
            if self.entry.foods:
                content.add_widget(MDLabel(
                    text="Lebensmittel",
                    font_style="Title",
                    role="small",
                    adaptive_height=True,
                ))
                food_flow = MDBoxLayout(
                    orientation="vertical",
                    adaptive_height=True,
                    spacing=dp(4),
                )
                row = None
                for idx, food in enumerate(self.entry.foods):
                    if idx % 3 == 0:
                        row = MDBoxLayout(
                            orientation="horizontal",
                            adaptive_height=True,
                            spacing=dp(6),
                        )
                        food_flow.add_widget(row)
                    emoji = FOOD_EMOJIS.get(food, "🍽")
                    chip = MDChip(
                        MDChipText(text=f"{emoji} {food}"),
                        type="assist",
                    )
                    row.add_widget(chip)
                content.add_widget(food_flow)

            # Food notes
            if self.entry.food_notes:
                content.add_widget(MDLabel(
                    text="Notizen Ernährung",
                    font_style="Title",
                    role="small",
                    adaptive_height=True,
                ))
                content.add_widget(self._note_card(self.entry.food_notes))

            content.add_widget(MDDivider())

            # Trigger details
            trigger_items = []
            if self.entry.stress_level is not None:
                trigger_items.append(f"😰 Stress: {self.entry.stress_level}/5")
            if self.entry.fungal_active:
                trigger_items.append("🍄 Zehenpilz aktiv")
            if self.entry.sleep_quality is not None:
                trigger_items.append(f"😴 Schlaf: {self.entry.sleep_quality}/5")
            if self.entry.weather:
                trigger_items.append(f"🌤 Wetter: {self.entry.weather}")
            if self.entry.sweating:
                trigger_items.append("💧 Starkes Schwitzen")
            if self.entry.contact_exposures:
                trigger_items.append(f"🧤 Kontakt: {', '.join(self.entry.contact_exposures)}")

            if trigger_items:
                content.add_widget(MDLabel(
                    text="Trigger",
                    font_style="Title",
                    role="small",
                    adaptive_height=True,
                ))
                for item_text in trigger_items:
                    content.add_widget(MDLabel(
                        text=item_text,
                        adaptive_height=True,
                    ))

            # Timestamps
            content.add_widget(MDDivider())
            content.add_widget(MDLabel(
                text=f"Erstellt: {self.entry.created_at[:16] if self.entry.created_at else '—'}",
                theme_text_color="Secondary",
                adaptive_height=True,
                font_style="Body",
                role="small",
            ))
            if self.entry.updated_at and self.entry.updated_at != self.entry.created_at:
                content.add_widget(MDLabel(
                    text=f"Aktualisiert: {self.entry.updated_at[:16]}",
                    theme_text_color="Secondary",
                    adaptive_height=True,
                    font_style="Body",
                    role="small",
                ))
        else:
            content.add_widget(MDLabel(
                text="Kein Eintrag für diesen Tag",
                theme_text_color="Secondary",
                halign="center",
                adaptive_height=True,
            ))

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def _note_card(self, text: str) -> MDCard:
        card = MDCard(
            style="outlined",
            padding=[dp(12), dp(8), dp(12), dp(8)],
            size_hint_y=None,
            height=dp(60),
        )
        card.orientation = "vertical"
        card.add_widget(MDLabel(
            text=text,
            adaptive_height=True,
        ))
        return card

    def _go_back(self):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        sm = app.root.ids.screen_manager
        sm.current = "calendar"

    def _go_edit(self):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        sm = app.root.ids.screen_manager
        entry_screen = sm.get_screen("entry")
        entry_screen.current_date = self.display_date
        entry_screen._load_date(self.display_date)
        sm.current = "entry"
