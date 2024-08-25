import requests
import json
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st


# Função para converter segundos para hms
def seconds_to_hms(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours)}:{int(minutes)}:{int(seconds)}"


# Função para fazer a chamada de API e retornar df.
def fetch_runrunit_tasks(
        pages=10,
        limit=None,
        is_closed=None,
        is_working_on=None,
        sort=None,
        sort_dir="desc"
):
    url = "https://runrun.it/api/v1.0/tasks"
    headers = {
        "App-Key": "8cdb5426d5eb6a8408dec01affa5f023",
        "User-Token": "1hX3ZnUyCQu5mQtaeCDN"
    }

    all_tasks = []

    try:
        for page in range(1, pages + 1):
            print("opening page", page)
            parameters = {
                "limit": limit,
                "is_closed": is_closed,
                "sort": sort,
                "sort_dir": sort_dir,
                "page": page
            }
            if is_working_on is not None:
                parameters["is_working_on"] = is_working_on

            response = requests.get(url, headers=headers, params=parameters)

            if response.status_code == 200:
                tasks = response.json()
                all_tasks.extend(tasks)
            else:
                print(f"Failed to fetch page {page}: {response.status_code}, {response.text}")
                break

        tarefas_filtradas = []

        for tarefa in all_tasks:
            if tarefa['board_name'].lower() != "acompanhamento de clientes":
                continue

            estimated_delivery_date = tarefa.get('estimated_delivery_date')
            if estimated_delivery_date:
                estimated_delivery_date = estimated_delivery_date.split('T')[0]
            else:
                estimated_delivery_date = 'N/A'  # or any default value

            tarefa_filtrada = {
                'id Runrunit': tarefa['id'],
                'titulo': tarefa['title'],
                'estado': tarefa['state'],
                'Quadro': tarefa['board_name'],
                'campos personalizados': tarefa['custom_fields'],
            }
            tarefas_filtradas.append(tarefa_filtrada)

        df = pd.DataFrame(tarefas_filtradas)

        # Função para extrair apenas os labels dos campos personalizados
        # Função para extrair apenas os labels dos campos personalizados
        def extrair_labels(campos_personalizados):
            if isinstance(campos_personalizados, list):
                return [campo['label'] for campo in campos_personalizados]
            elif isinstance(campos_personalizados, dict):
                return campos_personalizados.get('label', None)
            else:
                return campos_personalizados

        # Aplicar a função a cada coluna de campos personalizados
        for col in df['campos personalizados'][0].keys():
            df[col] = df['campos personalizados'].apply(lambda x: extrair_labels(x[col]) if col in x else None)

        # Remover a coluna original de campos personalizados
        df = df.drop(columns=['campos personalizados'])

        # Renomear as colunas de campos customizáveis
        df = df.rename(columns={
            'custom_26': 'ocorridos',
            'custom_27': 'data',
            'custom_28': 'cliente',
        })

        df = df.explode('ocorridos')

        # Substituir NaNs para evitar problemas de formatação
        df = df.fillna('')

        print("Dataframe fetched with dimensions: ", df.shape)

    except Exception as e:
        print(f"An error occurred: {e}")
        if 'tarefas_filtradas' in locals():
            df = pd.DataFrame(tarefas_filtradas)
            return df
        else:
            return pd.DataFrame()  # return an empty DataFrame if no data was fetched

    return df

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
        "https://docs.google.com/spreadsheets/d/1pB8OKJzam3uyRL5y8d2q7ATWKwTliYIjhXFW39uaPAU/edit?gid=0#gid=0").sheet1

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

st.markdown(
    """
    <style>
    div.stButton > button {
        display: block;
        margin-left: auto;
        margin-right: auto;
        font-size: 80px;
        padding: 20px 40px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
    .centered-image {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.image("img/Logo.png", width=300, caption="", use_column_width=False, output_format="auto", clamp=False, channels="RGB")

st.title("Runrunit Task Fetcher")

df = pd.DataFrame()

# Chamar a função para buscar os dados
if st.button("Executar"):
    df = fetch_runrunit_tasks(
        pages=2,
        sort_dir="desc",
        sort="id"
    )
    # Fazer o upload dos dados para o Google Sheets
    upload_to_sheets(df, sheet_name="Macfor")


# Verificar o DataFrame antes de enviar para o Google Sheets
print("df head:\n", df.head(), "\n\n")  # Imprime as primeiras linhas do DataFrame para verificar o resultado
print("df shape:", df.shape)  # Imprime as dimensões do DataFrame para verificar o resultado