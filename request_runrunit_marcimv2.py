import requests
import json
import pandas as pd
from google.oauth2.service_account import Credentials
from gspread_formatting import CellFormat, Color, format_cell_range, TextFormat
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
            estimated_delivery_date = tarefa.get('estimated_delivery_date')
            if estimated_delivery_date:
                estimated_delivery_date = estimated_delivery_date.split('T')[0]
            else:
                estimated_delivery_date = 'N/A'  # or any default value you prefer

            tarefa_filtrada = {
                'data de inicio': tarefa['start_date'],
                'data de fechamento': tarefa['close_date'],
                'data ideal': tarefa['desired_date'],
                'data estimada de entrega': estimated_delivery_date,
                'data fim gantt': tarefa['gantt_bar_end_date'],
                'id Runrunit': tarefa['id'],
                'titulo': tarefa['title'],
                'cliente': tarefa['client_name'],
                'projeto': tarefa['project_name'],
                'Asset': tarefa['type_name'],
                'colaborador': tarefa['responsible_name'],
                'estado': tarefa['state'],
                'status': tarefa['task_status_name'],
                'atraso': tarefa['overdue'],
                'Time': tarefa['team_name'],
                'board': tarefa['board_name'],
                'foi reaberto': tarefa['was_reopened'],
                'numero de subtarefas': tarefa['subtasks_count'],
                'tempo trabalhado': seconds_to_hms(tarefa['time_worked']),
                'priority': tarefa['priority'],
                'sendo trabalhado': tarefa['is_working_on'],
                'é urgente?': tarefa['is_urgent'], 
                'é subtarefa?': tarefa['is_subtask'],
                'campos personalizados': tarefa['custom_fields'],
                'tags': tarefa['tags_data'],
                'ids dos filhos': tarefa['child_ids'],
                'id dos prerequisitos': tarefa['parent_ids'],
                'id do pai': tarefa['parent_task_id'],
                'nome do pai': tarefa['parent_task_title'],
                'ids das subtarefas': tarefa['subtask_ids'],
                'tempo trabalhado em subtasks': tarefa['all_subtasks_time_worked'],
                'numero de anexos': tarefa['attachments_count'],
            }
            tarefas_filtradas.append(tarefa_filtrada)

        json_filename = f"{export_filename}.json"
        with open(json_filename, "w", encoding='utf-8') as file:
            json.dump(tarefas_filtradas, file, ensure_ascii=False, indent=4)

        # append parameters to the export filename
        date_string = datetime.datetime.now().strftime("%Y/%m/%d_%H:%M")
        export_filename += f"{date_string}_p{pages}_l{limit}_closed{is_closed}_workingon{is_working_on}_sort{sort}_{sort_dir}"

        # Save to an excel file from pandas
        excel_filename = f"outputs/{export_filename}.xlsx"

        df = pd.DataFrame(tarefas_filtradas)
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
    is_closed=False,
    is_working_on=False,
    sort="estimated_delivery_date",
    sort_dir="desc",
    export_filename="tarefas_"
)

print(df.head())  # print the first few rows of the DataFrame to check the result
