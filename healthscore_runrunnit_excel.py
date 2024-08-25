import requests
import json
import pandas as pd
import datetime

#Function to convert seconds to hms
def seconds_to_hms(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours)}:{int(minutes)}:{int(seconds)}"

def fetch_runrunit_tasks(
    pages=10,
    limit=1000,
    is_closed=None,
    is_working_on=None,
    sort=None,
    sort_dir="desc",
    export_filename="tarefas_filtradas"
):
    url = "https://runrun.it/api/v1.0/tasks"
    headers = {
        "App-Key": "8cdb5426d5eb6a8408dec01affa5f023",
        "User-Token": "1hX3ZnUyCQu5mQtaeCDN"
    }
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    all_tasks = []

    try:
        for page in range(1, pages + 1):
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
                estimated_delivery_date = 'N/A'  # or any default value you prefer

            tarefa_filtrada = {
                'id Runrunit': tarefa['id'],
                'titulo': tarefa['title'],
                'estado': tarefa['state'],
                'Quadro': tarefa['board_name'],
                'campos personalizados': tarefa['custom_fields'],
                'tags': tarefa['tags_data'],
            }
            tarefas_filtradas.append(tarefa_filtrada)

        #Creating a .json file
        json_filename = f"{export_filename}.json"
        with open(json_filename, "w", encoding='utf-8') as file:
            json.dump(tarefas_filtradas, file, ensure_ascii=False, indent=4)

        # Save to an excel file from pandas
        excel_filename = f"outputs/{export_filename}.xlsx"

        df = pd.DataFrame(tarefas_filtradas)

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

        df = df.rename(columns={
            'custom_26': 'ocorridos',
            'custom_27': 'data',
            'custom_28': 'cliente',
        })

        df = df.explode('ocorridos')

        print("Saving a dataframe with dimensions: ", df.shape)
        df.to_excel(excel_filename, index=False)

    except Exception as e:
        print(f"An error occurred: {e}")
        if 'tarefas_filtradas' in locals():
            df = pd.DataFrame(tarefas_filtradas)
            return df
        else:
            return pd.DataFrame()  # return an empty DataFrame if no data was fetched

    return df

# Call the function with the desired parameters
df = fetch_runrunit_tasks(
    pages=10,
    limit=1000,
    sort_dir="desc",
    export_filename="feedback_full"
)

print(df.head())  # print the first few rows of the DataFrame to check the result
