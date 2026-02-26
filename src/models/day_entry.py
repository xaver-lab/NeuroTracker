"""
Data model for a single day entry
"""
from datetime import datetime
from typing import List, Optional, Dict, Any


class DayEntry:
    """Represents a single day's health and food data"""

    def __init__(
        self,
        date: str,
        severity: Optional[int] = None,
        foods: Optional[List[str]] = None,
        notes: str = "",
        skin_notes: str = "",
        food_notes: str = "",
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        # ── New modular trigger fields ─────────────────────────────────────
        stress_level: Optional[int] = None,          # 1-5 (1=entspannt, 5=extrem)
        fungal_active: Optional[bool] = None,         # Zehenpilz / Mykose aktiv?
        sleep_quality: Optional[int] = None,          # 1-5 (1=schlecht, 5=sehr gut)
        weather: Optional[str] = None,                # Wetterkategorie
        sweating: Optional[bool] = None,              # Übermäßiges Schwitzen?
        contact_exposures: Optional[List[str]] = None, # Kontaktallergene
    ):
        self.date = date
        self.severity = severity
        self.foods = foods if foods is not None else []
        self.notes = notes
        self.skin_notes = skin_notes
        self.food_notes = food_notes

        now = datetime.now().isoformat()
        self.created_at = created_at or now
        self.updated_at = updated_at or now

        # Trigger fields
        self.stress_level = stress_level
        self.fungal_active = fungal_active
        self.sleep_quality = sleep_quality
        self.weather = weather
        self.sweating = sweating
        self.contact_exposures = contact_exposures if contact_exposures is not None else []

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary for JSON serialization"""
        return {
            "date": self.date,
            "severity": self.severity,
            "foods": self.foods,
            "notes": self.notes,
            "skin_notes": self.skin_notes,
            "food_notes": self.food_notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            # Trigger fields (only written if not None)
            "stress_level": self.stress_level,
            "fungal_active": self.fungal_active,
            "sleep_quality": self.sleep_quality,
            "weather": self.weather,
            "sweating": self.sweating,
            "contact_exposures": self.contact_exposures,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DayEntry':
        """Create DayEntry from dictionary (backward compatible)"""
        return cls(
            date=data["date"],
            severity=data.get("severity"),
            foods=data.get("foods", []),
            notes=data.get("notes", ""),
            skin_notes=data.get("skin_notes", ""),
            food_notes=data.get("food_notes", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            # New fields default to None if missing (old entries)
            stress_level=data.get("stress_level"),
            fungal_active=data.get("fungal_active"),
            sleep_quality=data.get("sleep_quality"),
            weather=data.get("weather"),
            sweating=data.get("sweating"),
            contact_exposures=data.get("contact_exposures", []),
        )

    def update(
        self,
        severity: Optional[int] = None,
        foods: Optional[List[str]] = None,
        notes: Optional[str] = None,
        skin_notes: Optional[str] = None,
        food_notes: Optional[str] = None,
        stress_level: Optional[int] = None,
        fungal_active: Optional[bool] = None,
        sleep_quality: Optional[int] = None,
        weather: Optional[str] = None,
        sweating: Optional[bool] = None,
        contact_exposures: Optional[List[str]] = None,
    ):
        """Update entry data and refresh updated_at timestamp"""
        if severity is not None:
            self.severity = severity
        if foods is not None:
            self.foods = foods
        if notes is not None:
            self.notes = notes
        if skin_notes is not None:
            self.skin_notes = skin_notes
        if food_notes is not None:
            self.food_notes = food_notes
        if stress_level is not None:
            self.stress_level = stress_level
        if fungal_active is not None:
            self.fungal_active = fungal_active
        if sleep_quality is not None:
            self.sleep_quality = sleep_quality
        if weather is not None:
            self.weather = weather
        if sweating is not None:
            self.sweating = sweating
        if contact_exposures is not None:
            self.contact_exposures = contact_exposures

        self.updated_at = datetime.now().isoformat()

    def is_complete(self) -> bool:
        """Check if entry has all required data"""
        return self.severity is not None

    def __str__(self) -> str:
        foods_str = ", ".join(self.foods) if self.foods else "Keine"
        return f"DayEntry({self.date}, Severity: {self.severity}, Foods: {foods_str})"

    def __repr__(self) -> str:
        return f"DayEntry(date='{self.date}', severity={self.severity}, foods={self.foods})"
