[app]
# NeuroTracker Android – Buildozer Configuration

title = NeuroTracker
package.name = neurotracker
package.domain = org.xaver

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 1.0.0

# Python-for-android requirements
# IMPORTANT: kivymd==1.2.0 matches the API used in mobile_ui/ and main_android.py
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,certifi,materialyoucolor,exceptiongroup

# Android configuration
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 34
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24
android.accept_sdk_license = True
android.enable_androidx = True

# Architecture
android.archs = arm64-v8a, armeabi-v7a

# Orientation
orientation = portrait

# Fullscreen mode (0 = no)
fullscreen = 0

# Icon (optional – set if icon file exists)
# icon.filename = resources/icons/app_icon.png

# Presplash (optional)
# presplash.filename = resources/presplash.png

# Include shared modules in APK
source.include_patterns = main.py, src/models/*.py, src/utils/*.py, src/mobile_ui/*.py, src/config.py, data/.gitkeep

# Exclude desktop-only files from APK
# NOTE: main_android.py is copied to main.py by the Makefile before building.
#       The desktop main.py is temporarily backed up and restored after the build.
source.exclude_patterns = src/ui/*, main_android.py, build.md, Makefile, profile.md, umstellung.md, README.md, requirements*.txt, buildozer.spec, venv/*, dist/*, build/*, __pycache__/*, .git/*, .buildozer/*

# python-for-android distribution
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
