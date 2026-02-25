"""
Settings Manager for Neuro-Tracker Application
Manages which trigger modules are enabled/disabled.
Settings are persisted to data/settings.json
"""
import json
import copy
from pathlib import Path
from typing import Dict

from config import SETTINGS_FILE, TRACKER_MODULES


class SettingsManager:
    """
    Manages application settings, especially which tracker modules are active.

    Module states are saved persistently so the user's choices survive restarts.
    Each module maps to a boolean: True = visible in EntryPanel and Statistics.
    """

    def __init__(self):
        self._settings: Dict = {}
        self.load()

    def load(self):
        """Load settings from disk; falls back to config defaults on first run."""
        try:
            if Path(SETTINGS_FILE).exists():
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    self._settings = json.load(f)
            else:
                self._settings = {}
        except Exception:
            self._settings = {}

        # Ensure every module from config exists in settings
        if "modules" not in self._settings:
            self._settings["modules"] = {}

        for key, info in TRACKER_MODULES.items():
            if key not in self._settings["modules"]:
                self._settings["modules"][key] = info["enabled"]

    def save(self):
        """Persist settings to disk."""
        try:
            Path(SETTINGS_FILE).parent.mkdir(parents=True, exist_ok=True)
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[SettingsManager] Fehler beim Speichern: {e}")

    # ── Module API ─────────────────────────────────────────────────────────────

    def is_module_enabled(self, module_key: str) -> bool:
        """Return True if the given module is currently active."""
        return self._settings.get("modules", {}).get(module_key, False)

    def set_module_enabled(self, module_key: str, enabled: bool):
        """Enable or disable a module and persist the change."""
        if "modules" not in self._settings:
            self._settings["modules"] = {}
        self._settings["modules"][module_key] = enabled
        self.save()

    def get_all_modules(self) -> Dict[str, bool]:
        """Return dict {module_key: is_enabled} for all known modules."""
        result = {}
        for key in TRACKER_MODULES:
            result[key] = self.is_module_enabled(key)
        return result

    def get_module_info(self, module_key: str) -> Dict:
        """Return label and icon for a module key."""
        return copy.deepcopy(TRACKER_MODULES.get(module_key, {"label": module_key, "icon": ""}))
