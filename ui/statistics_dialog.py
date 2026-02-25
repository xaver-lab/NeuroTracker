"""
Statistics Dialog for Neuro-Tracker Application
Shows analysis and correlations for all tracked trigger factors.
"""

from datetime import date, timedelta
from typing import Dict, List, Tuple, Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QTableWidget, QTableWidgetItem,
    QFrame, QScrollArea, QComboBox, QHeaderView, QSizePolicy,
    QSpinBox, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from config import (
    SEVERITY_COLORS, COLOR_PRIMARY, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
    STATS_MIN_DAYS, CORRELATION_THRESHOLD, TRACKER_MODULES,
)
from models.data_manager import DataManager
from utils.statistics import StatisticsCalculator


class StatCard(QFrame):
    """A card widget for displaying a single statistic"""

    def __init__(self, title: str, value: str, subtitle: str = "",
                 highlight: bool = False, parent=None):
        super().__init__(parent)
        self.setup_ui(title, value, subtitle, highlight)

    def setup_ui(self, title, value, subtitle, highlight):
        bg = "#E3F2FD" if highlight else "white"
        border = COLOR_PRIMARY if highlight else "#E0E0E0"
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: 8px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        self._title = QLabel(title)
        self._title.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 12px;")

        self._value = QLabel(value)
        self._value.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self._value.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")

        layout.addWidget(self._title)
        layout.addWidget(self._value)

        if subtitle:
            sub = QLabel(subtitle)
            sub.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
            sub.setWordWrap(True)
            layout.addWidget(sub)

    def set_value(self, v: str):
        self._value.setText(v)


class StatisticsDialog(QDialog):
    """Dialog showing statistics, trends, pattern detection and trigger analysis."""

    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.stats_calculator = StatisticsCalculator(data_manager)

        self.setWindowTitle("Statistiken & Analyse")
        self.setMinimumSize(900, 650)
        self.setup_ui()
        self.load_statistics()

    # ── Top-level UI ───────────────────────────────────────────────────────────

    def setup_ui(self):
        self.setStyleSheet("QDialog { background-color: #FAFAFA; }")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header row
        header = QHBoxLayout()
        title = QLabel("Statistiken & Analyse")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")

        self.time_range = QComboBox()
        self.time_range.addItems([
            "Letzte 7 Tage", "Letzte 14 Tage", "Letzte 30 Tage",
            "Letzte 90 Tage", "Alle Daten",
        ])
        self.time_range.setCurrentIndex(2)
        self.time_range.setStyleSheet("""
            QComboBox { padding: 8px 12px; border: 1px solid #E0E0E0;
                        border-radius: 4px; min-width: 150px; }
        """)
        self.time_range.currentIndexChanged.connect(self.load_statistics)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(QLabel("Zeitraum:"))
        header.addWidget(self.time_range)
        layout.addLayout(header)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E0E0E0; border-radius: 4px; background-color: white;
            }
            QTabBar::tab {
                padding: 10px 20px; margin-right: 4px;
                background-color: #F5F5F5;
                border: 1px solid #E0E0E0; border-bottom: none;
                border-top-left-radius: 4px; border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white; border-bottom: 1px solid white; margin-bottom: -1px;
            }
        """)

        self.overview_tab = QWidget()
        self.setup_overview_tab()
        self.tabs.addTab(self.overview_tab, "Übersicht")

        self.trends_tab = QWidget()
        self.setup_trends_tab()
        self.tabs.addTab(self.trends_tab, "Verlauf")

        self.patterns_tab = QWidget()
        self.setup_patterns_tab()
        self.tabs.addTab(self.patterns_tab, "Muster-Erkennung")

        self.trigger_tab = QWidget()
        self.setup_trigger_tab()
        self.tabs.addTab(self.trigger_tab, "Trigger-Analyse")

        layout.addWidget(self.tabs)

        close_btn = QPushButton("Schließen")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY}; color: white;
                border: none; border-radius: 4px;
                padding: 10px 30px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #1976D2; }}
        """)
        close_btn.clicked.connect(self.accept)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    # ── Overview Tab ───────────────────────────────────────────────────────────

    def setup_overview_tab(self):
        layout = QVBoxLayout(self.overview_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Primary stat cards
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)
        self.total_entries_card = StatCard("Einträge gesamt", "0")
        self.avg_severity_card  = StatCard("Durchschnittliche Schwere", "0.0", highlight=True)
        self.good_days_card     = StatCard("Gute Tage", "0", "Schwere 1-2")
        self.bad_days_card      = StatCard("Schlechte Tage", "0", "Schwere 4-5")
        for c in [self.total_entries_card, self.avg_severity_card,
                  self.good_days_card, self.bad_days_card]:
            cards_row.addWidget(c)
        layout.addLayout(cards_row)

        # Trigger summary cards (stress / fungal / sleep)
        trigger_row = QHBoxLayout()
        trigger_row.setSpacing(16)
        self.avg_stress_card  = StatCard("Ø Stresslevel", "—", "1-5")
        self.fungal_days_card = StatCard("Pilz-Tage", "—", "aktive Tage")
        self.avg_sleep_card   = StatCard("Ø Schlafqualität", "—", "1-5")
        for c in [self.avg_stress_card, self.fungal_days_card, self.avg_sleep_card]:
            trigger_row.addWidget(c)
        layout.addLayout(trigger_row)

        # Severity distribution
        sev_frame = self._card_frame("Verteilung der Hautzustände")
        self.severity_bars_layout = QVBoxLayout()
        sev_frame.layout().addLayout(self.severity_bars_layout)
        layout.addWidget(sev_frame)

        # Top foods
        food_frame = self._card_frame("Häufigste Lebensmittel")
        self.top_foods_layout = QVBoxLayout()
        food_frame.layout().addLayout(self.top_foods_layout)
        layout.addWidget(food_frame)
        layout.addStretch()

    # ── Trends Tab ─────────────────────────────────────────────────────────────

    def setup_trends_tab(self):
        layout = QVBoxLayout(self.trends_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        chart_frame = self._card_frame("Verlauf der Hautzustände")
        self.chart_container = QWidget()
        self.chart_layout = QHBoxLayout(self.chart_container)
        self.chart_layout.setContentsMargins(0, 20, 0, 40)
        self.chart_layout.setSpacing(2)
        self.chart_layout.setAlignment(Qt.AlignBottom | Qt.AlignLeft)

        chart_scroll = QScrollArea()
        chart_scroll.setWidget(self.chart_container)
        chart_scroll.setWidgetResizable(True)
        chart_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        chart_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        chart_scroll.setMinimumHeight(250)
        chart_scroll.setStyleSheet("QScrollArea { border: none; }")

        y_frame = QFrame()
        y_layout = QVBoxLayout(y_frame)
        y_layout.setContentsMargins(0, 0, 8, 40)
        y_layout.setSpacing(0)
        for i in range(5, 0, -1):
            lbl = QLabel(str(i))
            lbl.setFixedHeight(32)
            lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
            y_layout.addWidget(lbl)

        chart_with_axis = QHBoxLayout()
        chart_with_axis.addWidget(y_frame)
        chart_with_axis.addWidget(chart_scroll, stretch=1)
        chart_frame.layout().addLayout(chart_with_axis)
        layout.addWidget(chart_frame, stretch=1)

        # Day of week averages
        dow_frame = self._card_frame("Durchschnitt nach Wochentag")
        self.dow_bars_layout = QVBoxLayout()
        dow_frame.layout().addLayout(self.dow_bars_layout)
        layout.addWidget(dow_frame)

    # ── Pattern Detection Tab ──────────────────────────────────────────────────

    def setup_patterns_tab(self):
        layout = QVBoxLayout(self.patterns_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        info = QLabel(
            "Die Muster-Erkennung analysiert ALLE erfassten Trigger: Lebensmittel, Stress, "
            "Zehenpilz, Schlafqualität, Wetter, Schwitzen und Kontaktexposition. "
            "Je höher die Wahrscheinlichkeit, desto öfter folgte auf diesen Trigger ein schlechter Tag."
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; padding: 10px; "
            "background-color: #E8F5E9; border-radius: 4px;"
        )
        layout.addWidget(info)

        # Settings
        settings_frame = QFrame()
        settings_frame.setStyleSheet(
            "QFrame { background-color: white; border: 1px solid #E0E0E0; border-radius: 8px; }"
        )
        settings_layout = QHBoxLayout(settings_frame)
        settings_layout.setContentsMargins(16, 12, 16, 12)

        settings_layout.addWidget(QLabel("Zeitfenster (Tage nach Ereignis):"))
        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setRange(1, 5)
        self.delay_spinbox.setValue(2)
        self.delay_spinbox.setStyleSheet(
            "QSpinBox { padding: 6px 10px; border: 1px solid #E0E0E0; border-radius: 4px; min-width: 60px; }"
        )
        self.delay_spinbox.valueChanged.connect(self.update_patterns)
        settings_layout.addWidget(self.delay_spinbox)

        settings_layout.addSpacing(20)
        settings_layout.addWidget(QLabel("Schwellenwert (min. Schwere):"))
        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setRange(3, 5)
        self.threshold_spinbox.setValue(4)
        self.threshold_spinbox.setStyleSheet(
            "QSpinBox { padding: 6px 10px; border: 1px solid #E0E0E0; border-radius: 4px; min-width: 60px; }"
        )
        self.threshold_spinbox.valueChanged.connect(self.update_patterns)
        settings_layout.addWidget(self.threshold_spinbox)

        refresh_btn = QPushButton("Aktualisieren")
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY}; color: white;
                border: none; border-radius: 4px; padding: 6px 16px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #1976D2; }}
        """)
        refresh_btn.clicked.connect(self.update_patterns)
        settings_layout.addSpacing(20)
        settings_layout.addWidget(refresh_btn)
        settings_layout.addStretch()
        layout.addWidget(settings_frame)

        # Patterns table — 5 columns (with Trigger-Typ and Nickel-Flag)
        patterns_frame = self._card_frame("Erkannte Muster (alle Trigger)")
        self.patterns_table = QTableWidget()
        self.patterns_table.setColumnCount(5)
        self.patterns_table.setHorizontalHeaderLabels([
            "Trigger", "Typ", "Vorkommen", "Reaktionen", "Wahrscheinlichkeit"
        ])
        hdr = self.patterns_table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.Stretch)
        self.patterns_table.setAlternatingRowColors(True)
        self.patterns_table.setStyleSheet("""
            QTableWidget { border: none; gridline-color: #F5F5F5; }
            QTableWidget::item { padding: 8px; }
            QHeaderView::section {
                background-color: #F5F5F5; padding: 10px; border: none;
                border-bottom: 1px solid #E0E0E0; font-weight: bold;
            }
        """)
        self.patterns_table.verticalHeader().setVisible(False)
        self.patterns_table.setSelectionBehavior(QTableWidget.SelectRows)
        patterns_frame.layout().addWidget(self.patterns_table)
        layout.addWidget(patterns_frame, stretch=1)

    # ── Trigger Analysis Tab ───────────────────────────────────────────────────

    def setup_trigger_tab(self):
        layout = QVBoxLayout(self.trigger_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        inner = QWidget()
        self.trigger_inner_layout = QVBoxLayout(inner)
        self.trigger_inner_layout.setContentsMargins(0, 0, 0, 0)
        self.trigger_inner_layout.setSpacing(16)
        scroll.setWidget(inner)
        layout.addWidget(scroll)

        # Placeholder cards — filled in load_trigger_analysis()
        # Fungal
        self.fungal_frame = self._card_frame("🍄 Zehenpilz → Hautschub (Id-Reaktion)")
        self.fungal_layout = QVBoxLayout()
        self.fungal_frame.layout().addLayout(self.fungal_layout)
        self.trigger_inner_layout.addWidget(self.fungal_frame)

        # Stress
        self.stress_frame = self._card_frame("😰 Stresslevel → Hautzustand")
        self.stress_layout = QVBoxLayout()
        self.stress_frame.layout().addLayout(self.stress_layout)
        self.trigger_inner_layout.addWidget(self.stress_frame)

        # Sleep
        self.sleep_frame = self._card_frame("😴 Schlafqualität → Hautzustand")
        self.sleep_layout = QVBoxLayout()
        self.sleep_frame.layout().addLayout(self.sleep_layout)
        self.trigger_inner_layout.addWidget(self.sleep_frame)

        # Weather
        self.weather_frame = self._card_frame("🌤 Wetter → Ø Schweregrad")
        self.weather_layout = QVBoxLayout()
        self.weather_frame.layout().addLayout(self.weather_layout)
        self.trigger_inner_layout.addWidget(self.weather_frame)

        # Nickel
        self.nickel_frame = self._card_frame("⚗ Nickel-Analyse (Dyshidrosis-spezifisch)")
        self.nickel_layout = QVBoxLayout()
        self.nickel_frame.layout().addLayout(self.nickel_layout)
        self.trigger_inner_layout.addWidget(self.nickel_frame)

        self.trigger_inner_layout.addStretch()

    # ── Helper: create card frame with title ───────────────────────────────────

    def _card_frame(self, title: str) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame { background-color: white; border: 1px solid #E0E0E0; border-radius: 8px; }
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 16, 16, 16)
        if title:
            lbl = QLabel(title)
            lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
            layout.addWidget(lbl)
        return frame

    def _info_row(self, label: str, value: str, value_color: str = COLOR_TEXT_PRIMARY) -> QWidget:
        w = QWidget()
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 2, 0, 2)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 12px;")
        val = QLabel(value)
        val.setStyleSheet(f"color: {value_color}; font-size: 13px; font-weight: bold;")
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(val)
        return w

    def _no_data_label(self) -> QLabel:
        lbl = QLabel("Noch nicht genügend Daten — tracke mehr Tage um Muster zu erkennen.")
        lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-style: italic; padding: 4px 0;")
        lbl.setWordWrap(True)
        return lbl

    # ── Stats loading ──────────────────────────────────────────────────────────

    def get_selected_days(self) -> Optional[int]:
        return {0: 7, 1: 14, 2: 30, 3: 90, 4: None}.get(self.time_range.currentIndex())

    def load_statistics(self):
        days = self.get_selected_days()
        stats = self.stats_calculator.calculate_all(days)

        # Overview cards
        self.total_entries_card.set_value(str(stats['total_entries']))
        self.avg_severity_card.set_value(f"{stats['average_severity']:.1f}")
        self.good_days_card.set_value(str(stats['good_days']))
        self.bad_days_card.set_value(str(stats['bad_days']))

        avg_stress = stats.get('average_stress', 0)
        self.avg_stress_card.set_value(f"{avg_stress:.1f}" if avg_stress else "—")
        fungal_days = stats.get('fungal_days', 0)
        self.fungal_days_card.set_value(str(fungal_days) if fungal_days else "—")
        avg_sleep = stats.get('average_sleep', 0)
        self.avg_sleep_card.set_value(f"{avg_sleep:.1f}" if avg_sleep else "—")

        self._update_severity_bars(stats['severity_distribution'])
        self._update_top_foods(stats['top_foods'])
        self._update_chart()
        self._update_dow_bars(stats['day_of_week_averages'])
        self.update_patterns()
        self.load_trigger_analysis()

    # ── Pattern table (all triggers) ───────────────────────────────────────────

    def update_patterns(self):
        delay = self.delay_spinbox.value()
        threshold = self.threshold_spinbox.value()
        patterns = self.stats_calculator.detect_all_trigger_patterns(delay, threshold)

        type_labels = {
            'food':    '🍽 Nahrung',
            'stress':  '😰 Stress',
            'fungal':  '🍄 Pilz',
            'sleep':   '😴 Schlaf',
            'weather': '🌤 Wetter',
            'sweating':'💧 Schwitzen',
            'contact': '🧤 Kontakt',
        }

        self.patterns_table.setRowCount(len(patterns))
        for row, data in enumerate(patterns):
            # Trigger name (+ [Ni] marker for nickel-rich foods)
            name = data['trigger_label']
            if data.get('is_nickel_rich'):
                name += " [Ni]"
            name_item = QTableWidgetItem(name)
            if data.get('is_nickel_rich'):
                name_item.setForeground(QColor("#E65100"))
            self.patterns_table.setItem(row, 0, name_item)

            # Type
            type_item = QTableWidgetItem(type_labels.get(data['trigger_type'], data['trigger_type']))
            type_item.setTextAlignment(Qt.AlignCenter)
            self.patterns_table.setItem(row, 1, type_item)

            # Occurrences
            occ_item = QTableWidgetItem(str(data['total_occurrences']))
            occ_item.setTextAlignment(Qt.AlignCenter)
            self.patterns_table.setItem(row, 2, occ_item)

            # Reactions
            react_item = QTableWidgetItem(str(data['triggered_reactions']))
            react_item.setTextAlignment(Qt.AlignCenter)
            self.patterns_table.setItem(row, 3, react_item)

            # Probability with color
            prob = data['probability']
            if prob >= 50:
                color, icon = COLOR_DANGER, "⚠️"
            elif prob >= 25:
                color, icon = COLOR_WARNING, "⚡"
            else:
                color, icon = COLOR_SUCCESS, "✓"
            prob_item = QTableWidgetItem(f"{icon} {prob}%")
            prob_item.setForeground(QColor(color))
            prob_item.setTextAlignment(Qt.AlignCenter)
            self.patterns_table.setItem(row, 4, prob_item)

    # ── Trigger Analysis Tab content ───────────────────────────────────────────

    def load_trigger_analysis(self):
        self._load_fungal_analysis()
        self._load_stress_analysis()
        self._load_sleep_analysis()
        self._load_weather_analysis()
        self._load_nickel_analysis()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _load_fungal_analysis(self):
        self._clear_layout(self.fungal_layout)
        result = self.stats_calculator.detect_fungal_pattern()

        if result.get('insufficient_data'):
            self.fungal_layout.addWidget(self._no_data_label())
            return

        baseline = result['avg_baseline_severity']
        active   = result['avg_fungal_active_severity']
        onsets   = result['total_onsets']
        prob     = result['flare_probability']
        delay    = result['avg_peak_delay_days']

        color_active = COLOR_DANGER if active > baseline + 0.5 else COLOR_TEXT_PRIMARY
        self.fungal_layout.addWidget(self._info_row("Ø Schwere OHNE Pilz:", f"{baseline:.1f}"))
        self.fungal_layout.addWidget(self._info_row("Ø Schwere MIT Pilz:", f"{active:.1f}", color_active))
        self.fungal_layout.addWidget(self._info_row("Erkannte Pilz-Onsets:", str(onsets)))
        self.fungal_layout.addWidget(self._info_row(
            "Schub-Wahrscheinlichkeit nach Pilz-Onset:",
            f"{prob}%",
            COLOR_DANGER if prob >= 50 else COLOR_WARNING if prob >= 25 else COLOR_SUCCESS,
        ))
        if delay is not None:
            self.fungal_layout.addWidget(
                self._info_row("Ø Tage bis Schub-Peak:", f"{delay} Tage")
            )

        if active > baseline + 0.3:
            hint = QLabel(
                "⚠️  Deine Daten deuten auf eine Id-Reaktion hin: "
                "der Hautzustand ist bei aktivem Zehenpilz deutlich schlechter. "
                "Zeige diese Auswertung deinem Dermatologen."
            )
            hint.setWordWrap(True)
            hint.setStyleSheet(
                "color: #B71C1C; background: #FFEBEE; border-radius: 4px; padding: 8px; font-size: 12px;"
            )
            self.fungal_layout.addWidget(hint)

    def _load_stress_analysis(self):
        self._clear_layout(self.stress_layout)
        result = self.stats_calculator.detect_stress_pattern()

        sev_by_stress = result.get('stress_severity_by_level', {})
        if not sev_by_stress:
            self.stress_layout.addWidget(self._no_data_label())
            return

        stress_labels = {1: "Entspannt", 2: "Leicht", 3: "Mittel", 4: "Hoch", 5: "Extrem"}
        for level in sorted(sev_by_stress):
            avg = sev_by_stress[level]
            color = COLOR_DANGER if avg >= 4 else COLOR_WARNING if avg >= 3 else COLOR_TEXT_PRIMARY
            self.stress_layout.addWidget(
                self._info_row(f"Stress {level} ({stress_labels.get(level, '')}): Ø Schwere", f"{avg:.1f}", color)
            )

        prob = result.get('high_stress_flare_probability', 0)
        corr = result.get('correlation')
        self.stress_layout.addWidget(self._info_row(
            "Schub-Wahrscheinlichkeit bei Stress ≥4:",
            f"{prob}%",
            COLOR_DANGER if prob >= 50 else COLOR_WARNING if prob >= 25 else COLOR_SUCCESS,
        ))
        if corr is not None:
            strength = "stark" if abs(corr) > 0.6 else "moderat" if abs(corr) > 0.3 else "schwach"
            direction = "positiv (mehr Stress → mehr Schübe)" if corr > 0 else "negativ"
            self.stress_layout.addWidget(
                self._info_row(f"Korrelation ({strength}, {direction}):", f"r = {corr}")
            )

    def _load_sleep_analysis(self):
        self._clear_layout(self.sleep_layout)
        result = self.stats_calculator.get_sleep_analysis()

        same_day = result.get('same_day', {})
        next_day = result.get('next_day', {})
        if not same_day and not next_day:
            self.sleep_layout.addWidget(self._no_data_label())
            return

        if same_day:
            self.sleep_layout.addWidget(QLabel("Gleicher Tag:"))
            sleep_labels = {1: "Schlecht", 2: "Wenig", 3: "OK", 4: "Gut", 5: "Sehr gut"}
            for q in sorted(same_day):
                color = COLOR_SUCCESS if same_day[q] <= 2 else (COLOR_DANGER if same_day[q] >= 4 else COLOR_TEXT_PRIMARY)
                self.sleep_layout.addWidget(
                    self._info_row(f"  Schlaf {q} ({sleep_labels.get(q, '')}): Ø Schwere",
                                   f"{same_day[q]:.1f}", color)
                )

        corr = result.get('correlation')
        if corr is not None:
            direction = "negativ (schlechter Schlaf → mehr Schübe)" if corr < 0 else "positiv"
            self.sleep_layout.addWidget(
                self._info_row(f"Korrelation Schlaf↔Schwere ({direction}):", f"r = {corr}")
            )

    def _load_weather_analysis(self):
        self._clear_layout(self.weather_layout)
        data = self.stats_calculator.get_weather_analysis()
        if not data:
            self.weather_layout.addWidget(self._no_data_label())
            return

        sorted_weather = sorted(data.items(), key=lambda x: x[1], reverse=True)
        max_val = max(v for _, v in sorted_weather) or 1
        for weather, avg in sorted_weather:
            color = SEVERITY_COLORS.get(min(5, max(1, round(avg))), COLOR_TEXT_PRIMARY)
            row_w = QWidget()
            row = QHBoxLayout(row_w)
            row.setContentsMargins(0, 2, 0, 2)
            lbl = QLabel(weather)
            lbl.setFixedWidth(180)
            bar = QFrame()
            bar.setFixedSize(max(4, int(avg / max_val * 200)), 18)
            bar.setStyleSheet(f"background-color: {color}; border-radius: 3px;")
            val = QLabel(f"{avg:.1f}")
            val.setStyleSheet(f"color: {color}; font-weight: bold;")
            row.addWidget(lbl)
            row.addWidget(bar)
            row.addSpacing(8)
            row.addWidget(val)
            row.addStretch()
            self.weather_layout.addWidget(row_w)

    def _load_nickel_analysis(self):
        self._clear_layout(self.nickel_layout)
        result = self.stats_calculator.get_nickel_analysis()

        prob  = result.get('high_nickel_flare_probability', 0)
        foods = result.get('nickel_food_frequencies', {})
        by_load = result.get('avg_severity_by_nickel_load', {})

        if not foods and not by_load:
            hint = QLabel(
                "Keine nickelreichen Lebensmittel erfasst. "
                "Lebensmittel wie Schokolade, Haferflocken, Nüsse und Weizen sind nickelreich "
                "und können bei Nickel-sensiblen Patienten Dyshidrosis-Schübe auslösen."
            )
            hint.setWordWrap(True)
            hint.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-style: italic; padding: 4px 0;")
            self.nickel_layout.addWidget(hint)
            return

        self.nickel_layout.addWidget(
            self._info_row(
                "Schub-Wahrsch. bei ≥2 nickelreichen Lebensmitteln:",
                f"{prob}%",
                COLOR_DANGER if prob >= 50 else COLOR_WARNING if prob >= 25 else COLOR_SUCCESS,
            )
        )

        if by_load:
            self.nickel_layout.addWidget(QLabel("Ø Schwere nach Nickel-Last (Anzahl Lebensmittel):"))
            for load in sorted(by_load):
                color = SEVERITY_COLORS.get(min(5, max(1, round(by_load[load]))), COLOR_TEXT_PRIMARY)
                self.nickel_layout.addWidget(
                    self._info_row(f"  {load} nickelreiche{'s' if load == 1 else ''} Lebensmittel",
                                   f"Ø {by_load[load]:.1f}", color)
                )

        if foods:
            self.nickel_layout.addWidget(QLabel("Häufig konsumierte nickelreiche Lebensmittel:"))
            for food, cnt in list(foods.items())[:6]:
                self.nickel_layout.addWidget(
                    self._info_row(f"  {food}", f"{cnt}×", "#E65100")
                )

    # ── Overview helpers ───────────────────────────────────────────────────────

    def _update_severity_bars(self, distribution: Dict[int, int]):
        self._clear_layout(self.severity_bars_layout)
        total = sum(distribution.values()) or 1
        labels = {1: "Sehr gut", 2: "Gut", 3: "Mittel", 4: "Schlecht", 5: "Sehr schlecht"}
        for sev in range(1, 6):
            count = distribution.get(sev, 0)
            pct   = (count / total) * 100
            row_w = QWidget()
            row   = QHBoxLayout(row_w)
            row.setContentsMargins(0, 2, 0, 2)
            label = QLabel(f"{sev} - {labels[sev]}")
            label.setFixedWidth(130)
            label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 12px;")
            bar = QFrame()
            bar.setFixedHeight(20)
            bar.setFixedWidth(max(int(pct * 2.5), 4))
            bar.setStyleSheet(f"background-color: {SEVERITY_COLORS[sev]}; border-radius: 3px;")
            cnt_lbl = QLabel(f"{count} ({pct:.0f}%)")
            cnt_lbl.setFixedWidth(70)
            cnt_lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
            row.addWidget(label)
            row.addWidget(bar)
            row.addStretch()
            row.addWidget(cnt_lbl)
            self.severity_bars_layout.addWidget(row_w)

    def _update_top_foods(self, top_foods: List[Tuple[str, int]]):
        self._clear_layout(self.top_foods_layout)
        if not top_foods:
            self.top_foods_layout.addWidget(self._no_data_label())
            return
        max_count = top_foods[0][1] if top_foods else 1
        for food, count in top_foods[:10]:
            row_w = QWidget()
            row   = QHBoxLayout(row_w)
            row.setContentsMargins(0, 2, 0, 2)
            name = QLabel(food)
            name.setFixedWidth(130)
            name.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-size: 12px;")
            bar = QFrame()
            bar.setFixedSize(max(int((count / max_count) * 150), 4), 16)
            bar.setStyleSheet(f"background-color: {COLOR_PRIMARY}; border-radius: 3px;")
            cnt = QLabel(f"{count}×")
            cnt.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
            row.addWidget(name)
            row.addWidget(bar)
            row.addSpacing(8)
            row.addWidget(cnt)
            row.addStretch()
            self.top_foods_layout.addWidget(row_w)

    def _update_chart(self):
        while self.chart_layout.count():
            item = self.chart_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        days = self.get_selected_days()
        days = min(days if days is not None else 90, 60)
        end_date   = date.today()
        start_date = end_date - timedelta(days=days - 1)
        entries    = self.data_manager.get_entries_in_range(start_date, end_date)
        entry_map  = {date.fromisoformat(e.date): e for e in entries}
        bar_max    = 160

        current = start_date
        while current <= end_date:
            entry = entry_map.get(current)
            bar_w = QWidget()
            bar_l = QVBoxLayout(bar_w)
            bar_l.setContentsMargins(0, 0, 0, 0)
            bar_l.setSpacing(2)
            bar_l.setAlignment(Qt.AlignBottom)

            if entry and entry.severity:
                h = int((entry.severity / 5) * bar_max)
                color = SEVERITY_COLORS.get(entry.severity, "#9E9E9E")
                bar = QFrame()
                bar.setFixedSize(12, h)
                bar.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
                # Fungal marker on top
                if entry.fungal_active:
                    bar.setToolTip(
                        f"{current.strftime('%d.%m')}: Schwere {entry.severity} 🍄 Pilz aktiv"
                    )
                else:
                    bar.setToolTip(f"{current.strftime('%d.%m')}: Schwere {entry.severity}")
                bar_l.addWidget(bar, alignment=Qt.AlignHCenter)
            else:
                empty = QFrame()
                empty.setFixedSize(12, 4)
                empty.setStyleSheet("background-color: #E0E0E0; border-radius: 2px;")
                bar_l.addWidget(empty, alignment=Qt.AlignHCenter)

            if current == start_date or current == end_date or current.weekday() == 0:
                date_lbl = QLabel(current.strftime("%d.%m"))
                date_lbl.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 9px;")
                date_lbl.setAlignment(Qt.AlignCenter)
            else:
                date_lbl = QLabel("")
                date_lbl.setFixedHeight(14)
            bar_l.addWidget(date_lbl)
            bar_w.setFixedWidth(16)
            self.chart_layout.addWidget(bar_w)
            current += timedelta(days=1)
        self.chart_layout.addStretch()

    def _update_dow_bars(self, dow_data: Dict[int, float]):
        while self.dow_bars_layout.count():
            item = self.dow_bars_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        day_names = ["Montag", "Dienstag", "Mittwoch", "Donnerstag",
                     "Freitag", "Samstag", "Sonntag"]
        for day_num, name in enumerate(day_names):
            avg = dow_data.get(day_num, 0)
            row = QHBoxLayout()
            lbl = QLabel(name)
            lbl.setFixedWidth(100)
            color = (COLOR_SUCCESS if avg <= 2 else COLOR_WARNING if avg <= 3 else COLOR_DANGER)
            bar = QFrame()
            bar.setFixedSize(int(avg * 40), 20)
            bar.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
            val = QLabel(f"{avg:.1f}" if avg else "-")
            val.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")
            row.addWidget(lbl)
            row.addWidget(bar)
            row.addWidget(val)
            row.addStretch()
            self.dow_bars_layout.addLayout(row)
