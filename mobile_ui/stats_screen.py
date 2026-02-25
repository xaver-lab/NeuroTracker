"""
Statistics Screen – analysis, correlations, pattern detection (KivyMD 1.2.0).
Replaces ui/statistics_dialog.py.
Reuses utils/statistics.py (StatisticsCalculator) directly.
"""

from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard, MDSeparator
from kivymd.uix.chip import MDChip

from config import SEVERITY_COLORS, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER
from utils.statistics import StatisticsCalculator


def _hex_to_rgba(hex_color: str) -> list:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255
    return [r, g, b, 1]


class _StatCard(MDCard):
    """Small stat card with title and value."""

    def __init__(self, title: str, value: str, subtitle: str = "", **kwargs):
        super().__init__(
            orientation="vertical",
            padding=[dp(10), dp(8), dp(10), dp(8)],
            size_hint=(1, None),
            height=dp(85),
            radius=[dp(8)],
            elevation=2,
            **kwargs,
        )
        self.add_widget(MDLabel(
            text=title, theme_text_color="Secondary", font_style="Caption", adaptive_height=True,
        ))
        self._value_label = MDLabel(
            text=value, font_style="H6", bold=True, adaptive_height=True,
        )
        self.add_widget(self._value_label)
        if subtitle:
            self.add_widget(MDLabel(
                text=subtitle, theme_text_color="Secondary", font_style="Caption",
                adaptive_height=True,
            ))


class StatsScreen(MDScreen):
    """Statistics and pattern analysis screen."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._built = False
        self._selected_days = 30
        Clock.schedule_once(self._build_ui, 0)

    def _build_ui(self, *_):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        self.data_manager = app.data_manager
        self.stats_calculator = StatisticsCalculator(self.data_manager)

        root = MDBoxLayout(orientation="vertical")

        # Title
        title_bar = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            padding=[dp(16), dp(12), dp(16), dp(4)],
        )
        title_bar.add_widget(MDLabel(
            text="Statistiken & Analyse", font_style="H6", adaptive_height=True,
        ))
        root.add_widget(title_bar)

        # Time range chips
        range_row = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            padding=[dp(16), dp(0), dp(16), dp(8)],
            spacing=dp(6),
        )
        self._range_chips = {}
        for label, days in [("7 T", 7), ("14 T", 14), ("30 T", 30), ("90 T", 90), ("Alle", None)]:
            chip = MDChip(
                text=label,
                type="filter",
                active=(days == 30),
                on_active=lambda inst, val, d=days: self._on_range_selected(d, val),
            )
            self._range_chips[days] = chip
            range_row.add_widget(chip)
        root.add_widget(range_row)

        # Scrollable stats content
        scroll = ScrollView()
        self.stats_content = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            padding=[dp(16), dp(8), dp(16), dp(16)],
            spacing=dp(10),
        )
        scroll.add_widget(self.stats_content)
        root.add_widget(scroll)

        self.add_widget(root)
        self._built = True
        self._load_stats()

    def _on_range_selected(self, days, active):
        if active:
            for d, chip in self._range_chips.items():
                if d != days and chip.active:
                    chip.active = False
            self._selected_days = days
            self._load_stats()

    # ── Load & render stats ─────────────────────────────────────────────────────

    def _load_stats(self):
        if not self._built:
            return
        self.stats_content.clear_widgets()
        stats = self.stats_calculator.calculate_all(self._selected_days)

        # ── Overview ────────────────────────────────────────────────────────────
        self._section_header("Übersicht")

        row1 = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(8))
        row1.add_widget(_StatCard("Einträge", str(stats["total_entries"])))
        row1.add_widget(_StatCard("Ø Schwere", f"{stats['average_severity']:.1f}"))
        self.stats_content.add_widget(row1)

        row2 = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(8))
        row2.add_widget(_StatCard("Gute Tage", str(stats["good_days"]), "Schwere 1-2"))
        row2.add_widget(_StatCard("Schlechte Tage", str(stats["bad_days"]), "Schwere 4-5"))
        self.stats_content.add_widget(row2)

        row3 = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(8))
        avg_stress = stats.get("average_stress", 0)
        avg_sleep = stats.get("average_sleep", 0)
        fungal_days = stats.get("fungal_days", 0)
        row3.add_widget(_StatCard("Ø Stress", f"{avg_stress:.1f}" if avg_stress else "—"))
        row3.add_widget(_StatCard("Ø Schlaf", f"{avg_sleep:.1f}" if avg_sleep else "—"))
        row3.add_widget(_StatCard("Pilz-Tage", str(fungal_days) if fungal_days else "—"))
        self.stats_content.add_widget(row3)

        self.stats_content.add_widget(MDSeparator(height=dp(1)))

        # ── Severity distribution ───────────────────────────────────────────────
        self._section_header("Verteilung Hautzustand")
        dist = stats["severity_distribution"]
        total = sum(dist.values()) or 1
        severity_labels = {1: "Sehr gut", 2: "Gut", 3: "Mittel", 4: "Schlecht", 5: "Sehr schlecht"}
        for sev in range(1, 6):
            count = dist.get(sev, 0)
            pct = (count / total) * 100
            color_hex = SEVERITY_COLORS.get(sev, "#9E9E9E")
            self.stats_content.add_widget(
                self._bar_row(f"{sev} {severity_labels[sev]}", count, pct, color_hex)
            )
        self.stats_content.add_widget(MDSeparator(height=dp(1)))

        # ── Top foods ──────────────────────────────────────────────────────────
        top_foods = stats["top_foods"]
        if top_foods:
            self._section_header("Häufigste Lebensmittel")
            max_count = top_foods[0][1] if top_foods else 1
            for food, count in top_foods[:10]:
                pct = (count / max_count) * 100
                self.stats_content.add_widget(self._bar_row(food, count, pct, "#2196F3"))
            self.stats_content.add_widget(MDSeparator(height=dp(1)))

        # ── Pattern detection ───────────────────────────────────────────────────
        self._section_header("Muster-Erkennung (alle Trigger)")
        self.stats_content.add_widget(MDLabel(
            text="Zeitfenster: 2 Tage · Schwelle: Schwere ≥ 4",
            theme_text_color="Secondary", font_style="Caption", adaptive_height=True,
        ))

        patterns = self.stats_calculator.detect_all_trigger_patterns(delay_days=2, severity_threshold=4)
        if patterns:
            type_labels = {
                "food": "🍽 Nahrung", "stress": "😰 Stress", "fungal": "🍄 Pilz",
                "sleep": "😴 Schlaf", "weather": "🌤 Wetter",
                "sweating": "💧 Schwitzen", "contact": "🧤 Kontakt",
            }
            for p in patterns:
                prob = p["probability"]
                if prob >= 50:
                    color = COLOR_DANGER
                    icon = "⚠️"
                elif prob >= 25:
                    color = COLOR_WARNING
                    icon = "⚡"
                else:
                    color = COLOR_SUCCESS
                    icon = "✓"

                name = p["trigger_label"]
                if p.get("is_nickel_rich"):
                    name += " [Ni]"
                ttype = type_labels.get(p["trigger_type"], p["trigger_type"])

                row = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(4))
                row.add_widget(MDLabel(
                    text=name, adaptive_height=True, size_hint_x=0.4,
                ))
                row.add_widget(MDLabel(
                    text=ttype, theme_text_color="Secondary",
                    adaptive_height=True, size_hint_x=0.25, halign="center",
                ))
                row.add_widget(MDLabel(
                    text=f"{p['triggered_reactions']}/{p['total_occurrences']}",
                    theme_text_color="Secondary",
                    adaptive_height=True, size_hint_x=0.15, halign="center",
                ))
                prob_label = MDLabel(
                    text=f"{icon} {prob}%",
                    adaptive_height=True, size_hint_x=0.2, halign="right", bold=True,
                )
                prob_label.theme_text_color = "Custom"
                prob_label.text_color = _hex_to_rgba(color)
                row.add_widget(prob_label)
                self.stats_content.add_widget(row)
        else:
            self.stats_content.add_widget(MDLabel(
                text="Noch nicht genügend Daten — tracke mehr Tage.",
                theme_text_color="Secondary", adaptive_height=True,
            ))

        self.stats_content.add_widget(MDSeparator(height=dp(1)))

        # ── Detailed trigger analysis ───────────────────────────────────────────
        self._add_trigger_analysis()

    # ── Helpers ─────────────────────────────────────────────────────────────────

    def _section_header(self, text: str):
        self.stats_content.add_widget(MDLabel(
            text=text, font_style="Subtitle1", bold=True, adaptive_height=True,
        ))

    def _bar_row(self, label: str, count: int, pct: float, color_hex: str) -> MDBoxLayout:
        row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(28), spacing=dp(8))
        row.add_widget(MDLabel(text=label, size_hint_x=0.35, adaptive_height=True))

        bar_container = MDBoxLayout(size_hint_x=0.5, padding=[0, dp(4), 0, dp(4)])
        bar = MDCard(
            md_bg_color=_hex_to_rgba(color_hex),
            size_hint_x=max(pct / 100, 0.02),
            size_hint_y=1,
            radius=[dp(4)],
            elevation=0,
        )
        bar_container.add_widget(bar)

        row.add_widget(bar_container)
        row.add_widget(MDLabel(
            text=str(count), theme_text_color="Secondary",
            size_hint_x=0.15, adaptive_height=True, halign="right",
        ))
        return row

    def _info_row(self, label: str, value: str, color_hex: str = None) -> MDBoxLayout:
        row = MDBoxLayout(orientation="horizontal", adaptive_height=True)
        row.add_widget(MDLabel(
            text=label, theme_text_color="Secondary", adaptive_height=True, size_hint_x=0.65,
        ))
        val = MDLabel(
            text=value, adaptive_height=True, size_hint_x=0.35, halign="right", bold=True,
        )
        if color_hex:
            val.theme_text_color = "Custom"
            val.text_color = _hex_to_rgba(color_hex)
        row.add_widget(val)
        return row

    # ── Trigger analysis ────────────────────────────────────────────────────────

    def _add_trigger_analysis(self):
        self._section_header("Trigger-Analyse")

        # Fungal
        fungal = self.stats_calculator.detect_fungal_pattern()
        if not fungal.get("insufficient_data"):
            self.stats_content.add_widget(MDLabel(
                text="🍄 Zehenpilz → Hautschub", adaptive_height=True, bold=True,
            ))
            baseline = fungal["avg_baseline_severity"]
            active = fungal["avg_fungal_active_severity"]
            prob = fungal["flare_probability"]
            self.stats_content.add_widget(self._info_row("Ø Schwere OHNE Pilz", f"{baseline:.1f}"))
            self.stats_content.add_widget(self._info_row("Ø Schwere MIT Pilz", f"{active:.1f}"))
            self.stats_content.add_widget(self._info_row(
                "Schub-Wahrsch.",
                f"{prob}%",
                COLOR_DANGER if prob >= 50 else COLOR_WARNING if prob >= 25 else COLOR_SUCCESS,
            ))
            if fungal.get("avg_peak_delay_days") is not None:
                self.stats_content.add_widget(
                    self._info_row("Ø Tage bis Peak", f"{fungal['avg_peak_delay_days']} Tage")
                )
            self.stats_content.add_widget(MDSeparator(height=dp(1)))

        # Stress
        stress = self.stats_calculator.detect_stress_pattern()
        sev_by_stress = stress.get("stress_severity_by_level", {})
        if sev_by_stress:
            self.stats_content.add_widget(MDLabel(
                text="😰 Stress → Hautzustand", adaptive_height=True, bold=True,
            ))
            stress_names = {1: "Entspannt", 2: "Leicht", 3: "Mittel", 4: "Hoch", 5: "Extrem"}
            for level in sorted(sev_by_stress):
                avg = sev_by_stress[level]
                color = COLOR_DANGER if avg >= 4 else (COLOR_WARNING if avg >= 3 else None)
                self.stats_content.add_widget(self._info_row(
                    f"Stress {level} ({stress_names.get(level, '')})", f"Ø {avg:.1f}", color
                ))
            prob = stress.get("high_stress_flare_probability", 0)
            self.stats_content.add_widget(self._info_row(
                "Schub bei Stress ≥4", f"{prob}%",
                COLOR_DANGER if prob >= 50 else COLOR_WARNING if prob >= 25 else COLOR_SUCCESS,
            ))
            self.stats_content.add_widget(MDSeparator(height=dp(1)))

        # Sleep
        sleep = self.stats_calculator.get_sleep_analysis()
        same_day = sleep.get("same_day", {})
        if same_day:
            self.stats_content.add_widget(MDLabel(
                text="😴 Schlaf → Hautzustand", adaptive_height=True, bold=True,
            ))
            sleep_names = {1: "Schlecht", 2: "Wenig", 3: "OK", 4: "Gut", 5: "Sehr gut"}
            for q in sorted(same_day):
                avg = same_day[q]
                color = COLOR_SUCCESS if avg <= 2 else (COLOR_DANGER if avg >= 4 else None)
                self.stats_content.add_widget(self._info_row(
                    f"Schlaf {q} ({sleep_names.get(q, '')})", f"Ø {avg:.1f}", color
                ))
            self.stats_content.add_widget(MDSeparator(height=dp(1)))

        # Weather
        weather = self.stats_calculator.get_weather_analysis()
        if weather:
            self.stats_content.add_widget(MDLabel(
                text="🌤 Wetter → Ø Schwere", adaptive_height=True, bold=True,
            ))
            for w, avg in sorted(weather.items(), key=lambda x: x[1], reverse=True):
                sev_color = SEVERITY_COLORS.get(min(5, max(1, round(avg))), "#9E9E9E")
                self.stats_content.add_widget(self._info_row(w, f"{avg:.1f}", sev_color))
            self.stats_content.add_widget(MDSeparator(height=dp(1)))

        # Nickel
        nickel = self.stats_calculator.get_nickel_analysis()
        nickel_foods = nickel.get("nickel_food_frequencies", {})
        if nickel_foods:
            self.stats_content.add_widget(MDLabel(
                text="⚗ Nickel-Analyse", adaptive_height=True, bold=True,
            ))
            prob = nickel.get("high_nickel_flare_probability", 0)
            self.stats_content.add_widget(self._info_row(
                "Schub bei ≥2 Nickel-LM", f"{prob}%",
                COLOR_DANGER if prob >= 50 else COLOR_WARNING if prob >= 25 else COLOR_SUCCESS,
            ))
            for food, cnt in list(nickel_foods.items())[:6]:
                self.stats_content.add_widget(self._info_row(food, f"{cnt}×", "#E65100"))

    # ── Refresh on tab switch ───────────────────────────────────────────────────

    def on_enter_screen(self):
        self._load_stats()
