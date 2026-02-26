# NeuroTracker – Build Automation
# Usage: make <target>
#
# Desktop targets use PyInstaller.
# Android targets use Buildozer (swaps main_android.py → main.py automatically).

.PHONY: desktop desktop-debug android-debug android-release android-deploy android-logcat clean clean-android help

# ──────────────────────────────────────────────────────────────────────────────
# Desktop (PyInstaller)
# ──────────────────────────────────────────────────────────────────────────────

PYINSTALLER_COMMON = --name "NeuroTracker" \
	--paths src \
	--hidden-import google.oauth2.credentials \
	--hidden-import google_auth_oauthlib.flow \
	--hidden-import google.auth.transport.requests \
	--hidden-import googleapiclient.discovery \
	--hidden-import googleapiclient.http \
	--add-data "data$(SEP)data"

# Path separator: ; on Windows, : on Linux/macOS
ifeq ($(OS),Windows_NT)
    SEP = ;
else
    SEP = :
endif

desktop:
	pyinstaller --onefile --windowed $(PYINSTALLER_COMMON) main.py
	@echo ""
	@echo "Build fertig: dist/NeuroTracker"

desktop-debug:
	pyinstaller --onefile --console $(PYINSTALLER_COMMON) --name "NeuroTracker_Debug" main.py
	@echo ""
	@echo "Debug-Build fertig: dist/NeuroTracker_Debug"

# ──────────────────────────────────────────────────────────────────────────────
# Android (Buildozer)
# ──────────────────────────────────────────────────────────────────────────────
# Buildozer always expects main.py as the entry point.
# We temporarily swap main_android.py → main.py for the build.

define SWAP_ENTRYPOINT
	@echo "Swapping entry point: main_android.py → main.py"
	@cp main.py main_desktop_backup.py
	@cp main_android.py main.py
endef

define RESTORE_ENTRYPOINT
	@echo "Restoring desktop entry point"
	@mv main_desktop_backup.py main.py
endef

android-debug:
	$(SWAP_ENTRYPOINT)
	buildozer android debug || { $(RESTORE_ENTRYPOINT); exit 1; }
	$(RESTORE_ENTRYPOINT)
	@echo ""
	@echo "APK: bin/$$(ls -t bin/*.apk 2>/dev/null | head -1)"

android-release:
	$(SWAP_ENTRYPOINT)
	buildozer android release || { $(RESTORE_ENTRYPOINT); exit 1; }
	$(RESTORE_ENTRYPOINT)
	@echo ""
	@echo "Release-APK: bin/$$(ls -t bin/*.apk 2>/dev/null | head -1)"

android-deploy:
	$(SWAP_ENTRYPOINT)
	buildozer android debug deploy run || { $(RESTORE_ENTRYPOINT); exit 1; }
	$(RESTORE_ENTRYPOINT)

android-logcat:
	buildozer android logcat | grep -i "python\|kivy\|neurotracker"

# ──────────────────────────────────────────────────────────────────────────────
# Cleanup
# ──────────────────────────────────────────────────────────────────────────────

clean: clean-android
	rm -rf build/ dist/ *.spec __pycache__/
	@echo "Desktop build artifacts removed."

clean-android:
	rm -rf .buildozer/ bin/
	@echo "Android build artifacts removed."

# ──────────────────────────────────────────────────────────────────────────────
# Help
# ──────────────────────────────────────────────────────────────────────────────

help:
	@echo "NeuroTracker Build Targets"
	@echo "========================="
	@echo ""
	@echo "Desktop:"
	@echo "  make desktop        – Build Desktop-App (PyInstaller, GUI)"
	@echo "  make desktop-debug  – Build Desktop-App mit Konsole"
	@echo ""
	@echo "Android:"
	@echo "  make android-debug  – Debug-APK bauen"
	@echo "  make android-release – Release-APK bauen"
	@echo "  make android-deploy – APK auf Gerät installieren & starten"
	@echo "  make android-logcat – Logcat-Ausgabe für NeuroTracker"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          – Alle Build-Artefakte entfernen"
	@echo "  make clean-android  – Nur Android-Artefakte entfernen"
