import gspread
from google.oauth2.service_account import Credentials
import os
import shutil
import re
import winreg

# ---- KONFIGURATION ----
SERVICE_ACCOUNT_FILE = "service_account.json"  # Google Service Account JSON
SPREADSHEET_NAME = "MeinSheet"                 # Google Sheet Name
STRINGTABLE_FOLDER = "stringtables"            # Ordner mit Sprachdateien (.ini)
BACKUP_FOLDER = "backups"                      # Ort, wo Backups abgelegt werden

# ---- FUNKTIONEN ----
def find_star_citizen_install_path():
    """
    Versucht automatisch den Star Citizen Installationspfad zu finden.
    Prüft Standardorte und Registry-Einträge.
    """
    possible_paths = [
        r"C:\Program Files\Roberts Space Industries\StarCitizen\LIVE",
        r"C:\Program Files (x86)\Roberts Space Industries\StarCitizen\LIVE",
        os.path.expandvars(r"%ProgramFiles%\Roberts Space Industries\StarCitizen\LIVE"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Roberts Space Industries\StarCitizen\LIVE"),
    ]

    # Versuche über Registry
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Roberts Space Industries") as key:
            install_path, _ = winreg.QueryValueEx(key, "InstallLocation")
            live_path = os.path.join(install_path, "StarCitizen", "LIVE")
            if os.path.exists(live_path):
                return live_path
    except FileNotFoundError:
        pass

    # Fallback auf Standardpfade
    for path in possible_paths:
        if os.path.exists(path):
            return path

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

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(modified_lines)

def main():
    print("Lade Google Sheet ...")
    data = read_google_sheet(SPREADSHEET_NAME)
    print(f"→ {len(data)} Einträge geladen.")

    # Sprache wählen
    language = input("Sprache wählen (de/en/fr): ").strip().lower()
    available_langs = ["de", "en", "fr"]
    if language not in available_langs:
        print("Ungültige Sprache, Standard 'de' wird verwendet.")
        language = "de"

    input_file = os.path.join(STRINGTABLE_FOLDER, f"{language}.ini")

    if not os.path.exists(input_file):
        print(f"Datei nicht gefunden: {input_file}")
        return

    # Star Citizen Pfad ermitteln
    star_citizen_path = find_star_citizen_install_path()
    if not os.path.exists(star_citizen_path):
        print(f" Ungültiger Pfad: {star_citizen_path}")
        return

    output_file = os.path.join(star_citizen_path, "global.ini")

    # Backup erstellen, falls vorhanden
    backup = backup_existing_file(output_file)
    if backup:
        print(f"Backup erstellt unter: {backup}")

    print(f"Bearbeite Sprachdatei ({language}.ini) ...")
    process_ini_file(data, input_file, output_file)

    print(f"global.ini erfolgreich erstellt im LIVE-Verzeichnis:")
    print(f"   {output_file}")

if __name__ == "__main__":
    main()
