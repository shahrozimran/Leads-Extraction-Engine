import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from typing import List, Dict

# Defines the scope of the application
SCOPES = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]


def export_to_sheets(data: List[Dict[str, str]], sheet_name: str, credentials_path: str = 'credentials.json'):
    """
    Exports a list of leads (dictionaries with title, url, description) to a Google Sheet.
    """
    if not os.path.exists(credentials_path):
        print(
            f"\n[!] Critical Error: Credentials file '{credentials_path}' not found.")
        print(
            "[!] Please follow the setup instructions to create a Google Service Account.")
        return False

    if not data:
        print("\n[!] No data provided to export.")
        return False

    try:
        print(
            f"\n[*] Authenticating with Google Sheets using {credentials_path}...")
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_path, SCOPES)
        client = gspread.authorize(creds)

        print(f"[*] Opening Google Sheet: '{sheet_name}'...")
        # Open the sheet by its exact name
        sheet = client.open(sheet_name).sheet1

        # Check if headers exist, if not, create them
        first_row = sheet.row_values(1) if sheet.row_count > 0 else []
        expected_headers = ["Title", "URL", "Email", "Description"]

        if not first_row or "url" not in [str(h).lower() for h in first_row]:
            print("[*] Adding headers to the sheet...")
            sheet.insert_row(expected_headers, 1)
        elif len(first_row) < 4 or first_row[2].lower() != "email":
            print("[*] Updating headers to accommodate Email column...")
            try:
                sheet.update(range_name="A1:D1", values=[expected_headers])
            except Exception:
                sheet.update("A1:D1", [expected_headers])

        # Prepare rows
        rows_to_insert = []
        for row in data:
            rows_to_insert.append([
                row.get("title", ""),
                row.get("url", ""),
                row.get("email", ""),
                row.get("description", "")
            ])

        # Append rows to the end of the sheet
        print(f"[*] Appending {len(rows_to_insert)} rows to the sheet...")
        sheet.append_rows(rows_to_insert)

        print(f"[*] Successfully exported data to '{sheet_name}'.")
        return True

    except gspread.exceptions.SpreadsheetNotFound:
        print(f"\n[!] Error: Spreadsheet '{sheet_name}' not found.")
        print("[!] MAKE SURE you have shared the Google Sheet with the email address found in your credentials.json file!")
        return False
    except Exception as e:
        print(f"\n[!] Error exporting to Google Sheets: {e}")
        return False
