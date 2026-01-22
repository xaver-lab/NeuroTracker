"""
Data Manager for loading and saving day entries
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from models.day_entry import DayEntry
import config


class DataManager:
    """Manages loading, saving, and querying day entries"""

    def __init__(self, data_file: Path = None):
        """
        Initialize DataManager

        Args:
            data_file: Path to JSON file for storing entries
        """
        self.data_file = data_file or config.ENTRIES_FILE
        self.entries: Dict[str, DayEntry] = {}
        self.load()

    def load(self):
        """Load entries from JSON file"""
        if not self.data_file.exists():
            self.entries = {}
            return

        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.entries = {
                    date: DayEntry.from_dict(entry_data)
                    for date, entry_data in data.items()
                }
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading data: {e}")
            self.entries = {}

    def save(self):
        """Save entries to JSON file"""
        try:
            # Ensure directory exists
            self.data_file.parent.mkdir(parents=True, exist_ok=True)

            data = {
                date: entry.to_dict()
                for date, entry in self.entries.items()
            }

            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error saving data: {e}")
            raise

    def get_entry(self, date: str) -> Optional[DayEntry]:
        """
        Get entry for a specific date

        Args:
            date: Date in ISO format (YYYY-MM-DD)

        Returns:
            DayEntry if exists, None otherwise
        """
        return self.entries.get(date)

    def add_or_update_entry(self, entry: DayEntry):
        """
        Add new entry or update existing one

        Args:
            entry: DayEntry to add/update
        """
        self.entries[entry.date] = entry
        self.save()

    def delete_entry(self, date: str) -> bool:
        """
        Delete entry for a specific date

        Args:
            date: Date in ISO format (YYYY-MM-DD)

        Returns:
            True if entry was deleted, False if it didn't exist
        """
        if date in self.entries:
            del self.entries[date]
            self.save()
            return True
        return False

    def get_entries_in_range(self, start_date: str, end_date: str) -> List[DayEntry]:
        """
        Get all entries within a date range (inclusive)

        Args:
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)

        Returns:
            List of DayEntry objects sorted by date
        """
        entries = [
            entry for date, entry in self.entries.items()
            if start_date <= date <= end_date
        ]
        return sorted(entries, key=lambda e: e.date)

    def get_recent_entries(self, days: int = 14) -> List[DayEntry]:
        """
        Get entries from the last N days

        Args:
            days: Number of days to look back

        Returns:
            List of DayEntry objects sorted by date
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)

        return self.get_entries_in_range(
            start_date.isoformat(),
            end_date.isoformat()
        )

    def get_all_entries(self) -> List[DayEntry]:
        """
        Get all entries sorted by date

        Returns:
            List of all DayEntry objects
        """
        return sorted(self.entries.values(), key=lambda e: e.date)

    def get_all_foods(self) -> List[str]:
        """
        Get list of all unique foods ever entered

        Returns:
            Sorted list of unique food names
        """
        foods = set()
        for entry in self.entries.values():
            foods.update(entry.foods)
        return sorted(foods)

    def get_statistics(self) -> dict:
        """
        Calculate basic statistics

        Returns:
            Dictionary with statistics
        """
        if not self.entries:
            return {
                "total_entries": 0,
                "avg_severity": 0,
                "min_severity": 0,
                "max_severity": 0,
                "unique_foods": 0
            }

        severities = [e.severity for e in self.entries.values() if e.severity is not None]

        return {
            "total_entries": len(self.entries),
            "avg_severity": sum(severities) / len(severities) if severities else 0,
            "min_severity": min(severities) if severities else 0,
            "max_severity": max(severities) if severities else 0,
            "unique_foods": len(self.get_all_foods())
        }
