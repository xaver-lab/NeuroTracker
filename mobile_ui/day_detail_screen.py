"""
Day Detail Dialog – read-only detail view for a single day's entry (KivyMD 1.2.0).
Shown as a modal dialog from the calendar screen.
"""

from datetime import date

from kivy.metrics import dp

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard, MDSeparator
from kivymd.uix.chip import MDChip
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

from config import SEVERITY_COLORS, FOOD_EMOJIS
from models.day_entry import DayEntry


def _hex_to_rgba(hex_color: str) -> list:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255
    return [r, g, b, 1]


class DayDetailContent(MDBoxLayout):
    """Content widget for the day detail dialog."""

    def __init__(self, display_date: date, entry: DayEntry, **kwargs):
        super().__init__(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(8),
            padding=[dp(4), dp(4), dp(4), dp(4)],
            **kwargs,
        )
        self.display_date = display_date
        self.entry = entry
        self._build()

    def _build(self):
        if not self.entry:
            self.add_widget(MDLabel(
                text="Kein Eintrag für diesen Tag.",
                theme_text_color="Secondary",
                adaptive_height=True,
            ))
            return

        # Severity
        severity = self.entry.severity
        severity_texts = {
            1: "Sehr gut", 2: "Gut", 3: "Mittel", 4: "Schlecht", 5: "Sehr schlecht",
        }
        color_hex = SEVERITY_COLORS.get(severity, "#9E9E9E")
        sev_label = MDLabel(
            text=f"Hautzustand: {severity} — {severity_texts.get(severity, '')}",
            font_style="Subtitle1",
            bold=True,
            adaptive_height=True,
        )
        sev_label.theme_text_color = "Custom"
        sev_label.text_color = _hex_to_rgba(color_hex)
        self.add_widget(sev_label)

        # Skin notes
        if self.entry.skin_notes:
            self.add_widget(MDLabel(
                text="Notizen Hautzustand:", font_style="Subtitle2", bold=True, adaptive_height=True,
            ))
            self.add_widget(MDLabel(
                text=self.entry.skin_notes, adaptive_height=True,
            ))

        # Foods
        if self.entry.foods:
            self.add_widget(MDSeparator(height=dp(1)))
            self.add_widget(MDLabel(
                text="Lebensmittel:", font_style="Subtitle2", bold=True, adaptive_height=True,
            ))
            food_text = ", ".join(
                f"{FOOD_EMOJIS.get(f, '')} {f}" for f in self.entry.foods
            )
            self.add_widget(MDLabel(text=food_text, adaptive_height=True))

        # Food notes
        if self.entry.food_notes:
            self.add_widget(MDLabel(
                text="Notizen Ernährung:", font_style="Subtitle2", bold=True, adaptive_height=True,
            ))
            self.add_widget(MDLabel(text=self.entry.food_notes, adaptive_height=True))

        # Triggers
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
            self.add_widget(MDSeparator(height=dp(1)))
            self.add_widget(MDLabel(
                text="Trigger:", font_style="Subtitle2", bold=True, adaptive_height=True,
            ))
            for item_text in trigger_items:
                self.add_widget(MDLabel(text=item_text, adaptive_height=True))

        # Timestamps
        self.add_widget(MDSeparator(height=dp(1)))
        ts = self.entry.created_at[:16] if self.entry.created_at else "—"
        self.add_widget(MDLabel(
            text=f"Erstellt: {ts}",
            theme_text_color="Secondary", font_style="Caption", adaptive_height=True,
        ))


def show_day_detail(display_date: date, entry: DayEntry, on_edit=None):
    """Show a modal dialog with the day's details."""
    weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    title = f"{weekdays[display_date.weekday()]}, {display_date.strftime('%d.%m.%Y')}"

    content = DayDetailContent(display_date, entry)

    buttons = [MDFlatButton(text="Schließen")]
    if on_edit:
        buttons.append(MDFlatButton(
            text="Bearbeiten",
            theme_text_color="Custom",
            text_color=_hex_to_rgba("#2196F3"),
        ))

    dialog = MDDialog(
        title=title,
        type="custom",
        content_cls=content,
        buttons=buttons,
    )

    def _close(*_):
        dialog.dismiss()

    def _edit(*_):
        dialog.dismiss()
        if on_edit:
            on_edit(display_date)

    buttons[0].bind(on_release=_close)
    if len(buttons) > 1:
        buttons[1].bind(on_release=_edit)

    dialog.open()
    return dialog
