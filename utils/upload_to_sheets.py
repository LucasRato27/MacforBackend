import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path


def upload_to_sheets(df, sheet_name, sheet_url):
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    # Configurando as credenciais e autenticando com o Google Sheets
    creds = ServiceAccountCredentials.from_json_keyfile_name(Path('credentials.json'), scopes)
    client = gspread.authorize(creds)

    # Abrindo a planilha e a aba desejada
    sheet = client.open_by_url(sheet_url).sheet1

    try:
        # Limpar a planilha antes de inserir novos dados
        sheet.clear()

        # Enviar o DataFrame inteiro para o Google Sheets
        set_with_dataframe(sheet, df)

        print(f"Data uploaded successfully to Google Sheets: {sheet_name}")
        return True

    except Exception as e:
        print(f"An error occurred while uploading to Google Sheets: {e}")
        return False