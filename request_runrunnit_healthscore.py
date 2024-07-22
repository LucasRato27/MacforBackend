import requests
import json
import pandas as pd
import datetime

def seconds_to_hms(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours)}:{int(minutes)}:{int(seconds)}"

def fetch_runrunit_tasks(
    pages=1,
    limit=1000,
    is_closed=False,
    is_working_on=None,
    sort="desired_date",
    sort_dir="desc",
    export_filename="tarefas_filtradas",
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
                tasks = response.json()
                all_tasks.extend(tasks)
                break

        tarefas_filtradas = []

        json_filename = f"tarefas_raw.json"
        with open(json_filename, "w", encoding='utf-8') as file:
            json.dump(tarefas_filtradas, file, ensure_ascii=False, indent=4)

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
                'tags': tarefa['tags_data'],
            }
            tarefas_filtradas.append(tarefa_filtrada)

        json_filename = f"{export_filename}.json"
        with open(json_filename, "w", encoding='utf-8') as file:
            json.dump(tarefas_filtradas, file, ensure_ascii=False, indent=4)

        # append parameters to the export filename
        datestring = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
        export_filename += f"{datestring}"

        # Save to an excel file from pandas
        excel_filename = f"outputs/{export_filename}{'_closed' if is_closed else ''}.xlsx"

        df = pd.DataFrame(tarefas_filtradas)

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
            'custom_28': 'cliente'
        })

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
    pages=5,
    limit=1000,
    is_closed=False,
    is_working_on=False,
    export_filename="feedback_"
)

print(df.head())  # print the first few rows of the DataFrame to check the result

df_closed = fetch_runrunit_tasks(
    pages=50,
    limit=1000,
    is_closed=True,
    is_working_on=False,
    export_filename="feedback_"
)

print(df_closed.head())  # print the first few rows of the DataFrame to check the result

# save df_full to xlsx file

df_full = pd.concat([df, df_closed])

df_full.to_excel("outputs/tarefas_full.xlsx", index=False)