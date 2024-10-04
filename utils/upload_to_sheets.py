import streamlit as st
import json
import gspread
from google.oauth2 import service_account
from gspread_dataframe import set_with_dataframe


def upload_to_sheets(df, sheet_name, sheet_url):
    # Definir os escopos necessários
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    # Carregar as credenciais dos segredos do Streamlit
    creds_info = st.secrets["google_credentials"]

    # Criar as credenciais a partir do dicionário e incluir os escopos
    creds = service_account.Credentials.from_service_account_info(creds_info, scopes=scopes)

    # Autenticar com as credenciais e acessar o Google Sheets
    client = gspread.authorize(creds)

    # Abrir a planilha e a aba desejada
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