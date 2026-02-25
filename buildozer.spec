[app]
# NeuroTracker Android – Buildozer Configuration

title = NeuroTracker
package.name = neurotracker
package.domain = org.xaver

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 1.0.0
requirements = python3,kivy==2.3.0,kivymd==2.0.1.dev0,pillow,certifi

# Entry point
entrypoint = main_android.py

# Android configuration
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True

# Architecture
android.archs = arm64-v8a, armeabi-v7a

# Orientation
orientation = portrait

# Fullscreen mode
fullscreen = 0

# Icon (optional – set if icon exists)
# icon.filename = resources/icons/app_icon.png

# Presplash (optional)
# presplash.filename = resources/presplash.png

# Android specific
android.enable_androidx = True

# Include data directories
source.include_patterns = models/*.py, utils/*.py, mobile_ui/*.py, config.py, data/.gitkeep

# Exclude desktop-only files from APK
source.exclude_patterns = ui/*, main.py, build.md, profile.md, umstellung.md, README.md, requirements.txt, venv/*, dist/*, build/*, __pycache__/*

[buildozer]
log_level = 2
warn_on_root = 1
