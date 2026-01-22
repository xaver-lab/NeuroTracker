# Neuro-Tracker 🩺

Eine Python Desktop-Anwendung zur Erfassung und Analyse von Neurodermitis-Verläufen mit Fokus auf Nahrungsmittel-Zusammenhänge.

## 📋 Übersicht

Neuro-Tracker hilft dir dabei, deinen Neurodermitis-Verlauf systematisch zu dokumentieren und mögliche Zusammenhänge mit der Ernährung zu identifizieren. Die Anwendung bietet eine intuitive Kalenderansicht, einfache Dateneingabe und aussagekräftige Statistiken.

## ✨ Hauptfunktionen

### Datenerfassung
- **Täglicher Schweregrad**: Bewertung von 1-5 für den allgemeinen Hautzustand
- **Lebensmittel-Tracking**: Erfassung gegessener Lebensmittel mit intelligenten Vorschlägen
- **Notizfeld**: Optionale Notizen zu jedem Tag (Stress, Wetter, Schlaf, etc.)
- **Schnelle Bearbeitung**: Jeder Tag kann über ein Bearbeiten-Symbol nachträglich angepasst werden

### Benutzeroberfläche
- **Wochenansicht**: Übersichtliche Darstellung von 2 Wochen (aktuelle + letzte Woche)
- **Navigation**: Einfaches Blättern durch vergangene Wochen
- **Eingabe-Panel**: Permanente linke Spalte für schnelle Einträge
  - Standardmäßig vorausgewählt: Aktueller Tag
  - Andere Tage auswählbar
  - Speichern-Button für jeden Eintrag

### Analyse & Export
- **Statistiken**: Graphische Darstellung von Trends und Mustern
- **Charts**: Visualisierung von Zusammenhängen zwischen Ernährung und Symptomen
- **Export-Funktion**: Daten als CSV/PDF für Arztbesuche exportieren

### Synchronisation
- **Google Drive Integration**: Automatische Synchronisation zwischen mehreren PCs
- **Offline-Fähig**: Arbeiten auch ohne Internetverbindung möglich
- **Automatisches Backup**: Regelmäßige Sicherung deiner Daten

## 🏗️ Projektstruktur

```
Neuro-Tracker/
├── README.md                    # Diese Datei
├── requirements.txt             # Python-Dependencies
├── main.py                      # Einstiegspunkt der Anwendung
├── config.py                    # Konfiguration (Pfade, Einstellungen)
│
├── data/                        # Lokale Datenspeicherung
│   ├── entries.json             # Tägliche Einträge
│   ├── food_suggestions.json    # Lebensmittel-Vorschläge
│   └── settings.json            # Benutzereinstellungen
│
├── ui/                          # User Interface Komponenten
│   ├── __init__.py
│   ├── main_window.py           # Hauptfenster & Layout
│   ├── calendar_widget.py       # Wochen-Kalender-Ansicht
│   ├── entry_panel.py           # Eingabe-Panel (linke Spalte)
│   ├── day_card.py              # Einzelner Tag im Kalender
│   ├── statistics_dialog.py     # Statistik-Fenster
│   └── styles.py                # QSS Styling (Design)
│
├── models/                      # Datenmodelle & Logik
│   ├── __init__.py
│   ├── day_entry.py             # Datenmodell für einen Tag
│   ├── data_manager.py          # Speichern/Laden von Daten
│   └── food_manager.py          # Verwaltung von Lebensmitteln
│
├── utils/                       # Hilfsfunktionen
│   ├── __init__.py
│   ├── google_drive.py          # Google Drive Synchronisation
│   ├── statistics.py            # Statistik-Berechnungen
│   ├── export.py                # Export zu CSV/PDF
│   └── validators.py            # Eingabe-Validierung
│
├── resources/                   # Ressourcen (Icons, Bilder)
│   └── icons/
│       ├── edit.png
│       ├── save.png
│       └── stats.png
│
└── tests/                       # Unit-Tests
    ├── __init__.py
    ├── test_day_entry.py
    └── test_data_manager.py
```

## 🚀 Installation

### Voraussetzungen
- Python 3.8 oder höher
- pip (Python Package Manager)

### Schritt-für-Schritt Anleitung

1. **Repository klonen**
   ```bash
   git clone https://github.com/your-username/Neuro-Tracker.git
   cd Neuro-Tracker
   ```

2. **Virtual Environment erstellen** (empfohlen)
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Dependencies installieren**
   ```bash
   pip install -r requirements.txt
   ```

4. **Google Drive Synchronisation einrichten** (optional)
   - Google Cloud Projekt erstellen
   - Drive API aktivieren
   - Credentials herunterladen und als `credentials.json` im Projektordner speichern

5. **Anwendung starten**
   ```bash
   python main.py
   ```

## 🔧 Technologie-Stack

- **GUI Framework**: PyQt5 (moderne, plattformübergreifende Desktop-UI)
- **Datenformat**: JSON (einfach, lesbar, portabel)
- **Charts**: matplotlib / pyqtgraph (für Statistiken)
- **Google Drive**: google-api-python-client (Synchronisation)
- **Export**: reportlab (PDF) / pandas (CSV)

## 📊 Datenmodell

### Tag-Eintrag (DayEntry)
```python
{
    "date": "2026-01-22",
    "severity": 3,                    # Schweregrad 1-5
    "foods": ["Tomaten", "Milch"],    # Liste von Lebensmitteln
    "notes": "Viel Stress heute",     # Optional
    "created_at": "2026-01-22T10:30:00",
    "updated_at": "2026-01-22T10:30:00"
}
```

## 🎯 Geplante Features (Roadmap)

- [ ] **v1.0 - Grundfunktionen**
  - [x] Projektstruktur
  - [ ] Kalenderansicht mit 2 Wochen
  - [ ] Eingabe-Panel für neue Einträge
  - [ ] Daten lokal speichern (JSON)
  - [ ] Bearbeiten bestehender Einträge

- [ ] **v1.1 - Synchronisation**
  - [ ] Google Drive Integration
  - [ ] Automatisches Backup
  - [ ] Konflikt-Auflösung bei mehreren PCs

- [ ] **v1.2 - Analyse**
  - [ ] Basis-Statistiken (Durchschnittswerte, Trends)
  - [ ] Korrelation Essen ↔ Schweregrad
  - [ ] Häufigste Trigger-Lebensmittel

- [ ] **v1.3 - Erweiterte Features**
  - [ ] Export zu CSV/PDF
  - [ ] Interaktive Charts
  - [ ] Dunkler Modus (Dark Mode)
  - [ ] Mehrsprachigkeit (DE/EN)

- [ ] **v2.0 - Advanced**
  - [ ] KI-gestützte Muster-Erkennung
  - [ ] Lebensmittel-Kategorien
  - [ ] Mehrere Körperstellen tracken

## 🤝 Mitwirken

Contributions sind willkommen! Wenn du Ideen oder Verbesserungsvorschläge hast:

1. Fork das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

## 📝 Lizenz

Dieses Projekt ist unter der MIT-Lizenz veröffentlicht - siehe [LICENSE](LICENSE) für Details.

## 💡 Verwendung

### Ersten Eintrag erstellen
1. Starte die Anwendung
2. Das Eingabe-Panel links zeigt automatisch den heutigen Tag
3. Wähle den Schweregrad (1-5)
4. Füge Lebensmittel hinzu (mit Tab-Taste für Vorschläge)
5. Optional: Notizen hinzufügen
6. Klicke auf "Speichern"

### Vergangene Tage bearbeiten
1. Klicke auf das Bearbeiten-Symbol ✏️ im entsprechenden Tag
2. Der Tag wird ins Eingabe-Panel geladen
3. Nimm deine Änderungen vor
4. Klicke auf "Speichern"

### Statistiken ansehen
1. Klicke auf den "Statistiken"-Button in der Toolbar
2. Wähle den Zeitraum aus
3. Betrachte Charts und Korrelationen

## 🐛 Bekannte Probleme & FAQ

**Q: Wie oft wird mit Google Drive synchronisiert?**
A: Automatisch bei jedem Speichern + alle 5 Minuten im Hintergrund.

**Q: Kann ich die App ohne Google Drive nutzen?**
A: Ja! Die App funktioniert vollständig offline mit lokaler Speicherung.

**Q: Sind meine Daten sicher?**
A: Alle Daten werden nur lokal und in deinem persönlichen Google Drive gespeichert. Keine Cloud-Server.

## 📧 Kontakt

Bei Fragen oder Problemen erstelle bitte ein [Issue](https://github.com/your-username/Neuro-Tracker/issues).

---

**Hinweis**: Diese Software dient nur zur persönlichen Dokumentation und ersetzt keine ärztliche Beratung.