"""
Food Manager for managing food suggestions and autocomplete
"""
import json
from pathlib import Path
from typing import List, Set

import config


class FoodManager:
    """Manages food suggestions for autocomplete"""

    def __init__(self, suggestions_file: Path = None):
        """
        Initialize FoodManager

        Args:
            suggestions_file: Path to JSON file for storing suggestions
        """
        self.suggestions_file = suggestions_file or config.FOOD_SUGGESTIONS_FILE
        self.suggestions: Set[str] = set()
        self.load()

    def load(self):
        """Load suggestions from JSON file"""
        if not self.suggestions_file.exists():
            # Initialize with default suggestions
            self.suggestions = set(config.DEFAULT_FOOD_SUGGESTIONS)
            self.save()
            return

        try:
            with open(self.suggestions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.suggestions = set(data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading food suggestions: {e}")
            self.suggestions = set(config.DEFAULT_FOOD_SUGGESTIONS)

    def save(self):
        """Save suggestions to JSON file"""
        try:
            # Ensure directory exists
            self.suggestions_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.suggestions_file, 'w', encoding='utf-8') as f:
                json.dump(sorted(self.suggestions), f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error saving food suggestions: {e}")
            raise

    def add_food(self, food: str):
        """
        Add a new food to suggestions

        Args:
            food: Food name to add
        """
        food = food.strip()
        if food:
            self.suggestions.add(food)
            self.save()

    def add_foods(self, foods: List[str]):
        """
        Add multiple foods to suggestions

        Args:
            foods: List of food names to add
        """
        for food in foods:
            food = food.strip()
            if food:
                self.suggestions.add(food)
        self.save()

    def remove_food(self, food: str):
        """
        Remove a food from suggestions

        Args:
            food: Food name to remove
        """
        if food in self.suggestions:
            self.suggestions.remove(food)
            self.save()

    def get_suggestions(self, prefix: str = "") -> List[str]:
        """
        Get food suggestions, optionally filtered by prefix

        Args:
            prefix: Optional prefix to filter suggestions

        Returns:
            Sorted list of matching suggestions
        """
        if not prefix:
            return sorted(self.suggestions)

        prefix_lower = prefix.lower()
        matching = [
            food for food in self.suggestions
            if food.lower().startswith(prefix_lower)
        ]
        return sorted(matching)

    def get_all_suggestions(self) -> List[str]:
        """
        Get all food suggestions

        Returns:
            Sorted list of all suggestions
        """
        return sorted(self.suggestions)
