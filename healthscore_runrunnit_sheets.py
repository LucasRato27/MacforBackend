import requests
import pandas as pd
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import gspread

API_URL = "https://runrun.it/api/v1.0/tasks"
HEADERS = {
    "App-Key": "8cdb5426d5eb6a8408dec01affa5f023",
    "User-Token": "1hX3ZnUyCQu5mQtaeCDN"
}


def seconds_to_hms(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours)}:{int(minutes)}:{int(seconds)}"


def fetch_tasks(
        pages=10,
        limit=None,
        is_closed=None,
        is_working_on=None,
        sort=None,
        sort_dir="desc"
):
    all_tasks = []
    try:
        for page in range(1, pages + 1):
            params = {
                "limit": limit,
                "is_closed": is_closed,
                "sort": sort,
                "sort_dir": sort_dir,
                "page": page
            }
            if is_working_on is not None:
                params["is_working_on"] = is_working_on
            response = requests.get(API_URL, headers=HEADERS, params=params)
            if response.status_code == 200:
                all_tasks.extend(response.json())
            else:
                print(f"Failed to fetch page {page}: {response.status_code}, {response.text}")
                break
        return filter_tasks(all_tasks)
    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame(all_tasks) if all_tasks else pd.DataFrame()


def filter_tasks(tasks):
    filtered_tasks = [task for task in tasks if task['board_name'].lower() == "acompanhamento de clientes"]
    tasks_data = []
    for task in filtered_tasks:
        estimated_delivery_date = task.get('estimated_delivery_date', 'N/A').split('T')[0]
        tasks_data.append({
            'id Runrunit': task['id'],
            'titulo': task['title'],
            'estado': task['state'],
            'Quadro': task['board_name'],
            'campos personalizados': task['custom_fields']
        })
    df = pd.DataFrame(tasks_data)
    return process_custom_fields(df)


def process_custom_fields(df):
    def extrair_labels(campos_personalizados):
        if isinstance(campos_personalizados, list):
            return [campo['label'] for campo in campos_personalizados]
        return campos_personalizados.get('label') if isinstance(campos_personalizados, dict) else campos_personalizados

    for col in df['campos personalizados'][0].keys():
        df[col] = df['campos personalizados'].apply(lambda x: extrair_labels(x[col]) if col in x else None)
    df.drop(columns=['campos personalizados'], inplace=True)
    df.rename(columns={'custom_26': 'ocorridos', 'custom_27': 'data', 'custom_28': 'cliente'}, inplace=True)
    return df.explode('ocorridos').fillna('')


def upload_to_sheets(df, sheet_name):
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    # Configurando as credenciais e autenticando com o Google Sheets
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scopes)
    client = gspread.authorize(creds)

    # Abrindo a planilha e a aba desejada
    sheet = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1OWdcEc5NozVGXvDkAlrlCgs-5HUc8KeH3BXF-QqHlf4/edit?gid=1456452784#gid=1456452784").sheet1

    try:
        # Limpar a planilha antes de inserir novos dados
        sheet.clear()

        # Enviar o DataFrame inteiro para o Google Sheets
        set_with_dataframe(sheet, df)

        print(f"Data uploaded successfully to Google Sheets: {sheet_name}")
        st.write(f"Data uploaded successfully to Google Sheets: {sheet_name}")
        return True

    except Exception as e:
        st.write(f"An error occurred while uploading to Google Sheets: {e}")
        print(f"An error occurred while uploading to Google Sheets: {e}")
        return False

def set_streamlit_styles():
    st.markdown(
        """
        <style>
        div.stButton > button { display: block; margin-left: auto; margin-right: auto; font-size: 80px; padding: 20px 40px; }
        .centered-image { display: block; margin-left: auto; margin-right: auto; }
        </style>
        """,
        unsafe_allow_html=True
    )


set_streamlit_styles()
st.image("img/Logo.png", width=300)
st.title("Runrunit Healthscore Feedback Fetcher")
df = pd.DataFrame()
if st.button("Executar"):
    df = fetch_tasks(pages=2, sort_dir="desc", sort="id")
    upload_to_sheets(df, sheet_name="Macfor")
print("df head:\n", df.head(), "\n\n")
print("df shape:", df.shape)
