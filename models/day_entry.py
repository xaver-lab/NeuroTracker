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
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        """
        Initialize a DayEntry

        Args:
            date: Date in ISO format (YYYY-MM-DD)
            severity: Eczema severity rating (1-5)
            foods: List of food items consumed
            notes: Optional notes for the day
            created_at: Creation timestamp (ISO format)
            updated_at: Last update timestamp (ISO format)
        """
        self.date = date
        self.severity = severity
        self.foods = foods if foods is not None else []
        self.notes = notes

        now = datetime.now().isoformat()
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary for JSON serialization"""
        return {
            "date": self.date,
            "severity": self.severity,
            "foods": self.foods,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DayEntry':
        """Create DayEntry from dictionary"""
        return cls(
            date=data["date"],
            severity=data.get("severity"),
            foods=data.get("foods", []),
            notes=data.get("notes", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )

    def update(self, severity: Optional[int] = None, foods: Optional[List[str]] = None, notes: Optional[str] = None):
        """Update entry data and refresh updated_at timestamp"""
        if severity is not None:
            self.severity = severity
        if foods is not None:
            self.foods = foods
        if notes is not None:
            self.notes = notes

        self.updated_at = datetime.now().isoformat()

    def is_complete(self) -> bool:
        """Check if entry has all required data"""
        return self.severity is not None

    def __str__(self) -> str:
        """String representation"""
        foods_str = ", ".join(self.foods) if self.foods else "Keine"
        return f"DayEntry({self.date}, Severity: {self.severity}, Foods: {foods_str})"

    def __repr__(self) -> str:
        """Developer representation"""
        return f"DayEntry(date='{self.date}', severity={self.severity}, foods={self.foods})"
