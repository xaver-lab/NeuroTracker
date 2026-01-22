"""
Statistics Dialog for Neuro-Tracker Application
Shows analysis and correlations between food and symptoms
"""

from datetime import date, timedelta
from typing import Dict, List, Tuple, Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QTableWidget, QTableWidgetItem,
    QFrame, QScrollArea, QComboBox, QHeaderView, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

from config import (
    SEVERITY_COLORS, COLOR_PRIMARY, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
    STATS_MIN_DAYS, CORRELATION_THRESHOLD
)
from models.data_manager import DataManager
from utils.statistics import StatisticsCalculator


class StatCard(QFrame):
    """A card widget for displaying a single statistic"""

    def __init__(self, title: str, value: str, subtitle: str = "", highlight: bool = False, parent=None):
        super().__init__(parent)
        self.setup_ui(title, value, subtitle, highlight)

    def setup_ui(self, title: str, value: str, subtitle: str, highlight: bool):
        """Initialize the UI"""
        bg_color = "#E3F2FD" if highlight else "white"
        border_color = COLOR_PRIMARY if highlight else "#E0E0E0"

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 12px;")

        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        value_label.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
            subtitle_label.setWordWrap(True)
            layout.addWidget(subtitle_label)


class StatisticsDialog(QDialog):
    """
    Dialog showing statistics and food correlations
    """

    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.stats_calculator = StatisticsCalculator(data_manager)

        self.setWindowTitle("Statistiken & Analyse")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.load_statistics()

    def setup_ui(self):
        """Initialize the UI components"""
        self.setStyleSheet("""
            QDialog {
                background-color: #FAFAFA;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Statistiken & Analyse")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY};")

        # Time range selector
        self.time_range = QComboBox()
        self.time_range.addItems([
            "Letzte 7 Tage",
            "Letzte 14 Tage",
            "Letzte 30 Tage",
            "Letzte 90 Tage",
            "Alle Daten"
        ])
        self.time_range.setCurrentIndex(2)  # Default to 30 days
        self.time_range.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                min-width: 150px;
            }
        """)
        self.time_range.currentIndexChanged.connect(self.load_statistics)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Zeitraum:"))
        header_layout.addWidget(self.time_range)

        layout.addLayout(header_layout)

        # Tab widget for different views
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                padding: 10px 20px;
                margin-right: 4px;
                background-color: #F5F5F5;
                border: 1px solid #E0E0E0;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
                margin-bottom: -1px;
            }
        """)

        # Overview tab
        self.overview_tab = QWidget()
        self.setup_overview_tab()
        self.tabs.addTab(self.overview_tab, "Übersicht")

        # Food analysis tab
        self.food_tab = QWidget()
        self.setup_food_tab()
        self.tabs.addTab(self.food_tab, "Lebensmittel-Analyse")

        # Trends tab
        self.trends_tab = QWidget()
        self.setup_trends_tab()
        self.tabs.addTab(self.trends_tab, "Trends")

        layout.addWidget(self.tabs)

        # Close button
        close_btn = QPushButton("Schließen")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_PRIMARY};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 30px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
            }}
        """)
        close_btn.clicked.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

    def setup_overview_tab(self):
        """Setup the overview tab"""
        layout = QVBoxLayout(self.overview_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Stats cards row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        self.total_entries_card = StatCard("Einträge gesamt", "0", "")
        self.avg_severity_card = StatCard("Durchschnittliche Schwere", "0.0", "", highlight=True)
        self.good_days_card = StatCard("Gute Tage", "0", "Schwere 1-2")
        self.bad_days_card = StatCard("Schlechte Tage", "0", "Schwere 4-5")

        cards_layout.addWidget(self.total_entries_card)
        cards_layout.addWidget(self.avg_severity_card)
        cards_layout.addWidget(self.good_days_card)
        cards_layout.addWidget(self.bad_days_card)

        layout.addLayout(cards_layout)

        # Severity distribution
        severity_frame = QFrame()
        severity_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        severity_layout = QVBoxLayout(severity_frame)
        severity_layout.setContentsMargins(16, 16, 16, 16)

        severity_title = QLabel("Verteilung der Hautzustände")
        severity_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        severity_layout.addWidget(severity_title)

        self.severity_bars_layout = QVBoxLayout()
        severity_layout.addLayout(self.severity_bars_layout)

        layout.addWidget(severity_frame)

        # Most common foods
        foods_frame = QFrame()
        foods_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        foods_layout = QVBoxLayout(foods_frame)
        foods_layout.setContentsMargins(16, 16, 16, 16)

        foods_title = QLabel("Häufigste Lebensmittel")
        foods_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        foods_layout.addWidget(foods_title)

        self.top_foods_layout = QVBoxLayout()
        foods_layout.addLayout(self.top_foods_layout)

        layout.addWidget(foods_frame)
        layout.addStretch()

    def setup_food_tab(self):
        """Setup the food analysis tab"""
        layout = QVBoxLayout(self.food_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Info text
        info_label = QLabel(
            "Diese Analyse zeigt, wie sich verschiedene Lebensmittel auf deinen Hautzustand auswirken könnten. "
            "Lebensmittel mit höherer durchschnittlicher Schwere könnten Trigger sein."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; padding: 10px; background-color: #FFF8E1; border-radius: 4px;")
        layout.addWidget(info_label)

        # Food correlation table
        self.food_table = QTableWidget()
        self.food_table.setColumnCount(4)
        self.food_table.setHorizontalHeaderLabels([
            "Lebensmittel", "Anzahl Tage", "Durchschnittliche Schwere", "Bewertung"
        ])
        self.food_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.food_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.food_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.food_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.food_table.setAlternatingRowColors(True)
        self.food_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                gridline-color: #F5F5F5;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #E0E0E0;
                font-weight: bold;
            }
        """)
        self.food_table.verticalHeader().setVisible(False)
        self.food_table.setSelectionBehavior(QTableWidget.SelectRows)

        layout.addWidget(self.food_table)

    def setup_trends_tab(self):
        """Setup the trends tab"""
        layout = QVBoxLayout(self.trends_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Weekly averages
        weekly_frame = QFrame()
        weekly_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        weekly_layout = QVBoxLayout(weekly_frame)
        weekly_layout.setContentsMargins(16, 16, 16, 16)

        weekly_title = QLabel("Wöchentliche Durchschnitte")
        weekly_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        weekly_layout.addWidget(weekly_title)

        self.weekly_table = QTableWidget()
        self.weekly_table.setColumnCount(3)
        self.weekly_table.setHorizontalHeaderLabels(["Woche", "Durchschnitt", "Trend"])
        self.weekly_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.weekly_table.verticalHeader().setVisible(False)
        self.weekly_table.setStyleSheet("""
            QTableWidget {
                border: none;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)
        weekly_layout.addWidget(self.weekly_table)

        layout.addWidget(weekly_frame)

        # Day of week analysis
        dow_frame = QFrame()
        dow_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
        """)
        dow_layout = QVBoxLayout(dow_frame)
        dow_layout.setContentsMargins(16, 16, 16, 16)

        dow_title = QLabel("Durchschnitt nach Wochentag")
        dow_title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        dow_layout.addWidget(dow_title)

        self.dow_bars_layout = QVBoxLayout()
        dow_layout.addLayout(self.dow_bars_layout)

        layout.addWidget(dow_frame)
        layout.addStretch()

    def get_selected_days(self) -> int:
        """Get the number of days for the selected time range"""
        index = self.time_range.currentIndex()
        days_map = {0: 7, 1: 14, 2: 30, 3: 90, 4: None}
        return days_map.get(index)

    def load_statistics(self):
        """Load and display statistics"""
        days = self.get_selected_days()
        stats = self.stats_calculator.calculate_all(days)

        # Update overview cards
        self.total_entries_card.findChild(QLabel).setText(str(stats['total_entries']))

        avg_label = self.avg_severity_card.findChildren(QLabel)[1]
        avg_label.setText(f"{stats['average_severity']:.1f}")

        good_label = self.good_days_card.findChildren(QLabel)[1]
        good_label.setText(str(stats['good_days']))

        bad_label = self.bad_days_card.findChildren(QLabel)[1]
        bad_label.setText(str(stats['bad_days']))

        # Update severity distribution
        self._update_severity_bars(stats['severity_distribution'])

        # Update top foods
        self._update_top_foods(stats['top_foods'])

        # Update food correlation table
        self._update_food_table(stats['food_correlations'])

        # Update weekly averages
        self._update_weekly_table(stats['weekly_averages'])

        # Update day of week analysis
        self._update_dow_bars(stats['day_of_week_averages'])

    def _update_severity_bars(self, distribution: Dict[int, int]):
        """Update the severity distribution bars"""
        # Clear existing
        while self.severity_bars_layout.count():
            item = self.severity_bars_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        total = sum(distribution.values()) or 1
        severity_labels = {
            1: "Sehr gut", 2: "Gut", 3: "Mittel", 4: "Schlecht", 5: "Sehr schlecht"
        }

        for severity in range(1, 6):
            count = distribution.get(severity, 0)
            percentage = (count / total) * 100

            row = QHBoxLayout()

            label = QLabel(f"{severity} - {severity_labels[severity]}")
            label.setFixedWidth(150)

            bar_container = QFrame()
            bar_container.setFixedHeight(24)
            bar_container.setStyleSheet("background-color: #F5F5F5; border-radius: 4px;")

            bar = QFrame(bar_container)
            bar.setFixedHeight(24)
            bar.setFixedWidth(int(percentage * 3))  # Scale factor
            bar.setStyleSheet(f"background-color: {SEVERITY_COLORS[severity]}; border-radius: 4px;")

            count_label = QLabel(f"{count} ({percentage:.0f}%)")
            count_label.setFixedWidth(80)
            count_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")

            row.addWidget(label)
            row.addWidget(bar_container, stretch=1)
            row.addWidget(count_label)

            self.severity_bars_layout.addLayout(row)

    def _update_top_foods(self, top_foods: List[Tuple[str, int]]):
        """Update the top foods list"""
        # Clear existing
        while self.top_foods_layout.count():
            item = self.top_foods_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not top_foods:
            empty = QLabel("Keine Daten verfügbar")
            empty.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY}; font-style: italic;")
            self.top_foods_layout.addWidget(empty)
            return

        max_count = top_foods[0][1] if top_foods else 1

        for food, count in top_foods[:10]:
            row = QHBoxLayout()

            name_label = QLabel(food)
            name_label.setFixedWidth(150)

            bar_width = int((count / max_count) * 200)
            bar = QFrame()
            bar.setFixedSize(bar_width, 20)
            bar.setStyleSheet(f"background-color: {COLOR_PRIMARY}; border-radius: 4px;")

            count_label = QLabel(f"{count}x")
            count_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")

            row.addWidget(name_label)
            row.addWidget(bar)
            row.addWidget(count_label)
            row.addStretch()

            self.top_foods_layout.addLayout(row)

    def _update_food_table(self, correlations: List[Dict]):
        """Update the food correlation table"""
        self.food_table.setRowCount(len(correlations))

        for row, data in enumerate(correlations):
            # Food name
            name_item = QTableWidgetItem(data['food'])
            self.food_table.setItem(row, 0, name_item)

            # Count
            count_item = QTableWidgetItem(str(data['count']))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.food_table.setItem(row, 1, count_item)

            # Average severity
            avg = data['average_severity']
            avg_item = QTableWidgetItem(f"{avg:.2f}")
            avg_item.setTextAlignment(Qt.AlignCenter)

            # Color based on severity
            if avg <= 2:
                avg_item.setForeground(QColor(COLOR_SUCCESS))
            elif avg >= 4:
                avg_item.setForeground(QColor(COLOR_DANGER))
            else:
                avg_item.setForeground(QColor(COLOR_WARNING))

            self.food_table.setItem(row, 2, avg_item)

            # Rating
            if avg <= 2:
                rating = "✓ Verträglich"
                color = COLOR_SUCCESS
            elif avg <= 3:
                rating = "○ Neutral"
                color = COLOR_WARNING
            else:
                rating = "⚠ Möglicher Trigger"
                color = COLOR_DANGER

            rating_item = QTableWidgetItem(rating)
            rating_item.setForeground(QColor(color))
            self.food_table.setItem(row, 3, rating_item)

    def _update_weekly_table(self, weekly_data: List[Dict]):
        """Update the weekly averages table"""
        self.weekly_table.setRowCount(len(weekly_data))

        prev_avg = None
        for row, data in enumerate(weekly_data):
            # Week label
            week_item = QTableWidgetItem(data['week_label'])
            self.weekly_table.setItem(row, 0, week_item)

            # Average
            avg = data['average']
            avg_item = QTableWidgetItem(f"{avg:.2f}")
            avg_item.setTextAlignment(Qt.AlignCenter)
            self.weekly_table.setItem(row, 1, avg_item)

            # Trend
            if prev_avg is not None:
                diff = avg - prev_avg
                if diff < -0.3:
                    trend = "↑ Besser"
                    color = COLOR_SUCCESS
                elif diff > 0.3:
                    trend = "↓ Schlechter"
                    color = COLOR_DANGER
                else:
                    trend = "→ Stabil"
                    color = COLOR_TEXT_SECONDARY
            else:
                trend = "-"
                color = COLOR_TEXT_SECONDARY

            trend_item = QTableWidgetItem(trend)
            trend_item.setForeground(QColor(color))
            trend_item.setTextAlignment(Qt.AlignCenter)
            self.weekly_table.setItem(row, 2, trend_item)

            prev_avg = avg

    def _update_dow_bars(self, dow_data: Dict[int, float]):
        """Update the day of week bars"""
        # Clear existing
        while self.dow_bars_layout.count():
            item = self.dow_bars_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        day_names = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

        for day_num, name in enumerate(day_names):
            avg = dow_data.get(day_num, 0)

            row = QHBoxLayout()

            label = QLabel(name)
            label.setFixedWidth(100)

            # Bar
            bar_width = int(avg * 40)  # Scale factor

            # Determine color based on average
            if avg <= 2:
                color = COLOR_SUCCESS
            elif avg <= 3:
                color = COLOR_WARNING
            else:
                color = COLOR_DANGER

            bar = QFrame()
            bar.setFixedSize(bar_width, 20)
            bar.setStyleSheet(f"background-color: {color}; border-radius: 4px;")

            value_label = QLabel(f"{avg:.1f}" if avg > 0 else "-")
            value_label.setStyleSheet(f"color: {COLOR_TEXT_SECONDARY};")

            row.addWidget(label)
            row.addWidget(bar)
            row.addWidget(value_label)
            row.addStretch()

            self.dow_bars_layout.addLayout(row)
