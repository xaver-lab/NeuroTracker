# NeuroTracker – Build-Anleitung

NeuroTracker hat zwei Plattform-Targets:

| Plattform | Framework | Entry Point | Build-Tool |
|-----------|-----------|-------------|------------|
| Desktop (Win/Linux/macOS) | PyQt5 | `main.py` | PyInstaller |
| Android | KivyMD 1.2.0 | `main_android.py` | Buildozer |

> **Tipp:** Alle Build-Targets sind auch über das `Makefile` aufrufbar (siehe unten).

---

## 1  Voraussetzungen

### Desktop

```bash
pip install -r requirements.txt
pip install pyinstaller
```

### Android

```bash
pip install -r requirements_android.txt

# Zusätzlich auf Linux (Ubuntu/Debian) für Buildozer:
sudo apt install -y \
    python3-pip python3-setuptools python3-venv \
    build-essential git zip unzip \
    openjdk-17-jdk \
    autoconf automake libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev \
    libffi-dev libssl-dev
```

---

## 2  Desktop-Build (PyInstaller)

### 2.1  Schneller Build

```bash
# Windows
pyinstaller --onefile --windowed --name "NeuroTracker" main.py

# Linux / macOS
pyinstaller --onefile --windowed --name "NeuroTracker" main.py
```

### 2.2  Vollständiger Build mit Ressourcen

Der Pfadtrenner für `--add-data` ist `;` unter Windows und `:` unter Linux/macOS.

**Windows (CMD):**

```cmd
pyinstaller --onefile --windowed ^
    --name "NeuroTracker" ^
    --icon "resources/icons/app_icon.ico" ^
    --add-data "data;data" ^
    --add-data "credentials.json;." ^
    --hidden-import google.oauth2.credentials ^
    --hidden-import google_auth_oauthlib.flow ^
    --hidden-import google.auth.transport.requests ^
    --hidden-import googleapiclient.discovery ^
    --hidden-import googleapiclient.http ^
    main.py
```

**Linux / macOS:**

```bash
pyinstaller --onefile --windowed \
    --name "NeuroTracker" \
    --add-data "data:data" \
    --add-data "credentials.json:." \
    --hidden-import google.oauth2.credentials \
    --hidden-import google_auth_oauthlib.flow \
    --hidden-import google.auth.transport.requests \
    --hidden-import googleapiclient.discovery \
    --hidden-import googleapiclient.http \
    main.py
```

### 2.3  Build mit Spec-Datei

Erstelle `NeuroTracker.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

block_cipher = None
sep = ";" if sys.platform == "win32" else ":"

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("data", "data"),
        ("credentials.json", "."),
    ],
    hiddenimports=[
        "google.oauth2.credentials",
        "google_auth_oauthlib.flow",
        "google.auth.transport.requests",
        "googleapiclient.discovery",
        "googleapiclient.http",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="NeuroTracker",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon="resources/icons/app_icon.ico",  # Einkommentieren wenn vorhanden
)
```

```bash
pyinstaller NeuroTracker.spec
```

### 2.4  Ausgabe

- Windows: `dist/NeuroTracker.exe`
- Linux: `dist/NeuroTracker`
- macOS: `dist/NeuroTracker.app` (mit `--windowed`)

---

## 3  Android-Build (Buildozer)

### 3.1  Wie es funktioniert

Buildozer erwartet immer `main.py` als Entry Point. Da `main.py` im Projekt die Desktop-Version ist, tauscht der Build-Prozess die Datei temporär:

1. `main.py` (Desktop) wird gesichert
2. `main_android.py` wird zu `main.py` kopiert
3. Buildozer baut das APK
4. Originale `main.py` wird wiederhergestellt

Das `Makefile` automatisiert diese Schritte.

### 3.2  Debug-APK bauen

```bash
make android-debug
```

Oder manuell:

```bash
cp main.py main_desktop_backup.py
cp main_android.py main.py
buildozer android debug
mv main_desktop_backup.py main.py
```

### 3.3  Release-APK bauen

```bash
make android-release
```

### 3.4  Auf Gerät deployen

```bash
make android-deploy
```

### 3.5  Ausgabe

- Debug: `bin/NeuroTracker-1.0.0-arm64-v8a_armeabi-v7a-debug.apk`
- Release: `bin/NeuroTracker-1.0.0-arm64-v8a_armeabi-v7a-release.apk`

---

## 4  Makefile-Referenz

| Befehl | Beschreibung |
|--------|-------------|
| `make desktop` | Desktop-EXE/Binary bauen (PyInstaller) |
| `make desktop-debug` | Desktop-Build mit Konsole (für Debugging) |
| `make android-debug` | Android Debug-APK bauen |
| `make android-release` | Android Release-APK bauen |
| `make android-deploy` | APK auf angeschlossenes Gerät installieren & starten |
| `make android-logcat` | ADB Logcat für NeuroTracker anzeigen |
| `make clean` | Alle Build-Artefakte entfernen |
| `make clean-android` | Nur Android Build-Artefakte entfernen |

---

## 5  Wichtige Hinweise

### Google Drive Credentials

Die `credentials.json` muss entweder:
1. Im selben Verzeichnis wie die fertige App liegen, ODER
2. Im Build mit `--add-data` eingebunden werden

### Daten-Verzeichnis

Die App erstellt automatisch einen `data/` Ordner für:
- `entries.json` – Einträge
- `food_suggestions.json` – Lebensmittel
- `settings.json` – Einstellungen
- `token.json` – Google Auth Token
- `sync_status.json` – Sync-Status

### Android-Berechtigungen

Das APK fordert folgende Berechtigungen:
- `INTERNET` – Google Drive Sync
- `READ_EXTERNAL_STORAGE` / `WRITE_EXTERNAL_STORAGE` – Datenspeicherung

---

## 6  Fehlerbehebung

### Desktop: App startet nicht

```bash
# Build mit Konsole für Debug-Ausgabe
make desktop-debug
# oder:
pyinstaller --onefile --console --name "NeuroTracker_Debug" main.py
```

### Desktop: Google API nicht gefunden

Prüfe, dass alle hidden imports enthalten sind (siehe Abschnitt 2.2).

### Desktop: PyQt5-Fehler

```bash
pip install --upgrade pyinstaller pyqt5
```

### Android: Buildozer findet main.py nicht

Stelle sicher, dass du `make android-debug` verwendest – das Makefile tauscht die Entry Points korrekt.

### Android: KivyMD Fehler

Prüfe, dass `kivymd==1.2.0` in `buildozer.spec` (requirements) und `requirements_android.txt` übereinstimmen.

### Android: NDK/SDK Fehler

```bash
# Buildozer-Cache komplett neu aufbauen
make clean-android
make android-debug
```
