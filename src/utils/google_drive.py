"""
Google Drive Sync Implementation for Neuro-Tracker
Real implementation using Google Drive API v3 with OAuth 2.0
"""
# pyright: reportMissingImports=false, reportOptionalMemberAccess=false
# pyright: reportPossiblyUnboundVariable=false, reportArgumentType=false

import json
import io
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

# Google API imports - these will be available when running locally
GOOGLE_API_AVAILABLE = False
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.auth.exceptions import RefreshError
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError:
    pass

import config
from config import (
    GOOGLE_DRIVE_ENABLED, GOOGLE_CREDENTIALS_FILE, GOOGLE_TOKEN_FILE,
    GOOGLE_DRIVE_FOLDER, GOOGLE_DRIVE_FOLDER_ID, DATA_DIR, ENTRIES_FILE,
    FOOD_SUGGESTIONS_FILE
)
from models.data_manager import DataManager


class SyncError(Exception):
    """Custom exception for sync errors"""
    def __init__(self, message: str, recoverable: bool = True):
        self.message = message
        self.recoverable = recoverable
        super().__init__(message)


class GoogleDriveAuthenticator:
    """
    Handles Google Drive OAuth2 authentication.
    Uses the installed application flow for desktop apps.
    """

    SCOPES = ['https://www.googleapis.com/auth/drive']

    def __init__(self):
        self.credentials_file = GOOGLE_CREDENTIALS_FILE
        self.token_file = GOOGLE_TOKEN_FILE
        self.credentials: Optional[Any] = None
        self.service = None

    def authenticate(self) -> Tuple[bool, str]:
        """
        Complete OAuth 2.0 flow for desktop application.

        Flow:
        1. Check for existing valid token
        2. If expired, try refresh
        3. If no token/refresh fails, start new OAuth flow

        Returns:
            Tuple of (success, message)
        """
        if not GOOGLE_API_AVAILABLE:
            return False, (
                "Google API Bibliotheken nicht installiert.\n\n"
                "Bitte installiere sie mit:\n"
                "pip install google-api-python-client google-auth-oauthlib"
            )

        try:
            # Step 1: Try to load existing credentials
            if self.token_file.exists():
                self.credentials = Credentials.from_authorized_user_file(
                    str(self.token_file), self.SCOPES
                )

            # Step 2: Validate and refresh if needed
            if self.credentials and self.credentials.valid:
                pass  # Credentials are good
            elif self.credentials and self.credentials.expired and self.credentials.refresh_token:
                # Token expired but we have refresh token
                try:
                    self.credentials.refresh(Request())
                    self._save_token()
                except Exception:
                    # Refresh failed, need full re-auth
                    self.credentials = None

            # Step 3: Full OAuth flow if no valid credentials
            if not self.credentials or not self.credentials.valid:
                if not self.credentials_file.exists():
                    return False, (
                        "credentials.json nicht gefunden.\n\n"
                        "Bitte erstelle ein Google Cloud Projekt und lade "
                        "die OAuth 2.0 Client-ID als 'credentials.json' herunter.\n\n"
                        f"Erwartet in: {self.credentials_file}"
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_file),
                    self.SCOPES
                )
                # Use local server for callback (opens browser)
                self.credentials = flow.run_local_server(
                    port=0,  # Auto-select available port
                    prompt='consent',  # Always show consent screen
                    success_message='Authentifizierung erfolgreich! Du kannst dieses Fenster schliessen.',
                    open_browser=True
                )
                self._save_token()

            # Build the Drive service
            self.service = build('drive', 'v3', credentials=self.credentials)

            return True, "Erfolgreich mit Google Drive verbunden!"

        except Exception as e:
            return False, f"Authentifizierungsfehler: {str(e)}"

    def _save_token(self):
        """Save credentials to token file for reuse"""
        if self.credentials:
            self.token_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_file, 'w') as f:
                f.write(self.credentials.to_json())

    def revoke(self) -> Tuple[bool, str]:
        """
        Revoke Google Drive access and delete stored token.

        Returns:
            Tuple of (success, message)
        """
        self.credentials = None
        self.service = None

        # Delete token file if exists
        if self.token_file.exists():
            self.token_file.unlink()

        return True, "Zugriff widerrufen. Token gelöscht."

    def is_authenticated(self) -> bool:
        """Check if authenticated with valid credentials"""
        return self.credentials is not None and self.credentials.valid


class GoogleDriveSync:
    """
    Google Drive synchronization for Neuro-Tracker.
    Handles uploading, downloading, and merging of data files.
    """

    FOLDER_ID = GOOGLE_DRIVE_FOLDER_ID
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.authenticator = GoogleDriveAuthenticator()
        self.service = None
        self._connected = False
        self._last_sync: Optional[datetime] = None
        self._sync_status_file = DATA_DIR / "sync_status.json"
        self._load_status()

    def _load_status(self):
        """Load sync status from file"""
        try:
            if self._sync_status_file.exists():
                with open(self._sync_status_file, 'r') as f:
                    status = json.load(f)
                    self._connected = status.get('connected', False)
                    last_sync_str = status.get('last_sync')
                    if last_sync_str:
                        self._last_sync = datetime.fromisoformat(last_sync_str)
        except Exception:
            pass

    def _save_status(self):
        """Save sync status to file"""
        try:
            status = {
                'connected': self._connected,
                'last_sync': self._last_sync.isoformat() if self._last_sync else None
            }
            with open(self._sync_status_file, 'w') as f:
                json.dump(status, f)
        except Exception:
            pass

    def connect(self) -> Tuple[bool, str]:
        """
        Connect to Google Drive using OAuth 2.0.

        Returns:
            Tuple of (success, message)
        """
        if not GOOGLE_API_AVAILABLE:
            return False, (
                "Google API Bibliotheken nicht installiert.\n\n"
                "Bitte installiere sie mit:\n"
                "pip install google-api-python-client google-auth-oauthlib"
            )

        # Authenticate
        success, message = self.authenticator.authenticate()

        if success:
            self.service = self.authenticator.service
            self._connected = True
            self._save_status()

            # Verify folder access
            try:
                self.service.files().get(fileId=self.FOLDER_ID).execute()
                return True, "Erfolgreich mit Google Drive verbunden!"
            except HttpError as e:
                if e.resp.status == 404:
                    return False, (
                        "Der konfigurierte Drive-Ordner wurde nicht gefunden.\n"
                        f"Folder ID: {self.FOLDER_ID}\n\n"
                        "Bitte überprüfe die GOOGLE_DRIVE_FOLDER_ID in config.py"
                    )
                raise
        else:
            self._connected = False
            self._save_status()
            return False, message

    def disconnect(self) -> Tuple[bool, str]:
        """
        Disconnect from Google Drive.

        Returns:
            Tuple of (success, message)
        """
        self._connected = False
        self._last_sync = None
        self.service = None
        self._save_status()

        # Also revoke authentication
        self.authenticator.revoke()

        return True, "Verbindung zu Google Drive getrennt."

    def _find_file_in_folder(self, filename: str) -> Optional[str]:
        """
        Find a file by name in the target folder.

        Args:
            filename: Name of the file to find

        Returns:
            File ID if found, None otherwise
        """
        if not self.service:
            return None

        try:
            query = f"name = '{filename}' and '{self.FOLDER_ID}' in parents and trashed = false"

            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, modifiedTime)',
                pageSize=1
            ).execute()

            files = results.get('files', [])
            return files[0]['id'] if files else None

        except Exception:
            return None

    def _download_file(self, file_id: str) -> Optional[bytes]:
        """
        Download file content from Google Drive.

        Args:
            file_id: The Google Drive file ID

        Returns:
            File content as bytes, or None on error
        """
        if not self.service:
            return None

        try:
            request = self.service.files().get_media(fileId=file_id)

            buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(buffer, request)

            done = False
            while not done:
                _, done = downloader.next_chunk()

            return buffer.getvalue()

        except Exception as e:
            print(f"Download error: {e}")
            return None

    def _download_json(self, file_id: str) -> Optional[Dict]:
        """
        Download and parse JSON file from Drive.

        Args:
            file_id: The Google Drive file ID

        Returns:
            Parsed JSON as dict, or None on error
        """
        content = self._download_file(file_id)
        if content:
            try:
                return json.loads(content.decode('utf-8'))
            except json.JSONDecodeError:
                return None
        return None

    def _upload_json(self, data: Any, filename: str, file_id: Optional[str] = None) -> Optional[str]:
        """
        Upload JSON data to Drive (create or update).

        Args:
            data: Data to serialize as JSON
            filename: Name for the file
            file_id: Existing file ID for update, None for create

        Returns:
            File ID on success, None on error
        """
        if not self.service:
            return None

        temp_path = None
        try:
            # Create temporary file with JSON content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                temp_path = Path(f.name)

            # Use resumable=False to avoid file locking issues on Windows
            media = MediaFileUpload(
                str(temp_path),
                mimetype='application/json',
                resumable=False
            )

            if file_id:
                # Update existing file
                result = self.service.files().update(
                    fileId=file_id,
                    media_body=media
                ).execute()
            else:
                # Create new file
                file_metadata = {
                    'name': filename,
                    'parents': [self.FOLDER_ID]
                }
                result = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()

            return result.get('id')

        except Exception as e:
            print(f"Upload error: {e}")
            return None

        finally:
            # Clean up temp file
            if temp_path and temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass  # Ignore cleanup errors on Windows

    def _merge_entries(self, local_entries: Dict[str, Dict],
                       remote_entries: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Merge local and remote entries with intelligent conflict resolution.

        Strategy:
        - Entries only in local: Keep
        - Entries only in remote: Keep
        - Entries in both: Newer updated_at wins
        - On tie: Merge foods lists (union)

        Args:
            local_entries: Local entries dict {date: entry_dict}
            remote_entries: Remote entries dict {date: entry_dict}

        Returns:
            Merged entries dict
        """
        merged = {}

        # Get all unique dates
        all_dates = set(local_entries.keys()) | set(remote_entries.keys())

        for date in all_dates:
            local_entry = local_entries.get(date)
            remote_entry = remote_entries.get(date)

            if local_entry and not remote_entry:
                # Only local exists
                merged[date] = local_entry

            elif remote_entry and not local_entry:
                # Only remote exists
                merged[date] = remote_entry

            else:
                # Both exist - conflict resolution
                merged[date] = self._resolve_entry_conflict(local_entry, remote_entry)

        return merged

    def _resolve_entry_conflict(self, local: Dict, remote: Dict) -> Dict:
        """
        Resolve conflict between local and remote entry for same date.

        Strategy:
        1. Compare updated_at timestamps
        2. Newer wins entirely
        3. On exact tie: Keep newer's fields but merge foods lists

        Args:
            local: Local entry dict
            remote: Remote entry dict

        Returns:
            Resolved entry dict
        """
        local_time = datetime.fromisoformat(local.get('updated_at', '1970-01-01T00:00:00'))
        remote_time = datetime.fromisoformat(remote.get('updated_at', '1970-01-01T00:00:00'))

        if local_time > remote_time:
            # Local is newer
            return local
        elif remote_time > local_time:
            # Remote is newer
            return remote
        else:
            # Exact tie - merge foods, keep rest from remote (preference)
            merged_entry = remote.copy()

            # Merge foods lists (union)
            local_foods = set(local.get('foods', []))
            remote_foods = set(remote.get('foods', []))
            merged_foods = sorted(local_foods | remote_foods)

            merged_entry['foods'] = merged_foods

            # Use notes from remote if exists, otherwise from local
            if not merged_entry.get('notes') and local.get('notes'):
                merged_entry['notes'] = local['notes']

            # Update the timestamp to now (we modified it)
            merged_entry['updated_at'] = datetime.now().isoformat()

            return merged_entry

    def _merge_food_suggestions(self, local_foods: List[str],
                                 remote_foods: List[str]) -> List[str]:
        """
        Merge food suggestion lists.

        Strategy: Union of both lists (keep all unique foods)

        Args:
            local_foods: Local food suggestions list
            remote_foods: Remote food suggestions list

        Returns:
            Sorted merged list of unique foods
        """
        merged = set(local_foods) | set(remote_foods)
        return sorted(merged)

    def sync(self) -> Tuple[bool, str]:
        """
        Full synchronization with Google Drive.

        Flow:
        1. Download remote files
        2. Load local files
        3. Merge with conflict resolution
        4. Save merged data locally
        5. Upload merged data to Drive

        Returns:
            Tuple of (success, message)
        """
        if not GOOGLE_DRIVE_ENABLED:
            return False, "Google Drive Sync ist deaktiviert."

        if not self._connected or not self.service:
            # Try to reconnect
            success, msg = self.connect()
            if not success:
                return False, f"Nicht verbunden: {msg}"

        try:
            results = []

            # === SYNC ENTRIES.JSON ===
            entries_result = self._sync_entries()
            results.append(entries_result)

            # === SYNC FOOD_SUGGESTIONS.JSON ===
            foods_result = self._sync_food_suggestions()
            results.append(foods_result)

            # Update sync timestamp
            self._last_sync = datetime.now()
            self._save_status()

            return True, f"Sync erfolgreich um {self._last_sync.strftime('%H:%M:%S')}\n" + "\n".join(results)

        except SyncError as e:
            if not e.recoverable:
                self._connected = False
                self._save_status()
            return False, e.message

        except Exception as e:
            return False, f"Sync-Fehler: {str(e)}"

    def _sync_entries(self) -> str:
        """
        Sync entries.json with merge.

        Returns:
            Status message
        """
        # Find remote file
        remote_file_id = self._find_file_in_folder('entries.json')

        # Load local entries
        local_data = {}
        if ENTRIES_FILE.exists():
            try:
                with open(ENTRIES_FILE, 'r', encoding='utf-8') as f:
                    local_data = json.load(f)
            except json.JSONDecodeError:
                local_data = {}

        if remote_file_id:
            # Download and merge
            remote_data = self._download_json(remote_file_id) or {}
            merged_data = self._merge_entries(local_data, remote_data)

            # Save merged locally
            ENTRIES_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(ENTRIES_FILE, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=2)

            # Upload merged to Drive
            self._upload_json(merged_data, 'entries.json', remote_file_id)

            # Reload DataManager
            self.data_manager.load()

            local_count = len(local_data)
            remote_count = len(remote_data)
            merged_count = len(merged_data)

            return f"Einträge: {merged_count} (lokal: {local_count}, remote: {remote_count})"
        else:
            # No remote file - upload local
            if local_data:
                self._upload_json(local_data, 'entries.json')
            return f"Einträge: {len(local_data)} hochgeladen"

    def _sync_food_suggestions(self) -> str:
        """
        Sync food_suggestions.json with merge.

        Returns:
            Status message
        """
        remote_file_id = self._find_file_in_folder('food_suggestions.json')

        # Load local
        local_foods = []
        if FOOD_SUGGESTIONS_FILE.exists():
            try:
                with open(FOOD_SUGGESTIONS_FILE, 'r', encoding='utf-8') as f:
                    local_foods = json.load(f)
            except json.JSONDecodeError:
                local_foods = []

        if remote_file_id:
            remote_foods = self._download_json(remote_file_id) or []
            merged_foods = self._merge_food_suggestions(local_foods, remote_foods)

            # Save merged locally
            FOOD_SUGGESTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(FOOD_SUGGESTIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(merged_foods, f, ensure_ascii=False, indent=2)

            # Upload merged
            self._upload_json(merged_foods, 'food_suggestions.json', remote_file_id)

            return f"Lebensmittel: {len(merged_foods)} synchronisiert"
        else:
            if local_foods:
                self._upload_json(local_foods, 'food_suggestions.json')
            return f"Lebensmittel: {len(local_foods)} hochgeladen"

    def upload(self) -> Tuple[bool, str]:
        """
        Force upload local data to Google Drive (overwrites remote).

        Returns:
            Tuple of (success, message)
        """
        if not self._connected or not self.service:
            return False, "Nicht mit Google Drive verbunden."

        try:
            results = []

            # Upload entries
            if ENTRIES_FILE.exists():
                with open(ENTRIES_FILE, 'r', encoding='utf-8') as f:
                    entries_data = json.load(f)

                file_id = self._find_file_in_folder('entries.json')
                self._upload_json(entries_data, 'entries.json', file_id)
                results.append(f"Einträge: {len(entries_data)} hochgeladen")

            # Upload food suggestions
            if FOOD_SUGGESTIONS_FILE.exists():
                with open(FOOD_SUGGESTIONS_FILE, 'r', encoding='utf-8') as f:
                    foods_data = json.load(f)

                file_id = self._find_file_in_folder('food_suggestions.json')
                self._upload_json(foods_data, 'food_suggestions.json', file_id)
                results.append(f"Lebensmittel: {len(foods_data)} hochgeladen")

            self._last_sync = datetime.now()
            self._save_status()

            return True, "Upload erfolgreich!\n" + "\n".join(results)

        except Exception as e:
            return False, f"Upload-Fehler: {str(e)}"

    def download(self) -> Tuple[bool, str]:
        """
        Force download data from Google Drive (overwrites local).

        Returns:
            Tuple of (success, message)
        """
        if not self._connected or not self.service:
            return False, "Nicht mit Google Drive verbunden."

        try:
            results = []

            # Download entries
            file_id = self._find_file_in_folder('entries.json')
            if file_id:
                entries_data = self._download_json(file_id)
                if entries_data:
                    ENTRIES_FILE.parent.mkdir(parents=True, exist_ok=True)
                    with open(ENTRIES_FILE, 'w', encoding='utf-8') as f:
                        json.dump(entries_data, f, ensure_ascii=False, indent=2)
                    self.data_manager.load()
                    results.append(f"Einträge: {len(entries_data)} heruntergeladen")

            # Download food suggestions
            file_id = self._find_file_in_folder('food_suggestions.json')
            if file_id:
                foods_data = self._download_json(file_id)
                if foods_data:
                    with open(FOOD_SUGGESTIONS_FILE, 'w', encoding='utf-8') as f:
                        json.dump(foods_data, f, ensure_ascii=False, indent=2)
                    results.append(f"Lebensmittel: {len(foods_data)} heruntergeladen")

            if not results:
                return False, "Keine Dateien zum Herunterladen gefunden."

            self._last_sync = datetime.now()
            self._save_status()

            return True, "Download erfolgreich!\n" + "\n".join(results)

        except Exception as e:
            return False, f"Download-Fehler: {str(e)}"

    def get_status(self) -> Dict:
        """
        Get the current sync status.

        Returns:
            Dict with status information
        """
        return {
            'enabled': GOOGLE_DRIVE_ENABLED,
            'connected': self._connected,
            'last_sync': self._last_sync.strftime('%d.%m.%Y %H:%M:%S') if self._last_sync else None,
            'folder': GOOGLE_DRIVE_FOLDER,
            'folder_id': self.FOLDER_ID,
            'api_available': GOOGLE_API_AVAILABLE,
            'credentials_exist': GOOGLE_CREDENTIALS_FILE.exists(),
            'token_exists': GOOGLE_TOKEN_FILE.exists()
        }

    def is_connected(self) -> bool:
        """Check if connected to Google Drive"""
        return self._connected

    def get_last_sync(self) -> Optional[datetime]:
        """Get the last sync time"""
        return self._last_sync