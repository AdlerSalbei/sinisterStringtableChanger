import gspread
from google.oauth2.service_account import Credentials
import re
from config import SERVICE_ACCOUNT_FILE

def extract_spreadsheet_id(url):
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    return match.group(1) if match else None

def read_google_sheet(sheet_url):
    spreadsheet_id = extract_spreadsheet_id(sheet_url)
    if not spreadsheet_id:
        return {}
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(spreadsheet_id).sheet1
    data = sheet.get_all_values()
    mapping = {}
    for row in data[1:]:
        if len(row) >= 5 and row[0].strip():
            mapping[row[0].strip()] = row[4].strip()
    return mapping
