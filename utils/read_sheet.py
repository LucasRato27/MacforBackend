import pandas as pd

def read_google_sheet(sheet_url):
    """
    Reads a Google Sheet into a pandas DataFrame.

    Parameters:
    sheet_url (str): The URL of the Google Sheet.

    Returns:
    pd.DataFrame: The DataFrame containing the Google Sheet data.
    """
    # Extract the Google Sheet ID from the URL
    sheet_id = sheet_url.split('/')[5]

    # Google Sheets CSV export URL format
    csv_export_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv'

    # Read the CSV into a pandas DataFrame
    df = pd.read_csv(csv_export_url)

    return df
