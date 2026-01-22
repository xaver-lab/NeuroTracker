"""
Export Manager for Neuro-Tracker Application
Handles CSV and PDF export/import of tracking data
"""

import csv
import json
from datetime import date, datetime
from typing import Tuple, List, Optional
from pathlib import Path

from config import EXPORT_CSV_DELIMITER, EXPORT_DATE_FORMAT, SEVERITY_COLORS
from models.data_manager import DataManager
from models.day_entry import DayEntry


class ExportManager:
    """
    Handles export and import of tracking data to various formats.
    """

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    def export_csv(self, filepath: str, entries: List[DayEntry] = None) -> Tuple[bool, str]:
        """
        Export entries to CSV file.

        Args:
            filepath: Path to save the CSV file
            entries: Optional list of entries. If None, exports all entries.

        Returns:
            Tuple of (success, message)
        """
        try:
            if entries is None:
                entries = self.data_manager.get_all_entries()

            if not entries:
                return False, "Keine Einträge zum Exportieren vorhanden."

            # Sort by date
            entries = sorted(entries, key=lambda x: x.date)

            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=EXPORT_CSV_DELIMITER)

                # Header
                writer.writerow([
                    'Datum',
                    'Wochentag',
                    'Schweregrad',
                    'Lebensmittel',
                    'Notizen',
                    'Erstellt',
                    'Aktualisiert'
                ])

                weekdays = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']

                for entry in entries:
                    entry_date = date.fromisoformat(entry.date)
                    weekday = weekdays[entry_date.weekday()]

                    writer.writerow([
                        entry_date.strftime(EXPORT_DATE_FORMAT),
                        weekday,
                        entry.severity,
                        ', '.join(entry.foods),
                        entry.notes or '',
                        entry.created_at or '',
                        entry.updated_at or ''
                    ])

            return True, f"Erfolgreich {len(entries)} Einträge nach {filepath} exportiert."

        except Exception as e:
            return False, f"Fehler beim Export: {str(e)}"

    def export_pdf(self, filepath: str, entries: List[DayEntry] = None,
                   title: str = "Neuro-Tracker Bericht") -> Tuple[bool, str]:
        """
        Export entries to PDF report.

        Args:
            filepath: Path to save the PDF file
            entries: Optional list of entries. If None, exports all entries.
            title: Title for the PDF report

        Returns:
            Tuple of (success, message)
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.platypus import (
                SimpleDocTemplate, Table, TableStyle, Paragraph,
                Spacer, PageBreak
            )
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
        except ImportError:
            return False, "ReportLab ist nicht installiert. Bitte 'pip install reportlab' ausführen."

        try:
            if entries is None:
                entries = self.data_manager.get_all_entries()

            if not entries:
                return False, "Keine Einträge zum Exportieren vorhanden."

            # Sort by date (newest first for report)
            entries = sorted(entries, key=lambda x: x.date, reverse=True)

            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )

            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(
                name='CenteredTitle',
                parent=styles['Heading1'],
                alignment=TA_CENTER,
                spaceAfter=30
            ))

            story = []

            # Title
            story.append(Paragraph(title, styles['CenteredTitle']))

            # Summary
            from utils.statistics import StatisticsCalculator
            stats_calc = StatisticsCalculator(self.data_manager)
            stats = stats_calc.calculate_all(30)

            summary_text = f"""
            <b>Zusammenfassung (letzte 30 Tage):</b><br/>
            Einträge: {stats['total_entries']}<br/>
            Durchschnittliche Schwere: {stats['average_severity']:.1f}<br/>
            Gute Tage: {stats['good_days']} | Schlechte Tage: {stats['bad_days']}<br/>
            <br/>
            Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M')}
            """
            story.append(Paragraph(summary_text, styles['Normal']))
            story.append(Spacer(1, 20))

            # Entries table
            weekdays = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']

            table_data = [['Datum', 'Tag', 'Schwere', 'Lebensmittel', 'Notizen']]

            for entry in entries:
                entry_date = date.fromisoformat(entry.date)
                weekday = weekdays[entry_date.weekday()]

                foods_text = ', '.join(entry.foods[:5])
                if len(entry.foods) > 5:
                    foods_text += f' (+{len(entry.foods) - 5})'

                notes_text = (entry.notes or '')[:50]
                if entry.notes and len(entry.notes) > 50:
                    notes_text += '...'

                table_data.append([
                    entry_date.strftime('%d.%m.%Y'),
                    weekday,
                    str(entry.severity),
                    foods_text,
                    notes_text
                ])

            # Create table
            table = Table(table_data, colWidths=[2.5*cm, 1.2*cm, 1.5*cm, 7*cm, 4*cm])

            # Severity colors for rows
            severity_colors_rgb = {
                1: colors.Color(0.298, 0.686, 0.314),  # Green
                2: colors.Color(0.545, 0.765, 0.290),  # Light green
                3: colors.Color(1.0, 0.757, 0.027),    # Yellow
                4: colors.Color(1.0, 0.596, 0.0),      # Orange
                5: colors.Color(0.957, 0.263, 0.212),  # Red
            }

            style_commands = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.13, 0.59, 0.95)),  # Header blue
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (3, 1), (4, -1), 'LEFT'),  # Left align foods and notes
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
            ]

            # Add severity coloring
            for row_idx, entry in enumerate(entries, start=1):
                severity = entry.severity
                if severity in severity_colors_rgb:
                    style_commands.append(
                        ('BACKGROUND', (2, row_idx), (2, row_idx),
                         severity_colors_rgb[severity])
                    )
                    style_commands.append(
                        ('TEXTCOLOR', (2, row_idx), (2, row_idx), colors.white)
                    )

            table.setStyle(TableStyle(style_commands))
            story.append(table)

            # Build PDF
            doc.build(story)

            return True, f"PDF-Bericht erfolgreich nach {filepath} exportiert."

        except Exception as e:
            return False, f"Fehler beim PDF-Export: {str(e)}"

    def import_data(self, filepath: str) -> Tuple[bool, str]:
        """
        Import data from CSV or JSON file.

        Args:
            filepath: Path to the file to import

        Returns:
            Tuple of (success, message)
        """
        path = Path(filepath)

        if path.suffix.lower() == '.csv':
            return self._import_csv(filepath)
        elif path.suffix.lower() == '.json':
            return self._import_json(filepath)
        else:
            return False, f"Nicht unterstütztes Dateiformat: {path.suffix}"

    def _import_csv(self, filepath: str) -> Tuple[bool, str]:
        """Import from CSV file"""
        try:
            imported = 0
            skipped = 0

            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=EXPORT_CSV_DELIMITER)

                for row in reader:
                    try:
                        # Parse date
                        date_str = row.get('Datum', '')
                        if not date_str:
                            skipped += 1
                            continue

                        # Try different date formats
                        entry_date = None
                        for fmt in [EXPORT_DATE_FORMAT, '%Y-%m-%d', '%d/%m/%Y']:
                            try:
                                entry_date = datetime.strptime(date_str, fmt).date()
                                break
                            except ValueError:
                                continue

                        if entry_date is None:
                            skipped += 1
                            continue

                        # Parse severity
                        severity_str = row.get('Schweregrad', row.get('Schwere', ''))
                        try:
                            severity = int(severity_str)
                            if not (1 <= severity <= 5):
                                severity = 3
                        except (ValueError, TypeError):
                            severity = 3

                        # Parse foods
                        foods_str = row.get('Lebensmittel', '')
                        foods = [f.strip() for f in foods_str.split(',') if f.strip()]

                        # Parse notes
                        notes = row.get('Notizen', '') or None

                        # Create entry
                        entry = DayEntry(
                            date=entry_date.isoformat(),
                            severity=severity,
                            foods=foods,
                            notes=notes
                        )

                        self.data_manager.add_or_update_entry(entry)
                        imported += 1

                    except Exception:
                        skipped += 1
                        continue

            return True, f"Import abgeschlossen: {imported} Einträge importiert, {skipped} übersprungen."

        except Exception as e:
            return False, f"Fehler beim CSV-Import: {str(e)}"

    def _import_json(self, filepath: str) -> Tuple[bool, str]:
        """Import from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                data = [data]

            imported = 0
            skipped = 0

            for item in data:
                try:
                    entry = DayEntry.from_dict(item)
                    self.data_manager.add_or_update_entry(entry)
                    imported += 1
                except Exception:
                    skipped += 1
                    continue

            return True, f"Import abgeschlossen: {imported} Einträge importiert, {skipped} übersprungen."

        except json.JSONDecodeError:
            return False, "Ungültiges JSON-Format."
        except Exception as e:
            return False, f"Fehler beim JSON-Import: {str(e)}"

    def export_json(self, filepath: str, entries: List[DayEntry] = None) -> Tuple[bool, str]:
        """
        Export entries to JSON file (backup format).

        Args:
            filepath: Path to save the JSON file
            entries: Optional list of entries. If None, exports all entries.

        Returns:
            Tuple of (success, message)
        """
        try:
            if entries is None:
                entries = self.data_manager.get_all_entries()

            if not entries:
                return False, "Keine Einträge zum Exportieren vorhanden."

            data = [entry.to_dict() for entry in entries]

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return True, f"Erfolgreich {len(entries)} Einträge nach {filepath} exportiert."

        except Exception as e:
            return False, f"Fehler beim JSON-Export: {str(e)}"

    def create_backup(self) -> Tuple[bool, str]:
        """
        Create a timestamped backup of all data.

        Returns:
            Tuple of (success, filepath or error message)
        """
        from config import DATA_DIR

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = DATA_DIR / 'backups'
        backup_dir.mkdir(exist_ok=True)

        backup_path = backup_dir / f'backup_{timestamp}.json'

        success, message = self.export_json(str(backup_path))

        if success:
            return True, str(backup_path)
        return False, message
