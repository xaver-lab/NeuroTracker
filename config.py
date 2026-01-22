"""
Configuration file for Neuro-Tracker Application
"""
import os
from pathlib import Path

# Application Info
APP_NAME = "Neuro-Tracker"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Your Name"

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RESOURCES_DIR = BASE_DIR / "resources"
ICONS_DIR = RESOURCES_DIR / "icons"

# Data Files
ENTRIES_FILE = DATA_DIR / "entries.json"
FOOD_SUGGESTIONS_FILE = DATA_DIR / "food_suggestions.json"
SETTINGS_FILE = DATA_DIR / "settings.json"

# Google Drive Settings
GOOGLE_DRIVE_ENABLED = False  # Set to True to enable sync
GOOGLE_CREDENTIALS_FILE = BASE_DIR / "credentials.json"
GOOGLE_TOKEN_FILE = DATA_DIR / "token.json"
GOOGLE_DRIVE_FOLDER = "Neuro-Tracker"  # Folder name in Google Drive
SYNC_INTERVAL_MINUTES = 5  # Auto-sync every 5 minutes

# UI Settings
WINDOW_TITLE = f"{APP_NAME} v{APP_VERSION}"
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 800
ENTRY_PANEL_WIDTH = 350  # Width of left entry panel

# Calendar Settings
WEEKS_TO_DISPLAY = 2  # Number of weeks to show (current + previous)
FIRST_DAY_OF_WEEK = 0  # 0 = Monday, 6 = Sunday

# Severity Settings
MIN_SEVERITY = 1
MAX_SEVERITY = 5
SEVERITY_COLORS = {
    1: "#4CAF50",  # Green - Very Good
    2: "#8BC34A",  # Light Green - Good
    3: "#FFC107",  # Yellow - Moderate
    4: "#FF9800",  # Orange - Bad
    5: "#F44336",  # Red - Very Bad
}

# Food Suggestions (Default suggestions, can be extended by user)
DEFAULT_FOOD_SUGGESTIONS = [
    # Dairy
    "Milch", "Käse", "Joghurt", "Butter", "Sahne", "Quark",

    # Vegetables
    "Tomaten", "Paprika", "Gurken", "Karotten", "Brokkoli", "Spinat",
    "Zwiebeln", "Knoblauch", "Salat", "Zucchini",

    # Fruits
    "Äpfel", "Bananen", "Orangen", "Erdbeeren", "Weintrauben", "Kiwi",
    "Ananas", "Mango", "Birnen", "Pfirsiche",

    # Grains
    "Weizen", "Haferflocken", "Reis", "Nudeln", "Brot", "Müsli",

    # Proteins
    "Hähnchen", "Rind", "Schwein", "Fisch", "Eier", "Tofu",

    # Nuts & Seeds
    "Erdnüsse", "Mandeln", "Walnüsse", "Haselnüsse", "Sonnenblumenkerne",

    # Other
    "Schokolade", "Kaffee", "Tee", "Alkohol", "Zucker", "Honig",
]

# Export Settings
EXPORT_CSV_DELIMITER = ";"
EXPORT_DATE_FORMAT = "%d.%m.%Y"

# Statistics Settings
STATS_MIN_DAYS = 7  # Minimum days needed for meaningful statistics
CORRELATION_THRESHOLD = 0.5  # Threshold for significant correlation

# Colors (QSS compatible)
COLOR_PRIMARY = "#2196F3"
COLOR_SECONDARY = "#FFC107"
COLOR_SUCCESS = "#4CAF50"
COLOR_WARNING = "#FF9800"
COLOR_DANGER = "#F44336"
COLOR_BACKGROUND = "#FAFAFA"
COLOR_SURFACE = "#FFFFFF"
COLOR_TEXT_PRIMARY = "#212121"
COLOR_TEXT_SECONDARY = "#757575"

# Ensure directories exist
def init_directories():
    """Create necessary directories if they don't exist"""
    DATA_DIR.mkdir(exist_ok=True)
    RESOURCES_DIR.mkdir(exist_ok=True)
    ICONS_DIR.mkdir(exist_ok=True)

# Initialize on import
init_directories()
