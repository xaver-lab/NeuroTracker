"""
Validators for Neuro-Tracker Application
Input validation utilities
"""

from datetime import date, datetime
from typing import Tuple, List, Optional
import re

from config import MIN_SEVERITY, MAX_SEVERITY


class Validators:
    """Collection of validation functions for the application"""

    @staticmethod
    def validate_severity(severity: int) -> Tuple[bool, str]:
        """
        Validate a severity value.

        Args:
            severity: The severity value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(severity, int):
            return False, "Schweregrad muss eine Ganzzahl sein."

        if severity < MIN_SEVERITY or severity > MAX_SEVERITY:
            return False, f"Schweregrad muss zwischen {MIN_SEVERITY} und {MAX_SEVERITY} liegen."

        return True, ""

    @staticmethod
    def validate_date(date_value) -> Tuple[bool, str]:
        """
        Validate a date value.

        Args:
            date_value: The date to validate (date object or ISO string)

        Returns:
            Tuple of (is_valid, error_message)
        """
        if isinstance(date_value, date):
            return True, ""

        if isinstance(date_value, str):
            try:
                parsed_date = date.fromisoformat(date_value)
                # Check if date is not too far in the future
                if parsed_date > date.today():
                    return False, "Datum kann nicht in der Zukunft liegen."
                # Check if date is not unreasonably old
                if parsed_date.year < 2000:
                    return False, "Datum muss nach dem Jahr 2000 liegen."
                return True, ""
            except ValueError:
                return False, "Ungültiges Datumsformat. Verwende YYYY-MM-DD."

        return False, "Datum muss ein date-Objekt oder ISO-String sein."

    @staticmethod
    def validate_food(food: str) -> Tuple[bool, str]:
        """
        Validate a food item name.

        Args:
            food: The food name to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(food, str):
            return False, "Lebensmittel muss ein Text sein."

        food = food.strip()

        if not food:
            return False, "Lebensmittel darf nicht leer sein."

        if len(food) < 2:
            return False, "Lebensmittel muss mindestens 2 Zeichen haben."

        if len(food) > 50:
            return False, "Lebensmittel darf maximal 50 Zeichen haben."

        # Check for invalid characters
        if re.search(r'[<>{}[\]\\]', food):
            return False, "Lebensmittel enthält ungültige Zeichen."

        return True, ""

    @staticmethod
    def validate_foods_list(foods: List[str]) -> Tuple[bool, str]:
        """
        Validate a list of food items.

        Args:
            foods: List of food names to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(foods, list):
            return False, "Lebensmittel müssen als Liste angegeben werden."

        if len(foods) > 50:
            return False, "Maximal 50 Lebensmittel pro Tag erlaubt."

        for food in foods:
            is_valid, error = Validators.validate_food(food)
            if not is_valid:
                return False, f"Ungültiges Lebensmittel '{food}': {error}"

        # Check for duplicates
        if len(foods) != len(set(foods)):
            return False, "Doppelte Lebensmittel in der Liste."

        return True, ""

    @staticmethod
    def validate_notes(notes: Optional[str]) -> Tuple[bool, str]:
        """
        Validate notes text.

        Args:
            notes: The notes text to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if notes is None:
            return True, ""

        if not isinstance(notes, str):
            return False, "Notizen müssen ein Text sein."

        if len(notes) > 1000:
            return False, "Notizen dürfen maximal 1000 Zeichen haben."

        return True, ""

    @staticmethod
    def validate_entry(date_value, severity: int, foods: List[str],
                       notes: Optional[str] = None) -> Tuple[bool, List[str]]:
        """
        Validate all fields of an entry.

        Args:
            date_value: The date to validate
            severity: The severity value
            foods: List of food names
            notes: Optional notes text

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        is_valid, error = Validators.validate_date(date_value)
        if not is_valid:
            errors.append(error)

        is_valid, error = Validators.validate_severity(severity)
        if not is_valid:
            errors.append(error)

        is_valid, error = Validators.validate_foods_list(foods)
        if not is_valid:
            errors.append(error)

        is_valid, error = Validators.validate_notes(notes)
        if not is_valid:
            errors.append(error)

        return len(errors) == 0, errors

    @staticmethod
    def sanitize_food(food: str) -> str:
        """
        Sanitize a food item name.

        Args:
            food: The food name to sanitize

        Returns:
            Sanitized food name
        """
        # Strip whitespace
        food = food.strip()

        # Remove multiple spaces
        food = re.sub(r'\s+', ' ', food)

        # Capitalize first letter
        if food:
            food = food[0].upper() + food[1:]

        return food

    @staticmethod
    def sanitize_foods_list(foods: List[str]) -> List[str]:
        """
        Sanitize a list of food items.

        Args:
            foods: List of food names to sanitize

        Returns:
            Sanitized list of food names (duplicates removed)
        """
        sanitized = []
        seen = set()

        for food in foods:
            clean_food = Validators.sanitize_food(food)
            if clean_food and clean_food.lower() not in seen:
                sanitized.append(clean_food)
                seen.add(clean_food.lower())

        return sanitized

    @staticmethod
    def sanitize_notes(notes: Optional[str]) -> Optional[str]:
        """
        Sanitize notes text.

        Args:
            notes: The notes text to sanitize

        Returns:
            Sanitized notes text or None if empty
        """
        if notes is None:
            return None

        notes = notes.strip()

        if not notes:
            return None

        # Remove excessive newlines
        notes = re.sub(r'\n{3,}', '\n\n', notes)

        # Limit length
        if len(notes) > 1000:
            notes = notes[:997] + '...'

        return notes


class DateRangeValidator:
    """Validator for date ranges"""

    @staticmethod
    def validate(start_date: date, end_date: date) -> Tuple[bool, str]:
        """
        Validate a date range.

        Args:
            start_date: Start of the range
            end_date: End of the range

        Returns:
            Tuple of (is_valid, error_message)
        """
        if start_date > end_date:
            return False, "Startdatum muss vor dem Enddatum liegen."

        if (end_date - start_date).days > 365:
            return False, "Datumsbereich darf maximal 1 Jahr umfassen."

        return True, ""


class ExportValidator:
    """Validator for export operations"""

    @staticmethod
    def validate_filepath(filepath: str, extension: str) -> Tuple[bool, str]:
        """
        Validate an export filepath.

        Args:
            filepath: The file path to validate
            extension: Expected file extension (e.g., '.csv', '.pdf')

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not filepath:
            return False, "Dateipfad darf nicht leer sein."

        if not filepath.lower().endswith(extension.lower()):
            return False, f"Datei muss die Endung {extension} haben."

        # Check for invalid characters in path
        if re.search(r'[<>"|?*]', filepath):
            return False, "Dateipfad enthält ungültige Zeichen."

        return True, ""
