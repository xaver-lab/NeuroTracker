# Neuro-Tracker 🩺

Eine Python-Anwendung zur Erfassung und Analyse von Neurodermitis-Verläufen mit Fokus auf Trigger-Erkennung — verfügbar als **Desktop-App (PyQt5)** und **Android-App (KivyMD)**.

## Übersicht

Neuro-Tracker hilft dir dabei, deinen Neurodermitis-Verlauf systematisch zu dokumentieren und mögliche Zusammenhänge mit Ernährung, Stress, Schlaf, Wetter und weiteren Faktoren zu identifizieren. Beide Versionen teilen sich dasselbe Daten-Backend und können über Google Drive synchronisiert werden.

## Hauptfunktionen

### Tägliche Datenerfassung
- **Schweregrad**: Bewertung von 1-5 mit Farbcodierung (grün bis rot)
- **Lebensmittel-Tracking**: Auswahl aus 50+ vordefinierten Lebensmitteln mit Emoji-Icons
- **Notizfelder**: Separate Notizen für Hautzustand und Nahrung
- **Schnelle Bearbeitung**: Jeden Tag im Kalender anklicken und bearbeiten

### Modulares Trigger-System
Individuell aktivierbare Module zur Erfassung zusätzlicher Trigger:

| Modul | Beschreibung | Standard |
|-------|-------------|----------|
| Stresslevel | Skala 1-5 | Aktiviert |
| Zehenpilz (Mykose) | Ja/Nein — Id-Reaktion tracken | Aktiviert |
| Schlafqualität | Skala 1-5 (invertiert: 5 = am besten) | Aktiviert |
| Wetter / Umgebung | 6 Kategorien (Normal, Trocken, Feucht, etc.) | Aktiviert |
| Schwitzen | Ja/Nein | Deaktiviert |
| Kontaktexposition | Nickel, Latex, Desinfektionsmittel, etc. | Deaktiviert |

### Benutzeroberfläche

**Desktop (PyQt5)**:
- 2-Wochen-Kalenderansicht (aktuelle + letzte Woche)
- Permanentes Eingabe-Panel als linke Seitenleiste mit Tabs (Hautzustand, Lebensmittel, Trigger)
- Menüleiste mit Datei, Bearbeiten, Ansicht, Statistiken, Hilfe
- Statusleiste mit Sync-Status und Durchschnittswerten

**Android (KivyMD)**:
- Material Design 3 mit Bottom-Navigation (Heute, Kalender, Statistiken, Einstellungen)
- Kategorisierte Lebensmittel-Auswahl (Milch, Gemüse, Obst, Getreide, Proteine, Nüsse, Sonstiges)
- Expandierbare Sheets mit Suchfunktion

### Muster-Erkennung & Statistiken
Die App analysiert automatisch Zusammenhänge zwischen Triggern und Hautzustand:

- **Wahrscheinlichkeitsberechnung**: Wie oft folgt auf ein Lebensmittel ein schlechter Tag?
- **Farbcodierung**: Rot (>50% — Trigger), Orange (25-50% — beobachten), Grün (<25% — verträglich)
- **Zeitfenster**: Einstellbar 1-5 Tage nach Verzehr
- **Weitere Metriken**: Durchschnittswerte, Trends, Streaks, Wochentag-Muster, Stress-/Schlaf-/Wetter-Korrelationen

### Synchronisation & Export
- **Google Drive**: Automatische Synchronisation alle 5 Minuten + bei jedem Speichern
- **Offline-fähig**: Arbeitet vollständig ohne Internet, synchronisiert bei Reconnect
- **Konfliktauflösung**: Server-Timestamp (UTC) hat Vorrang
- **Export**: CSV (Semikolon-getrennt) und PDF für Arztbesuche

## Projektstruktur

```
NeuroTracker/
├── main.py                      # Desktop-Einstiegspunkt (PyQt5)
├── main_android.py              # Android-Einstiegspunkt (KivyMD)
├── config.py                    # Zentrale Konfiguration
├── buildozer.spec               # Android-Build-Konfiguration
├── requirements.txt             # Desktop-Dependencies
├── requirements_android.txt     # Android-Dependencies
│
├── ui/                          # Desktop-UI (PyQt5)
│   ├── main_window.py           # Hauptfenster & Layout
│   ├── calendar_widget.py       # 2-Wochen-Kalender
│   ├── entry_panel.py           # Eingabe-Panel (linke Spalte)
│   ├── day_card.py              # Einzelner Tag im Kalender
│   ├── statistics_dialog.py     # Statistik-Fenster
│   └── styles.py                # QSS Styling
│
├── mobile_ui/                   # Android-UI (KivyMD)
│   ├── entry_screen.py          # Tageseintrag-Screen
│   ├── calendar_screen.py       # Monatskalender
│   ├── stats_screen.py          # Statistiken & Muster
│   ├── day_detail_screen.py     # Tagesdetail-Ansicht
│   └── settings_screen.py       # Modul-Einstellungen
│
├── models/                      # Datenmodelle (geteilt)
│   ├── day_entry.py             # DayEntry-Klasse
│   ├── data_manager.py          # JSON-Persistenz
│   ├── food_manager.py          # Lebensmittel-Verwaltung
│   └── settings_manager.py      # Modul-Einstellungen
│
├── utils/                       # Business-Logik (geteilt)
│   ├── statistics.py            # Trigger-Analyse-Engine
│   ├── google_drive.py          # Google Drive Synchronisation
│   ├── export.py                # CSV/PDF-Export
│   └── validators.py            # Eingabe-Validierung
│
└── data/                        # Lokale Datenspeicherung
    ├── entries.json             # Tägliche Einträge
    ├── food_suggestions.json    # Lebensmittel-Vorschläge
    └── settings.json            # Modul-Konfiguration
```

## Installation

### Desktop (PyQt5)

**Voraussetzungen:** Python 3.8+

```bash
git clone https://github.com/xaver-lab/Neuro-Tracker.git
cd Neuro-Tracker

python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

pip install -r requirements.txt
python main.py
```

**Google Drive einrichten** (optional):
1. Google Cloud Projekt erstellen und Drive API aktivieren
2. Credentials herunterladen als `credentials.json` im Projektordner

### Android (KivyMD)

**Voraussetzungen:** Python 3.8+, Java JDK 11+, Android SDK (API 33), Android NDK 25b

```bash
pip install -r requirements_android.txt
buildozer android debug
```

Die APK befindet sich danach in `bin/`. Auf ein Android-Gerät (7.0+) übertragen und installieren.

## Technologie-Stack

| Komponente | Desktop | Android |
|-----------|---------|---------|
| GUI | PyQt5 5.15.10+ | KivyMD 1.2.0 (Material Design 3) |
| Build | PyInstaller | Buildozer 1.5.0+ |
| Datenformat | JSON | JSON |
| Charts | matplotlib / pyqtgraph | — |
| Cloud-Sync | Google Drive API | Google Drive API |
| PDF-Export | reportlab 4.0.7+ | — |

## Datenmodell

### Tag-Eintrag (DayEntry)
```python
{
    "date": "2026-01-22",
    "severity": 3,                           # Schweregrad 1-5
    "foods": ["Tomaten", "Milch"],           # Lebensmittel
    "notes": "Viel Stress heute",            # Allgemeine Notizen
    "skin_notes": "Risse an Fingern",        # Haut-spezifisch
    "food_notes": "Großer Salat mittags",    # Nahrungs-spezifisch
    "stress_level": 4,                       # Trigger: Stress 1-5
    "fungal_active": true,                   # Trigger: Mykose aktiv
    "sleep_quality": 2,                      # Trigger: Schlaf 1-5
    "weather": "Trocken / Heizungsluft",     # Trigger: Wetter
    "sweating": false,                       # Trigger: Schwitzen
    "contact_exposures": ["Nickel"],         # Trigger: Kontakt
    "created_at": "2026-01-22T10:30:00",
    "updated_at": "2026-01-22T10:30:00"
}
```

## Roadmap

- [x] **v1.0** — Kalenderansicht, Eingabe-Panel, lokale JSON-Speicherung
- [x] **v1.1** — Google Drive Synchronisation, automatisches Backup
- [x] **v1.2** — Statistiken, Muster-Erkennung, Trigger-Wahrscheinlichkeiten, modulares Trigger-System
- [x] **v1.2-android** — Android-App mit KivyMD, kategorisierte Lebensmittel, Settings-Screen
- [ ] **v1.3** — CSV/PDF-Export verfeinern, interaktive Charts, Dark Mode, Mehrsprachigkeit (DE/EN)
- [ ] **v2.0** — Mehrere Körperstellen tracken, Kontakt-Allergen-Historie, Medikamenten-Tracking

## Verwendung

### Ersten Eintrag erstellen
1. Starte die Anwendung (`python main.py` oder Android-App)
2. Wähle den Schweregrad (1-5) und füge optional Notizen hinzu
3. Wähle die gegessenen Lebensmittel aus
4. Erfasse weitere Trigger (Stress, Schlaf, etc.) im Trigger-Tab
5. Klicke auf "Speichern"

### Muster-Erkennung nutzen
1. Öffne die Statistiken (Desktop: Toolbar-Button, Android: Tab "Statistiken")
2. Stelle das Zeitfenster ein (Tage nach Verzehr) und den Schwellenwert
3. Die Tabelle zeigt erkannte Muster mit Wahrscheinlichkeiten und Farbcodierung

## FAQ

**Wie oft wird mit Google Drive synchronisiert?**
Automatisch bei jedem Speichern + alle 5 Minuten im Hintergrund.

**Kann ich die App ohne Google Drive nutzen?**
Ja, die App funktioniert vollständig offline mit lokaler Speicherung.

**Sind meine Daten sicher?**
Alle Daten werden nur lokal und in deinem persönlichen Google Drive gespeichert. Keine externen Cloud-Server.

## Mitwirken

Contributions sind willkommen! Fork das Repository, erstelle einen Feature-Branch und öffne einen Pull Request.

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz veröffentlicht — siehe [LICENSE](LICENSE) für Details.

---

**Hinweis**: Diese Software dient nur zur persönlichen Dokumentation und ersetzt keine ärztliche Beratung.
