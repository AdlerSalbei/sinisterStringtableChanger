import gspread
from google.oauth2.service_account import Credentials
import os
import shutil

# ---- KONFIGURATION ----
SERVICE_ACCOUNT_FILE = "service_account.json"  # Google Service Account JSON
SPREADSHEET_NAME = "MeinSheet"                 # Google Sheet Name
STRINGTABLE_FOLDER = "stringtables"            # Ordner mit Sprachdateien (.ini)
BACKUP_FOLDER = "backups"                      # Ort, wo Backups abgelegt werden

# ---- FUNKTIONEN ----
def find_star_citizen_install_path():
    """
    Versucht automatisch den Star Citizen Installationspfad zu finden.
    Prüft zuerst die PATH-Umgebungsvariable, dann Standardpfade, danach Benutzerabfrage.
    """
    # 1. Suche in PATH-Variable
    paths = os.environ.get("PATH", "").split(os.pathsep)
    for path in paths:
        normalized_path = os.path.normpath(path).lower()
        if "starcitizen\\live" in normalized_path:
            return os.path.normpath(path)

    # 2. Fallback auf Standardpfade
    possible_paths = [
        r"C:\Program Files\Roberts Space Industries\StarCitizen\LIVE",
        r"C:\Program Files (x86)\Roberts Space Industries\StarCitizen\LIVE",
        os.path.expandvars(r"%ProgramFiles%\Roberts Space Industries\StarCitizen\LIVE"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Roberts Space Industries\StarCitizen\LIVE"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path

    # 3. Benutzerabfrage
    print("Star Citizen LIVE-Verzeichnis konnte nicht automatisch gefunden werden.")
    print("Bitte Pfad manuell eingeben (z. B. C:\\Program Files\\Roberts Space Industries\\StarCitizen\\LIVE):")
    manual_path = input("Pfad: ").strip('" ')
    return manual_path

def read_google_sheet(sheet_name):
    """Liest Name (Spalte A) und Wert (Spalte E) aus dem Sheet."""
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    data = sheet.get_all_values()

    mapping = {}
    for row in data[1:]:  # Erste Zeile = Header
        if len(row) >= 5 and row[0].strip():
            name = row[0].strip()
            value = row[4].strip()
            mapping[name] = value
    return mapping

def get_suffix(value):
    """Gibt den passenden Suffix-Text zurück."""
    try:
        num = int(value)
    except ValueError:
        return ""
    if num == 50:
        return " EHD"
    elif num == 25:
        return " HD"
    elif num == 1:
        return " ND"
    elif num == 0:
        return " ZD"
    return ""

def backup_existing_file(file_path):
    """Erstellt ein Backup der bestehenden global.ini."""
    if not os.path.exists(file_path):
        return None

    os.makedirs(BACKUP_FOLDER, exist_ok=True)
    backup_name = f"global_backup_{os.path.basename(file_path)}_{len(os.listdir(BACKUP_FOLDER)) + 1}.ini"
    backup_path = os.path.join(BACKUP_FOLDER, backup_name)
    shutil.copy2(file_path, backup_path)
    return backup_path

def process_ini_file(mapping, input_path, output_path):
    """Bearbeitet eine INI-Datei und speichert sie als global.ini."""
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    modified_lines = []
    for line in lines:
        if "=" in line:
            key, value = line.strip().split("=", 1)
            key = key.strip()
            value = value.strip()
            if key in mapping:
                suffix = get_suffix(mapping[key])
                if suffix and not value.endswith((" EHD", " HD", " ND", " ZD")):
                    value = value + suffix
                line = f"{key}={value}\n"
        modified_lines.append(line)
