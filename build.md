# Neuro-Tracker Build-Anleitung

## Voraussetzungen

```bash
pip install pyinstaller
```

## One-File Build

### Einfacher Build

```bash
pyinstaller --onefile --windowed --name "NeuroTracker" main.py
```

### Vollständiger Build (mit Icon und Ressourcen)

```bash
pyinstaller --onefile --windowed ^
    --name "NeuroTracker" ^
    --icon "resources/icons/app_icon.ico" ^
    --add-data "resources;resources" ^
    --add-data "data;data" ^
    --add-data "credentials.json;." ^
    main.py
```

### Build mit Spec-Datei

Erstelle `NeuroTracker.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),
        ('data', 'data'),
        ('credentials.json', '.'),
    ],
    hiddenimports=[
        'google.oauth2.credentials',
        'google_auth_oauthlib.flow',
        'google.auth.transport.requests',
        'googleapiclient.discovery',
        'googleapiclient.http',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NeuroTracker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # False = keine Konsole (GUI-App)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/app_icon.ico',  # Optional: App-Icon
)
```

Build mit Spec-Datei:

```bash
pyinstaller NeuroTracker.spec
```

## Ausgabe

Nach dem Build findest du die .exe in:
- `dist/NeuroTracker.exe`

## Wichtige Hinweise

### Google Drive Credentials

Die `credentials.json` muss entweder:
1. Im selben Verzeichnis wie die .exe liegen, ODER
2. Im Build mit `--add-data` eingebunden werden

### Daten-Verzeichnis

Die App erstellt automatisch einen `data/` Ordner im Verzeichnis der .exe für:
- `entries.json` - Einträge
- `food_suggestions.json` - Lebensmittel
- `token.json` - Google Auth Token
- `sync_status.json` - Sync-Status

### Fehlerbehebung

**Problem: App startet nicht**
```bash
# Build mit Konsole für Debug-Ausgabe
pyinstaller --onefile --console --name "NeuroTracker_Debug" main.py
```

**Problem: Google API nicht gefunden**
Füge hidden imports hinzu:
```bash
pyinstaller --onefile --windowed ^
    --hidden-import google.oauth2.credentials ^
    --hidden-import google_auth_oauthlib.flow ^
    --hidden-import googleapiclient.discovery ^
    main.py
```

**Problem: PyQt5 Fehler**
```bash
pip install pyinstaller --upgrade
pip install pyqt5 --upgrade
```

## Kompletter Build-Befehl (Empfohlen)

```bash
pyinstaller --onefile --windowed ^
    --name "NeuroTracker" ^
    --hidden-import google.oauth2.credentials ^
    --hidden-import google_auth_oauthlib.flow ^
    --hidden-import google.auth.transport.requests ^
    --hidden-import googleapiclient.discovery ^
    --hidden-import googleapiclient.http ^
    --add-data "credentials.json;." ^
    main.py
```

## Nach dem Build

1. Kopiere `dist/NeuroTracker.exe` in den gewünschten Ordner
2. Kopiere `credentials.json` in denselben Ordner (falls nicht im Build)
3. Starte die App - sie erstellt automatisch den `data/` Ordner