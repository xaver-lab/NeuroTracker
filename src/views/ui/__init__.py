"""
UI Components for Neuro-Tracker Application
"""

from views.ui.styles import (
    get_main_stylesheet,
    get_severity_button_style,
    get_day_card_style,
    get_panel_style,
    get_calendar_header_style,
    get_food_tag_style,
    get_statistics_card_style,
    get_empty_state_style,
    severity_to_color,
    get_contrast_text_color
)

from views.ui.day_card import DayCard, EmptyDayCard
from views.ui.calendar_widget import CalendarWidget
from views.ui.entry_panel import EntryPanel
from views.ui.statistics_dialog import StatisticsDialog, StatCard
from views.ui.main_window import MainWindow

__all__ = [
    # Styles
    'get_main_stylesheet',
    'get_severity_button_style',
    'get_day_card_style',
    'get_panel_style',
    'get_calendar_header_style',
    'get_food_tag_style',
    'get_statistics_card_style',
    'get_empty_state_style',
    'severity_to_color',
    'get_contrast_text_color',

    # Widgets
    'DayCard',
    'EmptyDayCard',
    'CalendarWidget',
    'EntryPanel',
    'StatisticsDialog',
    'StatCard',
    'MainWindow',
]
