"""
Stylesheet definitions for Neuro-Tracker Application
Uses QSS (Qt Style Sheets) for consistent styling
"""

from config import (
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
    COLOR_BACKGROUND, COLOR_SURFACE, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    SEVERITY_COLORS
)


def get_main_stylesheet():
    """Returns the main application stylesheet"""
    return f"""
        /* Main Window */
        QMainWindow {{
            background-color: {COLOR_BACKGROUND};
        }}

        /* General Widget Styling */
        QWidget {{
            font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
            font-size: 14px;
            color: {COLOR_TEXT_PRIMARY};
        }}

        /* Labels */
        QLabel {{
            color: {COLOR_TEXT_PRIMARY};
        }}

        QLabel.heading {{
            font-size: 24px;
            font-weight: bold;
            color: {COLOR_PRIMARY};
        }}

        QLabel.subheading {{
            font-size: 18px;
            font-weight: 500;
            color: {COLOR_TEXT_PRIMARY};
        }}

        QLabel.caption {{
            font-size: 12px;
            color: {COLOR_TEXT_SECONDARY};
        }}

        /* Push Buttons */
        QPushButton {{
            background-color: {COLOR_PRIMARY};
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: 500;
            min-height: 36px;
        }}

        QPushButton:hover {{
            background-color: #1976D2;
        }}

        QPushButton:pressed {{
            background-color: #1565C0;
        }}

        QPushButton:disabled {{
            background-color: #BDBDBD;
            color: #757575;
        }}

        QPushButton.secondary {{
            background-color: {COLOR_SURFACE};
            color: {COLOR_PRIMARY};
            border: 1px solid {COLOR_PRIMARY};
        }}

        QPushButton.secondary:hover {{
            background-color: #E3F2FD;
        }}

        QPushButton.danger {{
            background-color: {COLOR_DANGER};
        }}

        QPushButton.danger:hover {{
            background-color: #D32F2F;
        }}

        QPushButton.success {{
            background-color: {COLOR_SUCCESS};
        }}

        QPushButton.success:hover {{
            background-color: #388E3C;
        }}

        /* Line Edit */
        QLineEdit {{
            background-color: {COLOR_SURFACE};
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 8px 12px;
            min-height: 20px;
        }}

        QLineEdit:focus {{
            border: 2px solid {COLOR_PRIMARY};
        }}

        QLineEdit:disabled {{
            background-color: #F5F5F5;
            color: {COLOR_TEXT_SECONDARY};
        }}

        /* Text Edit */
        QTextEdit, QPlainTextEdit {{
            background-color: {COLOR_SURFACE};
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 8px;
        }}

        QTextEdit:focus, QPlainTextEdit:focus {{
            border: 2px solid {COLOR_PRIMARY};
        }}

        /* Combo Box */
        QComboBox {{
            background-color: {COLOR_SURFACE};
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 8px 12px;
            min-height: 20px;
        }}

        QComboBox:focus {{
            border: 2px solid {COLOR_PRIMARY};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}

        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {COLOR_TEXT_SECONDARY};
            margin-right: 10px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {COLOR_SURFACE};
            border: 1px solid #E0E0E0;
            selection-background-color: #E3F2FD;
            selection-color: {COLOR_TEXT_PRIMARY};
        }}

        /* Spin Box */
        QSpinBox {{
            background-color: {COLOR_SURFACE};
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 8px 12px;
            min-height: 20px;
        }}

        QSpinBox:focus {{
            border: 2px solid {COLOR_PRIMARY};
        }}

        /* Slider */
        QSlider::groove:horizontal {{
            border: none;
            height: 8px;
            background: #E0E0E0;
            border-radius: 4px;
        }}

        QSlider::handle:horizontal {{
            background: {COLOR_PRIMARY};
            border: none;
            width: 20px;
            height: 20px;
            margin: -6px 0;
            border-radius: 10px;
        }}

        QSlider::handle:horizontal:hover {{
            background: #1976D2;
        }}

        /* Scroll Area */
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}

        QScrollBar:vertical {{
            border: none;
            background: #F5F5F5;
            width: 10px;
            border-radius: 5px;
        }}

        QScrollBar::handle:vertical {{
            background: #BDBDBD;
            min-height: 30px;
            border-radius: 5px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: #9E9E9E;
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        QScrollBar:horizontal {{
            border: none;
            background: #F5F5F5;
            height: 10px;
            border-radius: 5px;
        }}

        QScrollBar::handle:horizontal {{
            background: #BDBDBD;
            min-width: 30px;
            border-radius: 5px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: #9E9E9E;
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}

        /* Frame / Card */
        QFrame.card {{
            background-color: {COLOR_SURFACE};
            border: 1px solid #E0E0E0;
            border-radius: 8px;
        }}

        QFrame.card:hover {{
            border: 1px solid {COLOR_PRIMARY};
        }}

        /* Group Box */
        QGroupBox {{
            font-weight: bold;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            color: {COLOR_TEXT_PRIMARY};
        }}

        /* Tab Widget */
        QTabWidget::pane {{
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            background-color: {COLOR_SURFACE};
        }}

        QTabBar::tab {{
            background-color: #F5F5F5;
            border: 1px solid #E0E0E0;
            padding: 8px 16px;
            margin-right: 2px;
        }}

        QTabBar::tab:selected {{
            background-color: {COLOR_SURFACE};
            border-bottom-color: {COLOR_SURFACE};
        }}

        QTabBar::tab:hover:!selected {{
            background-color: #E0E0E0;
        }}

        /* List Widget */
        QListWidget {{
            background-color: {COLOR_SURFACE};
            border: 1px solid #E0E0E0;
            border-radius: 4px;
        }}

        QListWidget::item {{
            padding: 8px;
            border-bottom: 1px solid #F5F5F5;
        }}

        QListWidget::item:selected {{
            background-color: #E3F2FD;
            color: {COLOR_TEXT_PRIMARY};
        }}

        QListWidget::item:hover {{
            background-color: #F5F5F5;
        }}

        /* Menu Bar */
        QMenuBar {{
            background-color: {COLOR_SURFACE};
            border-bottom: 1px solid #E0E0E0;
        }}

        QMenuBar::item {{
            padding: 8px 12px;
        }}

        QMenuBar::item:selected {{
            background-color: #E3F2FD;
        }}

        QMenu {{
            background-color: {COLOR_SURFACE};
            border: 1px solid #E0E0E0;
        }}

        QMenu::item {{
            padding: 8px 24px;
        }}

        QMenu::item:selected {{
            background-color: #E3F2FD;
        }}

        /* Status Bar */
        QStatusBar {{
            background-color: {COLOR_SURFACE};
            border-top: 1px solid #E0E0E0;
        }}

        /* Tool Tip */
        QToolTip {{
            background-color: #424242;
            color: white;
            border: none;
            padding: 8px;
            border-radius: 4px;
        }}

        /* Dialog */
        QDialog {{
            background-color: {COLOR_BACKGROUND};
        }}

        /* Progress Bar */
        QProgressBar {{
            border: none;
            border-radius: 4px;
            background-color: #E0E0E0;
            height: 8px;
            text-align: center;
        }}

        QProgressBar::chunk {{
            background-color: {COLOR_PRIMARY};
            border-radius: 4px;
        }}

        /* Check Box */
        QCheckBox {{
            spacing: 8px;
        }}

        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
            border: 2px solid #9E9E9E;
        }}

        QCheckBox::indicator:checked {{
            background-color: {COLOR_PRIMARY};
            border-color: {COLOR_PRIMARY};
        }}

        QCheckBox::indicator:hover {{
            border-color: {COLOR_PRIMARY};
        }}
    """


def get_severity_button_style(severity: int, is_selected: bool = False) -> str:
    """Returns the style for a severity button"""
    color = SEVERITY_COLORS.get(severity, "#9E9E9E")

    if is_selected:
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: 2px solid {color};
                border-radius: 50%;
                font-weight: bold;
                min-width: 40px;
                max-width: 40px;
                min-height: 40px;
                max-height: 40px;
            }}
        """
    else:
        return f"""
            QPushButton {{
                background-color: white;
                color: {color};
                border: 2px solid {color};
                border-radius: 50%;
                font-weight: bold;
                min-width: 40px;
                max-width: 40px;
                min-height: 40px;
                max-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {color}20;
            }}
        """


def get_day_card_style(severity: int = None, is_today: bool = False, is_selected: bool = False) -> str:
    """Returns the style for a day card"""
    base_color = SEVERITY_COLORS.get(severity, "#E0E0E0") if severity else "#E0E0E0"

    border_color = COLOR_PRIMARY if is_selected else ("#424242" if is_today else "#E0E0E0")
    border_width = "3px" if is_selected or is_today else "1px"

    return f"""
        QFrame {{
            background-color: {COLOR_SURFACE};
            border: {border_width} solid {border_color};
            border-radius: 8px;
            border-left: 4px solid {base_color};
        }}
        QFrame:hover {{
            border-color: {COLOR_PRIMARY};
            background-color: #FAFAFA;
        }}
    """


def get_panel_style():
    """Returns the style for side panels"""
    return f"""
        QFrame {{
            background-color: {COLOR_SURFACE};
            border: none;
            border-right: 1px solid #E0E0E0;
        }}
    """


def get_calendar_header_style():
    """Returns the style for calendar headers"""
    return f"""
        QLabel {{
            font-size: 16px;
            font-weight: bold;
            color: {COLOR_TEXT_PRIMARY};
            padding: 8px;
        }}
    """


def get_food_tag_style(is_removable: bool = True) -> str:
    """Returns the style for food tags/chips"""
    return f"""
        QFrame {{
            background-color: #E3F2FD;
            border: 1px solid {COLOR_PRIMARY};
            border-radius: 16px;
            padding: 4px 8px;
        }}
        QLabel {{
            color: {COLOR_PRIMARY};
            font-size: 13px;
        }}
        QPushButton {{
            background-color: transparent;
            border: none;
            color: {COLOR_PRIMARY};
            font-weight: bold;
            min-width: 20px;
            max-width: 20px;
            min-height: 20px;
            max-height: 20px;
        }}
        QPushButton:hover {{
            color: {COLOR_DANGER};
        }}
    """


def get_statistics_card_style(highlight: bool = False) -> str:
    """Returns the style for statistics cards"""
    bg_color = "#E3F2FD" if highlight else COLOR_SURFACE
    border_color = COLOR_PRIMARY if highlight else "#E0E0E0"

    return f"""
        QFrame {{
            background-color: {bg_color};
            border: 1px solid {border_color};
            border-radius: 8px;
            padding: 16px;
        }}
    """


def get_empty_state_style():
    """Returns the style for empty state messages"""
    return f"""
        QLabel {{
            color: {COLOR_TEXT_SECONDARY};
            font-size: 16px;
            padding: 32px;
        }}
    """


# Color utility functions
def severity_to_color(severity: int) -> str:
    """Convert severity level to color"""
    return SEVERITY_COLORS.get(severity, "#9E9E9E")


def get_contrast_text_color(background_color: str) -> str:
    """Get appropriate text color (black/white) based on background"""
    # Simple implementation - could be improved with actual luminance calculation
    dark_colors = [SEVERITY_COLORS[4], SEVERITY_COLORS[5], COLOR_PRIMARY, COLOR_DANGER]
    return "white" if background_color in dark_colors else COLOR_TEXT_PRIMARY
