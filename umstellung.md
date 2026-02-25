# NeuroTracker Android – Umstellungs-Prompt

## Ziel
Erstelle eine Android-Version von NeuroTracker mit **KivyMD** (Material Design für Python/Kivy).
Die Desktop-Version (PyQt5) bleibt unverändert bestehen. Beide Versionen teilen dieselben
Daten über Google Drive (bereits implementiert).

---

## Ausgangslage

### Bestehende Desktop-App (NICHT anfassen)
- Framework: Python 3.8+ / PyQt5
- Einstiegspunkt: `main.py`
- UI: `ui/` (PyQt5 – nicht wiederverwendbar)
- Logik: `models/`, `utils/` (wiederverwendbar!)
- Daten: Lokale JSON-Dateien + Google Drive Sync

### Wiederverwendbare Module (1:1 übernehmen)
| Datei | Inhalt | Wiederverwendbar? |
|---|---|---|
| `models/day_entry.py` | DayEntry Datenmodell | **Ja, komplett** |
| `models/data_manager.py` | JSON Lesen/Schreiben | **Ja, komplett** |
| `models/food_manager.py` | Lebensmittelliste | **Ja, komplett** |
| `utils/statistics.py` | Auswertungslogik | **Ja, komplett** |
| `utils/validators.py` | Eingabevalidierung | **Ja, komplett** |
| `utils/google_drive.py` | Drive Sync | **Ja, mit Anpassungen** |
| `config.py` | Farben, Konstanten | **Teilweise** |
| `utils/export.py` | CSV/PDF Export | **Optional** |

### Nicht wiederverwendbar (komplett neu schreiben)
- `ui/main_window.py` → `mobile_ui/main_screen.py`
- `ui/calendar_widget.py` → `mobile_ui/calendar_screen.py`
- `ui/entry_panel.py` → `mobile_ui/entry_screen.py`
- `ui/day_card.py` → `mobile_ui/day_detail_screen.py`
- `ui/statistics_dialog.py` → `mobile_ui/stats_screen.py`
- `ui/styles.py` → KivyMD Theme (ersetzt durch Material Design)

---

## Neue Projektstruktur

```
NeuroTracker/
├── main.py                    # Desktop-Einstiegspunkt (unverändert)
├── main_android.py            # NEU: Android-Einstiegspunkt
├── config.py                  # Gemeinsam (leicht angepasst)
├── requirements.txt           # Desktop-Abhängigkeiten (unverändert)
├── requirements_android.txt   # NEU: KivyMD-Abhängigkeiten
├── buildozer.spec             # NEU: Android Build-Konfiguration
│
├── models/                    # UNVERÄNDERT (geteilt)
│   ├── day_entry.py
│   ├── data_manager.py
│   └── food_manager.py
│
├── utils/                     # UNVERÄNDERT (geteilt)
│   ├── statistics.py
│   ├── validators.py
│   ├── google_drive.py
│   └── export.py
│
├── mobile_ui/                 # NEU: KivyMD Screens
│   ├── __init__.py
│   ├── main_screen.py         # Startseite / Navigation
│   ├── entry_screen.py        # Tageseintrag (Severity + Essen)
│   ├── calendar_screen.py     # 2-Wochen Kalender
│   ├── day_detail_screen.py   # Detailansicht eines Tages
│   └── stats_screen.py        # Statistiken & Muster
│
└── data/                      # UNVERÄNDERT (geteilt)
    ├── entries.json
    └── food_suggestions.json
```

---

## Technische Anforderungen

### Neue Abhängigkeiten (requirements_android.txt)
```
kivy>=2.3.0
kivymd>=1.2.0
buildozer>=1.5.0
```

### KivyMD Theme (entspricht bestehenden Farben aus config.py)
```python
# main_android.py
from kivymd.app import MDApp

class NeuroTrackerApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"       # COLOR_PRIMARY = #2196F3
        self.theme_cls.accent_palette  = "Amber"      # COLOR_SECONDARY = #FFC107
        self.theme_cls.theme_style     = "Light"      # COLOR_BACKGROUND = #FAFAFA
```

---

## Screen-für-Screen Umsetzung

### Screen 1: Entry Screen (Haupt-Screen)
**Ersetzt:** `ui/entry_panel.py` + `ui/main_window.py`

Komponenten:
- `MDTopAppBar` – Titel "NeuroTracker" + Datum
- `MDSlider` – Schweregrad 1–5 (mit Farbwechsel wie SEVERITY_COLORS)
- `MDChip`-Liste – Lebensmittel aus `food_manager.py` (mit Emojis aus config.py)
- `MDTextField` – Notizen (Haut / Ernährung)
- `MDRaisedButton` – Speichern → `data_manager.save_entry()`
- `MDBottomNavigation` – Navigation zu anderen Screens

### Screen 2: Kalender Screen
**Ersetzt:** `ui/calendar_widget.py` + `ui/day_card.py`

Komponenten:
- `MDTopAppBar` – Titel + Woche vor/zurück Buttons
- Scroll-Grid (7 Spalten) – Kalenderansicht
- Farbige Tages-Karten (`MDCard`) – Farbe aus SEVERITY_COLORS
- Tap auf Tag → Day Detail Screen

### Screen 3: Tag-Detail Screen
**Ersetzt:** `ui/day_card.py` (Detail-Dialog)

Komponenten:
- `MDTopAppBar` – Datum + Zurück-Button
- `MDCard` – Schweregrad mit Farbe
- `MDList` – gegessene Lebensmittel mit Emojis
- `MDTextField` (readonly) – Notizen

### Screen 4: Statistiken Screen
**Ersetzt:** `ui/statistics_dialog.py`

Komponenten:
- `MDTopAppBar` – "Statistiken"
- `MDCard` – Durchschnittlicher Schweregrad
- `MDList` – Lebensmittel-Korrelationen (Ampelfarben: Rot/Orange/Grün)
- Zeitfenster-Einstellung (1–5 Tage) via `MDSlider`

---

## Navigation (Bottom Navigation Bar)

```
[ 📝 Heute ] [ 📅 Kalender ] [ 📊 Statistiken ]
```

Implementierung mit `MDBottomNavigation` aus KivyMD.

---

## Datensynchronisation

Die bestehende `utils/google_drive.py` wird wiederverwendet.
Auf Android muss der OAuth-Flow angepasst werden:
- Desktop: Browser-basiert (funktioniert so)
- Android: Anpassung für Android OAuth oder token.json manuell einbinden

```python
# Workaround für Android: Token aus Google Drive laden
# (Token einmalig auf Desktop erstellen, dann per Drive synchronisieren)
```

---

## Build & Test

### Lokal in VS Code testen (kein Emulator nötig)
```bash
pip install kivymd
python main_android.py
# → Öffnet als Desktop-Fenster, Touch-Events via Maus simulierbar
```

### Android APK bauen
```bash
pip install buildozer
buildozer init          # Erstellt buildozer.spec
buildozer android debug # Baut APK (braucht Linux oder WSL)
# → Output: bin/NeuroTracker-1.0-arm64-v8a-debug.apk
```

### APK auf Handy installieren
```bash
# USB-Debugging aktivieren, dann:
buildozer android deploy run
# Oder APK manuell auf Handy kopieren und installieren
```

---

## Umsetzungs-Reihenfolge

1. `requirements_android.txt` erstellen
2. `main_android.py` – App-Grundgerüst mit Theme + Navigation
3. `mobile_ui/entry_screen.py` – Tageseintrag (wichtigster Screen)
4. `mobile_ui/calendar_screen.py` – Kalenderansicht
5. `mobile_ui/day_detail_screen.py` – Detailansicht
6. `mobile_ui/stats_screen.py` – Statistiken
7. `buildozer.spec` – Android Build-Konfiguration
8. Test auf Desktop (VS Code)
9. APK-Build und Test auf echtem Gerät

---

## Wichtige Einschränkungen

- **Google Drive OAuth auf Android:** Benötigt Anpassung oder manuellen Token-Transfer
- **reportlab (PDF-Export):** Funktioniert möglicherweise nicht auf Android → Optional weglassen
- **Dateipfade auf Android:** `data/` muss auf Android-Speicher angepasst werden
  ```python
  from kivy.utils import platform
  if platform == 'android':
      from android.storage import app_storage_path
      DATA_DIR = Path(app_storage_path()) / "data"
  ```

---

## Erfolgskriterien

- [ ] App startet auf Android ohne Absturz
- [ ] Tageseintrag (Schweregrad + Essen + Notizen) speichern funktioniert
- [ ] Kalender zeigt vergangene Einträge korrekt an
- [ ] Statistiken berechnen Lebensmittel-Korrelationen
- [ ] Google Drive Sync funktioniert (zumindest manuell auslösbar)
- [ ] Bestehende Desktop-App läuft weiterhin unverändert
