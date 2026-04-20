import sys
from scraper import search_leads
from sheets_exporter import export_to_sheets


def main():
    print("====================================")
    print("   Search Engine Lead Scraper       ")
    print("====================================")

    query = input(
        "\nEnter your search query (e.g., 'ladies garments companies URLs'):\n> ")
    if not query.strip():
        print("[!] No query entered. Exiting.")
        return

    try:
        max_results = int(
            input("\nHow many results do you want to extract? (e.g., 50):\n> "))
    except ValueError:
        print("[!] Invalid number. Defaulting to 50.")
        max_results = 50

    sheet_name = input(
        "\nEnter the EXACT name of your Google Sheet (e.g., 'My Leads'):\n> ")
    if not sheet_name.strip():
        print("[!] No sheet name entered. Exiting.")
        return

    # Phase 1: Scrape
    print("\n[Phase 1] Scraping Search Engine...")
    leads = search_leads(query, max_results)

    # Phase 2: Export
    print("\n[Phase 2] Exporting to Google Sheets...")
    if leads:
        export_to_sheets(leads, sheet_name)
    else:
        print("[!] Skipping export because no leads were found.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Script interrupted by user. Exiting.")
        sys.exit(0)
