"""
Url da planilha sendo editada: https://docs.google.com/spreadsheets/d/1OWdcEc5NozVGXvDkAlrlCgs-5HUc8KeH3BXF-QqHlf4/edit?gid=1456452784#gid=1456452784
"""

import requests
import json
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st


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

            message = f"opening page {page}"
            print(message)
            st.write(message)

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
            if tarefa['board_name'].lower() != "macfor - outros clientes ":
                continue

            def format_date(date):
                if date:
                    return date.split('T')[0]
                else:
                    return ''

            date_fields = ['start_date', 'close_date', 'desired_date', 'gantt_bar_end_date', "estimated_delivery_date"]

            for field in date_fields:
                tarefa[field] = format_date(tarefa.get(field))

            tarefa_filtrada = {
                'data de inicio': tarefa['start_date'],
                'data de fechamento': tarefa['close_date'],
                'data ideal': tarefa['desired_date'],
                'data ideal de inicio': tarefa['desired_start_date'],
                'data estimada de entrega': tarefa['estimated_delivery_date'],
                'data fim gantt': tarefa['gantt_bar_end_date'],
                'id Runrunit': tarefa['id'],
                'titulo': tarefa['title'],
                'cliente': tarefa['client_name'],
                'projeto': tarefa['project_name'],
                'tipo de tarefa': tarefa['type_name'],
                'colaborador': tarefa['responsible_name'],
                'estado': tarefa['state'],
                'status': tarefa['task_status_name'],
                'etapa': tarefa['board_stage_name'],
                'board_stage_description': tarefa['board_stage_description'],
                "board_stage_position": tarefa['board_stage_position'],
                'atraso': tarefa['overdue'],
                'Time': tarefa['team_name'],
                'board': tarefa['board_name'],
                'foi reaberto': tarefa['was_reopened'],
                'fechado?': tarefa['is_closed'],
                'numero de subtarefas': tarefa['subtasks_count'],
                'tempo trabalhado': tarefa['time_worked'],
                'priority': tarefa['priority'],
                'sendo trabalhado': tarefa['is_working_on'],
                'é urgente?': tarefa['is_urgent'],
                'é subtarefa?': tarefa['is_subtask'],
                'campos personalizados': tarefa['custom_fields'], # deve ser tratado depois
                'tags': tarefa['tags_data'],
                'ids dos filhos': tarefa['child_ids'],
                'id dos prerequisitos': tarefa['parent_ids'],
                'id do pai': tarefa['parent_task_id'],
                'nome do pai': tarefa['parent_task_title'],
                'ids das subtarefas': tarefa['subtask_ids'],
                'tempo trabalhado em subtasks': tarefa['all_subtasks_time_worked'],
                'numero de anexos': tarefa['attachments_count'], # nao sera usado
            }
            tarefas_filtradas.append(tarefa_filtrada)

        df = pd.DataFrame(tarefas_filtradas)

        # df.to_excel("outputs/tarefas.xlsx", index=False)

        # drop campos personalizados nan
        df = df.dropna(subset=["campos personalizados"])

        # Função para extrair apenas os labels dos campos personalizados
        def extrair_labels(campos_personalizados):
            if isinstance(campos_personalizados, list):
                # Extraindo os labels e unindo em uma string separada por vírgulas
                return ', '.join(campo['label'] for campo in campos_personalizados if 'label' in campo)
            elif isinstance(campos_personalizados, dict):
                # Retornando o valor do label como uma string simples
                return campos_personalizados.get('label', None)
            else:
                return None


        # change simple quotes to double quotes
        # convert campos personalizados to string
        df["campos personalizados"] = df["campos personalizados"].apply(json.dumps)
        df['campos personalizados'] = df['campos personalizados'].str.replace("'", '"')
        df['campos personalizados'] = df['campos personalizados'].apply(json.loads)


        df["custom_37"] = df["campos personalizados"].apply(lambda x: extrair_labels(x["custom_37"]) if "custom_37" in x else None)
        df["custom_38"] = df["campos personalizados"].apply(lambda x: extrair_labels(x["custom_38"]) if "custom_38" in x else None)
        df["custom_39"] = df["campos personalizados"].apply(lambda x: extrair_labels(x["custom_39"]) if "custom_39" in x else None)
        df["custom_40"] = df["campos personalizados"].apply(lambda x: extrair_labels(x["custom_40"]) if "custom_40" in x else None)
        df["custom_46"] = df["campos personalizados"].apply(lambda x: extrair_labels(x["custom_46"]) if "custom_46" in x else None)

        # Renomear as colunas de campos customizáveis
        df = df.rename(columns={
            'custom_37': 'tipo de solicitacao',
            'custom_38': 'tipo de job',
            'custom_39': 'aderencia ao briefing',
            'custom_40': 'numero de anexo esperados',
            'custom_46': 'motivacao da solicitacao',
        })

        df = df.drop(columns=['campos personalizados'])

        # Substituir NaNs para evitar problemas de formatação
        df = df.fillna('')

        # change campos personalizados to string
        def turn_to_string(x):
            return json.dumps(x, ensure_ascii=False)
        df["tags"] = df["tags"].apply(turn_to_string)
        df["ids dos filhos"] = df["ids dos filhos"].apply(turn_to_string)
        df["id dos prerequisitos"] = df["id dos prerequisitos"].apply(turn_to_string)
        df["ids das subtarefas"] = df["ids das subtarefas"].apply(turn_to_string)

        # Convert timedelta to float representing total hours
        df['tempo_trabalhado_horas'] = df['tempo trabalhado']/3600.0

        df['tempo trabalhado em subtasks'] = df['tempo trabalhado em subtasks'].replace('', 0)

        df['tempo_subtasks_horas'] = df['tempo trabalhado em subtasks']/3600.0

        df['tempo_total_tasks'] = df['tempo_subtasks_horas'] + df['tempo_trabalhado_horas']

        pontuacoes = read_google_sheet("https://docs.google.com/spreadsheets/d/1iDxF2ONzwaZAdIcuWE-adMyDIEVHGUx6F9nQsG0nYME/edit?gid=0#gid=0")

        df = df.merge(pontuacoes, how='left', left_on='tipo de job', right_on='Tipo_de_Job')

        # Step 1: Fill NaN values in the 'Multiplicador' column with 0
        df['Multiplicador'] = df['Multiplicador'].fillna(0)

        # Step 2: Ensure there are no leading or trailing spaces, then replace commas with dots
        df['Multiplicador'] = df['Multiplicador'].str.strip().replace(',', '.', regex=True)

        # Step 3: Convert 'Multiplicador' to numeric, coercing errors to NaN
        df['Multiplicador'] = pd.to_numeric(df['Multiplicador'], errors='coerce')

        # Step 4: Fill any remaining NaN values with 0 (optional, depending on your needs)
        df['Multiplicador'] = df['Multiplicador'].fillna(0)

        df = df.drop(columns=['Tipo_de_Job'])

        df["atraso"] = df["atraso"].replace({
            "on_schedule": "1. No prazo",
            "soft_overdue": "2. Atrasado",
            "hard_overdue": "3. Muito atrasado"
        })

        # rename multiplicador to pontuacao
        df = df.rename(columns={
            'Multiplicador': 'Pontuação'
        })


        # coluna a se basear para datas
        data_base = "data ideal"
        # Converte a coluna data_base para datetime, ignorando erros
        df[data_base] = pd.to_datetime(df[data_base], errors='coerce')

        # Extrai o primeiro dia do mês e ano da data
        df['mes da tarefa'] = df[data_base].dt.to_period('M')
        df["mes do ano"] = df[data_base].dt.month
        df['ano da tarefa'] = df[data_base].dt.year

        df[data_base] = df[data_base].astype(str)
        df[data_base] = df[data_base].str.replace("NaT", "")

        df.to_excel('outputs/tarefas.xlsx', index=False)

        print("Dataframe fetched with dimensions: ", df.shape)

    except Exception as e:
        print(f"An error occurred: {e}")
        st.write(f"An error occurred: {e}")
        st.write(f"Se ocorreu um erro, rode novamente o script. Se ele for de conexão, tentar novamente tende a resolver. Se persistir, entre em contato com o desenvolvedor.")
        df = pd.DataFrame()  # return an empty DataFrame if no data was fetched

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
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1OWdcEc5NozVGXvDkAlrlCgs-5HUc8KeH3BXF-QqHlf4/edit?gid=1456452784#gid=1456452784").sheet1

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

n_pags = st.number_input("Número de páginas", min_value=1, max_value=100, value=20, step=1, format="%d")

# Chamar a função para buscar os dados
if st.button("Executar"):
    df = fetch_runrunit_tasks(
        pages=n_pags,
        sort_dir="desc",
        sort="id"
    )
    # Fazer o upload dos dados para o Google Sheets
    upload_to_sheets(df, sheet_name="Macfor")

# Verificar o DataFrame antes de enviar para o Google Sheets
print("df head:\n", df.head(), "\n\n")  # Imprime as primeiras linhas do DataFrame para verificar o resultado
print("df shape:", df.shape)  # Imprime as dimensões do DataFrame para verificar o resultado