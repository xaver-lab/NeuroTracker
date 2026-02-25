"""
Statistics Calculator for Neuro-Tracker Application
Complete trigger analysis: food, stress, fungal infections, sleep, weather, sweating, contact.
"""

from datetime import date, timedelta
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

from models.data_manager import DataManager
from models.day_entry import DayEntry
from config import NICKEL_RICH_FOODS


class StatisticsCalculator:
    """
    Calculates statistics and detects trigger patterns from all tracked factors.
    Supports: food, stress, fungal (Id-reaction), sleep, weather, sweating, contact.
    """

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    # ── Core helpers ────────────────────────────────────────────────────────────

    def _get_entries_for_period(self, days: Optional[int]) -> List[DayEntry]:
        if days is None:
            return self.data_manager.get_all_entries()
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        return self.data_manager.get_entries_in_range(start_date, end_date)

    def _avg(self, values: List[float]) -> float:
        return round(sum(values) / len(values), 2) if values else 0.0

    def _entry_map(self, entries: List[DayEntry]) -> Dict[date, DayEntry]:
        return {date.fromisoformat(e.date): e for e in entries}

    # ── Primary statistics ──────────────────────────────────────────────────────

    def calculate_all(self, days: Optional[int] = None) -> Dict:
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
            # New trigger metrics
            'average_stress': self._avg_field(entries, 'stress_level'),
            'fungal_days': sum(1 for e in entries if e.fungal_active),
            'average_sleep': self._avg_field(entries, 'sleep_quality'),
            'weather_distribution': self._weather_distribution(entries),
            'sweating_days': sum(1 for e in entries if e.sweating),
        }

    def _avg_field(self, entries: List[DayEntry], field: str) -> float:
        values = [getattr(e, field) for e in entries if getattr(e, field) is not None]
        return self._avg(values)

    def _calculate_average_severity(self, entries: List[DayEntry]) -> float:
        values = [e.severity for e in entries if e.severity is not None]
        return self._avg(values)

    def _calculate_severity_distribution(self, entries: List[DayEntry]) -> Dict[int, int]:
        dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for e in entries:
            if e.severity in dist:
                dist[e.severity] += 1
        return dist

    def _count_good_days(self, entries: List[DayEntry]) -> int:
        return sum(1 for e in entries if e.severity is not None and e.severity <= 2)

    def _count_bad_days(self, entries: List[DayEntry]) -> int:
        return sum(1 for e in entries if e.severity is not None and e.severity >= 4)

    def _get_top_foods(self, entries: List[DayEntry], limit: int = 10) -> List[Tuple[str, int]]:
        counts = defaultdict(int)
        for e in entries:
            for f in e.foods:
                counts[f] += 1
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:limit]

    def _calculate_food_correlations(self, entries: List[DayEntry]) -> List[Dict]:
        food_data: Dict[str, Dict] = defaultdict(lambda: {'severities': [], 'count': 0})
        for e in entries:
            for f in e.foods:
                food_data[f]['severities'].append(e.severity)
                food_data[f]['count'] += 1
        result = []
        for food, data in food_data.items():
            if data['count'] >= 2:
                avg = sum(data['severities']) / len(data['severities'])
                result.append({
                    'food': food,
                    'count': data['count'],
                    'average_severity': round(avg, 2),
                    'severities': data['severities'],
                })
        result.sort(key=lambda x: x['average_severity'], reverse=True)
        return result

    def _calculate_weekly_averages(self, entries: List[DayEntry]) -> List[Dict]:
        if not entries:
            return []
        weeks: Dict[date, List[float]] = defaultdict(list)
        for e in entries:
            if e.severity is None:
                continue
            d = date.fromisoformat(e.date)
            week_start = d - timedelta(days=d.weekday())
            weeks[week_start].append(e.severity)
        weekly = []
        for ws in sorted(weeks.keys()):
            we = ws + timedelta(days=6)
            label = (
                f"{ws.day}.-{we.day}. {ws.strftime('%b')}"
                if ws.month == we.month
                else f"{ws.day}. {ws.strftime('%b')} - {we.day}. {we.strftime('%b')}"
            )
            sevs = weeks[ws]
            weekly.append({
                'week_start': ws.isoformat(),
                'week_label': label,
                'average': round(sum(sevs) / len(sevs), 2),
                'count': len(sevs),
            })
        return weekly[-8:]

    def _calculate_day_of_week_averages(self, entries: List[DayEntry]) -> Dict[int, float]:
        day_data: Dict[int, List[float]] = defaultdict(list)
        for e in entries:
            if e.severity is None:
                continue
            day_data[date.fromisoformat(e.date).weekday()].append(e.severity)
        return {
            d: round(sum(v) / len(v), 2) if v else 0
            for d in range(7)
            for v in [day_data[d]]
        }

    def _calculate_streak_info(self, entries: List[DayEntry]) -> Dict:
        if not entries:
            return {'current_streak': 0, 'streak_type': None, 'best_good_streak': 0}
        sorted_entries = sorted(entries, key=lambda x: x.date)
        best_good = cur_good = 0
        for e in sorted_entries:
            if e.severity is not None and e.severity <= 2:
                cur_good += 1
                best_good = max(best_good, cur_good)
            else:
                cur_good = 0
        current_streak = 0
        streak_type = None
        for e in reversed(sorted_entries):
            if current_streak == 0:
                streak_type = 'good' if (e.severity or 0) <= 2 else 'bad'
                current_streak = 1
            else:
                if streak_type == 'good' and (e.severity or 0) <= 2:
                    current_streak += 1
                elif streak_type == 'bad' and (e.severity or 0) >= 4:
                    current_streak += 1
                else:
                    break
        return {
            'current_streak': current_streak,
            'streak_type': streak_type,
            'best_good_streak': best_good,
        }

    def _weather_distribution(self, entries: List[DayEntry]) -> Dict[str, int]:
        dist: Dict[str, int] = defaultdict(int)
        for e in entries:
            if e.weather:
                dist[e.weather] += 1
        return dict(dist)

    # ── Pattern detection: foods (original, unchanged API) ────────────────────

    def detect_patterns(self, delay_days: int = 2, severity_threshold: int = 4) -> List[Dict]:
        """
        Detect food → skin-reaction patterns with a configurable time delay.
        Minimum 3 occurrences required for a result to appear.
        """
        entries = self.data_manager.get_all_entries()
        if len(entries) < 5:
            return []

        emap = self._entry_map(entries)
        patterns: Dict[str, Dict] = defaultdict(lambda: {'total': 0, 'bad': 0, 'details': []})

        for e in entries:
            if not e.foods:
                continue
            edate = date.fromisoformat(e.date)
            for food in e.foods:
                patterns[food]['total'] += 1
                for offset in range(1, delay_days + 1):
                    fut = emap.get(edate + timedelta(days=offset))
                    if fut and fut.severity is not None and fut.severity >= severity_threshold:
                        patterns[food]['bad'] += 1
                        patterns[food]['details'].append({
                            'food_date': e.date,
                            'reaction_date': fut.date,
                            'delay': offset,
                            'severity': fut.severity,
                        })
                        break

        result = []
        for food, data in patterns.items():
            if data['total'] >= 3:
                prob = round((data['bad'] / data['total']) * 100, 1)
                result.append({
                    'food': food,
                    'total_occurrences': data['total'],
                    'triggered_reactions': data['bad'],
                    'probability': prob,
                    'details': data['details'][:5],
                    'trigger_type': 'food',
                    'is_nickel_rich': food in NICKEL_RICH_FOODS,
                })
        result.sort(key=lambda x: x['probability'], reverse=True)
        return result

    # ── NEW: Fungal / Id-reaction analysis ────────────────────────────────────

    def detect_fungal_pattern(self, look_ahead_days: int = 14) -> Dict:
        """
        Analyse the Tinea pedis → Dyshidrosiform Id-reaction delay pattern.

        For each day where fungal_active flips from False/None to True we track
        severity over the following `look_ahead_days` days to find:
          - typical delay until flare onset
          - peak severity timing
          - average severity lift vs. baseline

        Returns a dict with:
          onset_events      – list of detected flare onsets
          avg_baseline      – avg severity without active fungus
          avg_fungal_active – avg severity on fungal-active days
          avg_peak_delay    – avg days until peak after fungal onset
          flare_probability – % of fungal onsets followed by severity ≥4
        """
        entries = self.data_manager.get_all_entries()
        if len(entries) < 5:
            return {'insufficient_data': True}

        emap = self._entry_map(entries)
        sorted_entries = sorted(entries, key=lambda x: x.date)

        # Split severities by fungal status
        sev_no_fungus = [
            e.severity for e in sorted_entries
            if e.severity is not None and not e.fungal_active
        ]
        sev_with_fungus = [
            e.severity for e in sorted_entries
            if e.severity is not None and e.fungal_active
        ]

        # Detect onset events (day fungal_active first becomes True in a sequence)
        onset_events = []
        prev_fungal = False
        for e in sorted_entries:
            current = bool(e.fungal_active)
            if current and not prev_fungal:
                # Onset detected
                onset_date = date.fromisoformat(e.date)
                window_sevs = []
                for offset in range(0, look_ahead_days + 1):
                    fut = emap.get(onset_date + timedelta(days=offset))
                    if fut and fut.severity is not None:
                        window_sevs.append((offset, fut.severity))

                if window_sevs:
                    peak_offset, peak_sev = max(window_sevs, key=lambda x: x[1])
                    onset_events.append({
                        'onset_date': e.date,
                        'peak_delay_days': peak_offset,
                        'peak_severity': peak_sev,
                        'window_data': window_sevs,
                        'flare_triggered': peak_sev >= 4,
                    })
            prev_fungal = current

        flare_count = sum(1 for ev in onset_events if ev['flare_triggered'])
        avg_peak_delay = (
            round(sum(ev['peak_delay_days'] for ev in onset_events) / len(onset_events), 1)
            if onset_events else None
        )

        return {
            'insufficient_data': False,
            'onset_events': onset_events,
            'total_onsets': len(onset_events),
            'avg_baseline_severity': self._avg(sev_no_fungus),
            'avg_fungal_active_severity': self._avg(sev_with_fungus),
            'avg_peak_delay_days': avg_peak_delay,
            'flare_probability': round(flare_count / len(onset_events) * 100, 1) if onset_events else 0,
        }

    # ── NEW: Stress analysis ──────────────────────────────────────────────────

    def detect_stress_pattern(self, delay_days: int = 2, severity_threshold: int = 4) -> Dict:
        """
        Correlate stress levels with skin severity (same day + N days later).

        Returns:
          stress_severity_by_level  – avg skin severity per stress level (1-5)
          high_stress_flare_prob    – % of stress ≥4 days followed by flare
          correlation_hint          – human-readable string
          delayed_patterns          – list of detected stress→flare events
        """
        entries = self.data_manager.get_all_entries()
        emap = self._entry_map(entries)

        # Average severity grouped by stress level (same day)
        sev_by_stress: Dict[int, List[float]] = defaultdict(list)
        for e in entries:
            if e.stress_level is not None and e.severity is not None:
                sev_by_stress[e.stress_level].append(e.severity)

        stress_severity_by_level = {
            lvl: self._avg(sevs) for lvl, sevs in sev_by_stress.items()
        }

        # High-stress → flare probability (time-delayed)
        high_stress_events = 0
        high_stress_flares = 0
        delayed_patterns = []

        for e in entries:
            if e.stress_level is None or e.stress_level < 4:
                continue
            edate = date.fromisoformat(e.date)
            high_stress_events += 1
            for offset in range(0, delay_days + 1):
                fut = emap.get(edate + timedelta(days=offset))
                if fut and fut.severity is not None and fut.severity >= severity_threshold:
                    high_stress_flares += 1
                    delayed_patterns.append({
                        'stress_date': e.date,
                        'stress_level': e.stress_level,
                        'reaction_date': fut.date,
                        'delay': offset,
                        'severity': fut.severity,
                    })
                    break

        flare_prob = (
            round(high_stress_flares / high_stress_events * 100, 1)
            if high_stress_events else 0
        )

        # Pearson-like correlation (simplified: higher stress → higher severity)
        pairs = [
            (e.stress_level, e.severity)
            for e in entries
            if e.stress_level is not None and e.severity is not None
        ]
        correlation = self._simple_correlation(pairs)

        return {
            'stress_severity_by_level': stress_severity_by_level,
            'high_stress_events': high_stress_events,
            'high_stress_flare_probability': flare_prob,
            'correlation': correlation,
            'delayed_patterns': delayed_patterns[:10],
        }

    def _simple_correlation(self, pairs: List[Tuple[float, float]]) -> Optional[float]:
        """Return a -1 to +1 Pearson-like correlation coefficient."""
        if len(pairs) < 3:
            return None
        n = len(pairs)
        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]
        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        num = sum((x - mean_x) * (y - mean_y) for x, y in pairs)
        den_x = sum((x - mean_x) ** 2 for x in xs) ** 0.5
        den_y = sum((y - mean_y) ** 2 for y in ys) ** 0.5
        if den_x == 0 or den_y == 0:
            return None
        return round(num / (den_x * den_y), 2)

    # ── NEW: Nickel-load analysis ─────────────────────────────────────────────

    def get_nickel_analysis(self) -> Dict:
        """
        Calculate daily nickel load (count of nickel-rich foods consumed)
        and correlate with skin severity.

        Returns:
          avg_severity_by_nickel_load  – dict {nickel_count: avg_severity}
          high_nickel_flare_prob       – % of high-nickel days (≥2 foods) → flare
          nickel_food_frequencies      – {food: count} for nickel-rich foods only
        """
        entries = self.data_manager.get_all_entries()
        emap = self._entry_map(entries)

        sev_by_load: Dict[int, List[float]] = defaultdict(list)
        nickel_food_counts: Dict[str, int] = defaultdict(int)
        high_nickel_events = 0
        high_nickel_flares = 0

        for e in entries:
            nickel_count = sum(1 for f in e.foods if f in NICKEL_RICH_FOODS)
            for f in e.foods:
                if f in NICKEL_RICH_FOODS:
                    nickel_food_counts[f] += 1

            if e.severity is not None:
                sev_by_load[nickel_count].append(e.severity)

            if nickel_count >= 2:
                high_nickel_events += 1
                edate = date.fromisoformat(e.date)
                for offset in range(0, 3):
                    fut = emap.get(edate + timedelta(days=offset))
                    if fut and fut.severity is not None and fut.severity >= 4:
                        high_nickel_flares += 1
                        break

        return {
            'avg_severity_by_nickel_load': {
                load: self._avg(sevs) for load, sevs in sev_by_load.items()
            },
            'high_nickel_flare_probability': (
                round(high_nickel_flares / high_nickel_events * 100, 1)
                if high_nickel_events else 0
            ),
            'nickel_food_frequencies': dict(
                sorted(nickel_food_counts.items(), key=lambda x: x[1], reverse=True)
            ),
        }

    # ── NEW: Weather impact analysis ──────────────────────────────────────────

    def get_weather_analysis(self) -> Dict[str, float]:
        """Return average severity per weather category."""
        entries = self.data_manager.get_all_entries()
        sev_by_weather: Dict[str, List[float]] = defaultdict(list)
        for e in entries:
            if e.weather and e.severity is not None:
                sev_by_weather[e.weather].append(e.severity)
        return {w: self._avg(s) for w, s in sev_by_weather.items()}

    # ── NEW: Sleep impact ─────────────────────────────────────────────────────

    def get_sleep_analysis(self) -> Dict:
        """Correlate sleep quality with next-day severity."""
        entries = self.data_manager.get_all_entries()
        emap = self._entry_map(entries)

        sev_by_sleep: Dict[int, List[float]] = defaultdict(list)
        next_day_impact: Dict[int, List[float]] = defaultdict(list)

        for e in entries:
            if e.sleep_quality is not None and e.severity is not None:
                sev_by_sleep[e.sleep_quality].append(e.severity)
            if e.sleep_quality is not None:
                tomorrow = emap.get(date.fromisoformat(e.date) + timedelta(days=1))
                if tomorrow and tomorrow.severity is not None:
                    next_day_impact[e.sleep_quality].append(tomorrow.severity)

        return {
            'same_day': {q: self._avg(s) for q, s in sev_by_sleep.items()},
            'next_day': {q: self._avg(s) for q, s in next_day_impact.items()},
            'correlation': self._simple_correlation([
                (e.sleep_quality, e.severity)
                for e in entries
                if e.sleep_quality is not None and e.severity is not None
            ]),
        }

    # ── NEW: Universal multi-factor pattern detection ─────────────────────────

    def detect_all_trigger_patterns(
        self, delay_days: int = 2, severity_threshold: int = 4
    ) -> List[Dict]:
        """
        Unified trigger pattern table covering ALL tracked factors:
          - Individual foods
          - High stress (≥4)
          - Active fungal infection
          - Bad sleep (≤2)
          - Weather types
          - Sweating
          - Contact exposures

        Returns a flat list of trigger dicts, each with:
          trigger_type, trigger_label, total_occurrences,
          triggered_reactions, probability, details
        """
        entries = self.data_manager.get_all_entries()
        if len(entries) < 5:
            return []

        emap = self._entry_map(entries)
        results: List[Dict] = []

        # Helper: test trigger events
        def analyse(label: str, ttype: str, event_filter, extra: Dict = None) -> Optional[Dict]:
            events = [(e, date.fromisoformat(e.date)) for e in entries if event_filter(e)]
            if not events:
                return None
            total = len(events)
            bad = 0
            details = []
            for e, edate in events:
                for offset in range(0, delay_days + 1):
                    fut = emap.get(edate + timedelta(days=offset))
                    if fut and fut.severity is not None and fut.severity >= severity_threshold:
                        bad += 1
                        details.append({
                            'trigger_date': e.date,
                            'reaction_date': fut.date,
                            'delay': offset,
                            'severity': fut.severity,
                        })
                        break
            if total < 2:
                return None
            prob = round(bad / total * 100, 1)
            r = {
                'trigger_label': label,
                'trigger_type': ttype,
                'total_occurrences': total,
                'triggered_reactions': bad,
                'probability': prob,
                'details': details[:5],
            }
            if extra:
                r.update(extra)
            return r

        # Foods
        all_foods: Dict[str, int] = defaultdict(int)
        for e in entries:
            for f in e.foods:
                all_foods[f] += 1
        for food in all_foods:
            r = analyse(
                label=food,
                ttype='food',
                event_filter=lambda e, f=food: f in e.foods,
                extra={'is_nickel_rich': food in NICKEL_RICH_FOODS},
            )
            if r and r['total_occurrences'] >= 3:
                results.append(r)

        # Stress ≥4
        r = analyse("Hoher Stress (≥4)", 'stress',
                    lambda e: e.stress_level is not None and e.stress_level >= 4)
        if r:
            results.append(r)

        # Stress = 5
        r = analyse("Extremer Stress (5)", 'stress',
                    lambda e: e.stress_level == 5)
        if r:
            results.append(r)

        # Fungal active
        r = analyse("Zehenpilz aktiv 🍄", 'fungal',
                    lambda e: e.fungal_active is True)
        if r:
            results.append(r)

        # Bad sleep (≤2)
        r = analyse("Schlechter Schlaf (≤2)", 'sleep',
                    lambda e: e.sleep_quality is not None and e.sleep_quality <= 2)
        if r:
            results.append(r)

        # Good sleep (≥4) — protective factor
        r = analyse("Guter Schlaf (≥4)", 'sleep',
                    lambda e: e.sleep_quality is not None and e.sleep_quality >= 4)
        if r:
            results.append(r)

        # Weather types
        weathers: Dict[str, int] = defaultdict(int)
        for e in entries:
            if e.weather:
                weathers[e.weather] += 1
        for w in weathers:
            r = analyse(f"Wetter: {w}", 'weather',
                        lambda e, ww=w: e.weather == ww)
            if r and r['total_occurrences'] >= 3:
                results.append(r)

        # Sweating
        r = analyse("Starkes Schwitzen 💧", 'sweating',
                    lambda e: e.sweating is True)
        if r:
            results.append(r)

        # Contact exposures
        contact_items: Dict[str, int] = defaultdict(int)
        for e in entries:
            for c in (e.contact_exposures or []):
                contact_items[c] += 1
        for item in contact_items:
            r = analyse(f"Kontakt: {item}", 'contact',
                        lambda e, ci=item: ci in (e.contact_exposures or []))
            if r and r['total_occurrences'] >= 3:
                results.append(r)

        results.sort(key=lambda x: x['probability'], reverse=True)
        return results

    # ── Legacy helpers (kept for backward compat) ──────────────────────────────

    def get_potential_triggers(self, threshold: float = 3.5, min_occurrences: int = 3) -> List[Dict]:
        entries = self.data_manager.get_all_entries()
        return [
            d for d in self._calculate_food_correlations(entries)
            if d['average_severity'] >= threshold and d['count'] >= min_occurrences
        ]

    def get_safe_foods(self, threshold: float = 2.5, min_occurrences: int = 3) -> List[Dict]:
        entries = self.data_manager.get_all_entries()
        safe = [
            d for d in self._calculate_food_correlations(entries)
            if d['average_severity'] <= threshold and d['count'] >= min_occurrences
        ]
        safe.sort(key=lambda x: x['average_severity'])
        return safe

    def get_summary(self, days: int = 30) -> str:
        stats = self.calculate_all(days)
        if stats['total_entries'] == 0:
            return "Noch keine Einträge vorhanden. Beginne mit dem Tracking um Analysen zu erhalten."

        lines = [
            f"Zusammenfassung der letzten {days} Tage:",
            "",
            f"📊 {stats['total_entries']} Einträge erfasst",
            f"📈 Durchschnittliche Schwere: {stats['average_severity']:.1f}",
            f"😊 {stats['good_days']} gute Tage (Schwere 1-2)",
            f"😟 {stats['bad_days']} schlechte Tage (Schwere 4-5)",
        ]
        if stats['average_stress']:
            lines.append(f"😰 Ø Stress: {stats['average_stress']:.1f}")
        if stats['fungal_days']:
            lines.append(f"🍄 Pilz-Tage: {stats['fungal_days']}")
        if stats['average_sleep']:
            lines.append(f"😴 Ø Schlaf: {stats['average_sleep']:.1f}")
        lines.append("")
        triggers = self.get_potential_triggers()
        if triggers:
            lines.append("⚠️ Mögliche Nahrungsmittel-Trigger:")
            for t in triggers[:3]:
                lines.append(f"   • {t['food']} (Ø {t['average_severity']:.1f})")
        return "\n".join(lines)

    def compare_periods(self, period1_days: int, period2_days: int) -> Dict:
        today = date.today()
        p1_end = today
        p1_start = today - timedelta(days=period1_days)
        p1_entries = self.data_manager.get_entries_in_range(p1_start, p1_end)
        p2_end = p1_start - timedelta(days=1)
        p2_start = p2_end - timedelta(days=period2_days)
        p2_entries = self.data_manager.get_entries_in_range(p2_start, p2_end)
        p1_avg = self._calculate_average_severity(p1_entries) if p1_entries else 0
        p2_avg = self._calculate_average_severity(p2_entries) if p2_entries else 0
        return {
            'period1': {'start': p1_start.isoformat(), 'end': p1_end.isoformat(),
                        'entries': len(p1_entries), 'average_severity': p1_avg},
            'period2': {'start': p2_start.isoformat(), 'end': p2_end.isoformat(),
                        'entries': len(p2_entries), 'average_severity': p2_avg},
            'change': round(p1_avg - p2_avg, 2),
            'improved': p1_avg < p2_avg,
        }

    def get_pattern_summary(self, delay_days: int = 2) -> str:
        patterns = self.detect_patterns(delay_days)
        if not patterns:
            return "Noch nicht genügend Daten für Muster-Erkennung. Mindestens 5 Einträge erforderlich."
        lines = [f"Muster-Analyse (Zeitfenster: {delay_days} Tage)\n"]
        high = [p for p in patterns if p['probability'] >= 50]
        mid = [p for p in patterns if 25 <= p['probability'] < 50]
        if high:
            lines.append("⚠️ Hohe Wahrscheinlichkeit (>50%):")
            for p in high[:3]:
                lines.append(f"   • {p['food']}: {p['probability']}% ({p['triggered_reactions']}/{p['total_occurrences']} mal)")
        if mid:
            lines.append("\n⚡ Mittlere Wahrscheinlichkeit (25-50%):")
            for p in mid[:3]:
                lines.append(f"   • {p['food']}: {p['probability']}% ({p['triggered_reactions']}/{p['total_occurrences']} mal)")
        return "\n".join(lines)
