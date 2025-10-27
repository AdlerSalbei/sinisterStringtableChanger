from __future__ import annotations
import gspread
from google.oauth2.service_account import Credentials
from typing import Dict, List, Optional

# === KONFIGURATION ===
SERVICE_ACCOUNT_FILE: str = "credentials.json"  # Service-Account-Datei
SHEET_NAME: str = "MeinSheet"                   # Name des Google Sheets
RANGE: str = "A:E"                              # Bereich mit Spalten A–E

# === AUTHENTIFIZIERUNG ===
scopes: List[str] = ["https://docs.google.com/spreadsheets/d/1E3F__tz9GuqV8kCtQHpGKmqkjf5Ust7JObf1LwFLhqs/edit?usp=sharing"]
creds: Credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=scopes
)
client: gspread.Client = gspread.authorize(creds)

# === SHEET LADEN ===
sheet: gspread.models.Worksheet = client.open(SHEET_NAME).sheet1  # Erstes Tabellenblatt
data: List[List[str]] = sheet.get(RANGE)  # Alle Zeilen (A bis E) als Liste von Listen

# === SCHNELLE DICTIONARY-STRUKTUR ===
# name_in_spalte_A → wert_in_spalte_E
lookup: Dict[str, str] = {
    row[0].strip().lower(): row[4]
    for row in data
    if len(row) >= 5 and row[0].strip()  # Nur Zeilen mit Werten in A & E
}

# === SUCHFUNKTION ===
def finde_wert(name: str) -> Optional[str]:
    """
    Gibt den Wert aus Spalte E für den Namen in Spalte A zurück.
    Suche ist case-insensitive.
    """
    return lookup.get(name.strip().lower())