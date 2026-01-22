"""
Statistics Calculator for Neuro-Tracker Application
Provides statistical analysis of symptoms and food correlations
"""

from datetime import date, timedelta
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

from models.data_manager import DataManager
from models.day_entry import DayEntry


class StatisticsCalculator:
    """
    Calculates various statistics from the tracking data.
    Includes severity analysis, food correlations, and trends.
    """

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    def calculate_all(self, days: Optional[int] = None) -> Dict:
        """
        Calculate all statistics for the given time period.

        Args:
            days: Number of days to analyze. None for all data.

        Returns:
            Dictionary containing all statistics
        """
        entries = self._get_entries_for_period(days)

        return {
            'total_entries': len(entries),
            'average_severity': self._calculate_average_severity(entries),
            'severity_distribution': self._calculate_severity_distribution(entries),
            'good_days': self._count_good_days(entries),
            'bad_days': self._count_bad_days(entries),
            'top_foods': self._get_top_foods(entries),
            'food_correlations': self._calculate_food_correlations(entries),
            'weekly_averages': self._calculate_weekly_averages(entries),
            'day_of_week_averages': self._calculate_day_of_week_averages(entries),
            'streak_info': self._calculate_streak_info(entries),
        }

    def _get_entries_for_period(self, days: Optional[int]) -> List[DayEntry]:
        """Get entries for the specified period"""
        if days is None:
            return self.data_manager.get_all_entries()

        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        return self.data_manager.get_entries_in_range(start_date, end_date)

    def _calculate_average_severity(self, entries: List[DayEntry]) -> float:
        """Calculate average severity"""
        if not entries:
            return 0.0

        total = sum(entry.severity for entry in entries)
        return round(total / len(entries), 2)

    def _calculate_severity_distribution(self, entries: List[DayEntry]) -> Dict[int, int]:
        """Calculate distribution of severity levels"""
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        for entry in entries:
            if entry.severity in distribution:
                distribution[entry.severity] += 1

        return distribution

    def _count_good_days(self, entries: List[DayEntry]) -> int:
        """Count days with severity 1 or 2"""
        return sum(1 for entry in entries if entry.severity <= 2)

    def _count_bad_days(self, entries: List[DayEntry]) -> int:
        """Count days with severity 4 or 5"""
        return sum(1 for entry in entries if entry.severity >= 4)

    def _get_top_foods(self, entries: List[DayEntry], limit: int = 10) -> List[Tuple[str, int]]:
        """Get the most frequently consumed foods"""
        food_counts = defaultdict(int)

        for entry in entries:
            for food in entry.foods:
                food_counts[food] += 1

        sorted_foods = sorted(food_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_foods[:limit]

    def _calculate_food_correlations(self, entries: List[DayEntry]) -> List[Dict]:
        """
        Calculate correlation between foods and severity.
        Returns foods sorted by their average associated severity.
        """
        food_data = defaultdict(lambda: {'severities': [], 'count': 0})

        for entry in entries:
            for food in entry.foods:
                food_data[food]['severities'].append(entry.severity)
                food_data[food]['count'] += 1

        correlations = []
        for food, data in food_data.items():
            if data['count'] >= 2:  # Need at least 2 occurrences
                avg_severity = sum(data['severities']) / len(data['severities'])
                correlations.append({
                    'food': food,
                    'count': data['count'],
                    'average_severity': round(avg_severity, 2),
                    'severities': data['severities']
                })

        # Sort by average severity (highest first - potential triggers)
        correlations.sort(key=lambda x: x['average_severity'], reverse=True)

        return correlations

    def _calculate_weekly_averages(self, entries: List[DayEntry]) -> List[Dict]:
        """Calculate weekly severity averages"""
        if not entries:
            return []

        # Group entries by week
        weeks = defaultdict(list)

        for entry in entries:
            entry_date = date.fromisoformat(entry.date)
            # Get the Monday of that week
            week_start = entry_date - timedelta(days=entry_date.weekday())
            weeks[week_start].append(entry.severity)

        # Calculate averages
        weekly_data = []
        for week_start in sorted(weeks.keys()):
            severities = weeks[week_start]
            avg = sum(severities) / len(severities)

            # Format week label
            week_end = week_start + timedelta(days=6)
            if week_start.month == week_end.month:
                label = f"{week_start.day}.-{week_end.day}. {week_start.strftime('%b')}"
            else:
                label = f"{week_start.day}. {week_start.strftime('%b')} - {week_end.day}. {week_end.strftime('%b')}"

            weekly_data.append({
                'week_start': week_start.isoformat(),
                'week_label': label,
                'average': round(avg, 2),
                'count': len(severities)
            })

        return weekly_data[-8:]  # Return last 8 weeks

    def _calculate_day_of_week_averages(self, entries: List[DayEntry]) -> Dict[int, float]:
        """Calculate average severity for each day of the week"""
        day_data = defaultdict(list)

        for entry in entries:
            entry_date = date.fromisoformat(entry.date)
            day_num = entry_date.weekday()  # 0=Monday, 6=Sunday
            day_data[day_num].append(entry.severity)

        averages = {}
        for day_num in range(7):
            severities = day_data[day_num]
            if severities:
                averages[day_num] = round(sum(severities) / len(severities), 2)
            else:
                averages[day_num] = 0

        return averages

    def _calculate_streak_info(self, entries: List[DayEntry]) -> Dict:
        """Calculate streak information (consecutive good/bad days)"""
        if not entries:
            return {'current_streak': 0, 'streak_type': None, 'best_good_streak': 0}

        # Sort entries by date
        sorted_entries = sorted(entries, key=lambda x: x.date)

        best_good_streak = 0
        current_good_streak = 0

        for entry in sorted_entries:
            if entry.severity <= 2:
                current_good_streak += 1
                best_good_streak = max(best_good_streak, current_good_streak)
            else:
                current_good_streak = 0

        # Calculate current streak (from today backwards)
        today_str = date.today().isoformat()
        current_streak = 0
        streak_type = None

        for entry in reversed(sorted_entries):
            if current_streak == 0:
                streak_type = 'good' if entry.severity <= 2 else 'bad'
                current_streak = 1
            else:
                if streak_type == 'good' and entry.severity <= 2:
                    current_streak += 1
                elif streak_type == 'bad' and entry.severity >= 4:
                    current_streak += 1
                else:
                    break

        return {
            'current_streak': current_streak,
            'streak_type': streak_type,
            'best_good_streak': best_good_streak
        }

    def get_potential_triggers(self, threshold: float = 3.5, min_occurrences: int = 3) -> List[Dict]:
        """
        Identify foods that might be triggers.

        Args:
            threshold: Minimum average severity to consider as trigger
            min_occurrences: Minimum times food must appear

        Returns:
            List of potential trigger foods with statistics
        """
        entries = self.data_manager.get_all_entries()
        correlations = self._calculate_food_correlations(entries)

        triggers = [
            food_data for food_data in correlations
            if food_data['average_severity'] >= threshold
            and food_data['count'] >= min_occurrences
        ]

        return triggers

    def get_safe_foods(self, threshold: float = 2.5, min_occurrences: int = 3) -> List[Dict]:
        """
        Identify foods that seem safe.

        Args:
            threshold: Maximum average severity to consider as safe
            min_occurrences: Minimum times food must appear

        Returns:
            List of safe foods with statistics
        """
        entries = self.data_manager.get_all_entries()
        correlations = self._calculate_food_correlations(entries)

        safe_foods = [
            food_data for food_data in correlations
            if food_data['average_severity'] <= threshold
            and food_data['count'] >= min_occurrences
        ]

        # Sort by lowest severity first
        safe_foods.sort(key=lambda x: x['average_severity'])

        return safe_foods

    def get_summary(self, days: int = 30) -> str:
        """
        Get a text summary of the analysis.

        Args:
            days: Number of days to analyze

        Returns:
            Human-readable summary text
        """
        stats = self.calculate_all(days)

        if stats['total_entries'] == 0:
            return "Noch keine Einträge vorhanden. Beginne mit dem Tracking um Analysen zu erhalten."

        lines = [
            f"Zusammenfassung der letzten {days} Tage:",
            f"",
            f"📊 {stats['total_entries']} Einträge erfasst",
            f"📈 Durchschnittliche Schwere: {stats['average_severity']:.1f}",
            f"😊 {stats['good_days']} gute Tage (Schwere 1-2)",
            f"😟 {stats['bad_days']} schlechte Tage (Schwere 4-5)",
            f""
        ]

        # Add potential triggers
        triggers = self.get_potential_triggers()
        if triggers:
            lines.append("⚠️ Mögliche Trigger:")
            for trigger in triggers[:3]:
                lines.append(f"   • {trigger['food']} (Ø {trigger['average_severity']:.1f})")
            lines.append("")

        # Add safe foods
        safe = self.get_safe_foods()
        if safe:
            lines.append("✅ Gut verträgliche Lebensmittel:")
            for food in safe[:3]:
                lines.append(f"   • {food['food']} (Ø {food['average_severity']:.1f})")

        return "\n".join(lines)

    def compare_periods(self, period1_days: int, period2_days: int) -> Dict:
        """
        Compare statistics between two time periods.

        Args:
            period1_days: Days in first period (more recent)
            period2_days: Days in second period (older)

        Returns:
            Comparison data
        """
        today = date.today()

        # Period 1: most recent
        p1_end = today
        p1_start = today - timedelta(days=period1_days)
        p1_entries = self.data_manager.get_entries_in_range(p1_start, p1_end)

        # Period 2: before period 1
        p2_end = p1_start - timedelta(days=1)
        p2_start = p2_end - timedelta(days=period2_days)
        p2_entries = self.data_manager.get_entries_in_range(p2_start, p2_end)

        p1_avg = self._calculate_average_severity(p1_entries) if p1_entries else 0
        p2_avg = self._calculate_average_severity(p2_entries) if p2_entries else 0

        return {
            'period1': {
                'start': p1_start.isoformat(),
                'end': p1_end.isoformat(),
                'entries': len(p1_entries),
                'average_severity': p1_avg
            },
            'period2': {
                'start': p2_start.isoformat(),
                'end': p2_end.isoformat(),
                'entries': len(p2_entries),
                'average_severity': p2_avg
            },
            'change': round(p1_avg - p2_avg, 2),
            'improved': p1_avg < p2_avg
        }
