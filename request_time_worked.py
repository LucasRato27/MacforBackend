import requests
import json
from datetime import datetime, timedelta

def fetch_runrunit_time_worked(
    start_date, 
    end_date,
    pages=2,
    group_by=["date", "user_id", "client_id"],  # Usando lista para o group_by
    period_type="custom_range",
    include_capacity=True,
    include_untracked=True,
    include_others=True,
    expand_others=True
):
    url = "https://runrun.it/api/v1.0/reports/time_worked"
    headers = {
        "App-Key": "8cdb5426d5eb6a8408dec01affa5f023",
        "User-Token": "1hX3ZnUyCQu5mQtaeCDN",
    }
    
    # Convertendo o group_by para string separada por vírgulas, se for uma lista
    if isinstance(group_by, list):
        group_by = ",".join(group_by)
    
    parameters = {
        "group_by": group_by,
        "period_type": period_type,
        "period_start": start_date,
        "period_end": end_date,
        "include_capacity": include_capacity,
        "include_untracked": include_untracked,
        "include_others": include_others,
        "expand_others": expand_others,
    }

    print(f"Request parameters: {parameters}")

    all_time_worked = []

    try:
        for page in range(1, pages + 1):
            message = f"Opening page {page}"
            print(message)

            response = requests.get(url, headers=headers, params=parameters)

            # Adicionando mensagens de depuração
            print(f"Status Code: {response.status_code}")
            # print(f"Response Text: {response.text}")

            if response.status_code == 200:
                try:
                    time_worked = response.json()
                    
                    # Verificando se a resposta é um dicionário com as chaves esperadas
                    if isinstance(time_worked, dict) and "result" in time_worked:
                        all_time_worked.extend(time_worked['result'])
                    else:
                        print(f"Unexpected response format on page {page}: {time_worked}")
                        break
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    break
            else:
                print(f"Failed to fetch page {page}: {response.status_code}, {response.text}")
                break

        with open('time_worked_raw.json', 'w') as json_file:
            json.dump(all_time_worked, json_file, indent=4)

        time_worked_filtrados = []

        for entry in all_time_worked:
            # Ensure the entry is a dictionary before accessing keys
            if isinstance(entry, dict):
                user_filtrado = {
                    'client_id': entry.get('project_id', None),
                    'client_name': entry.get('project_name', None),
                    'user_id': entry.get('user_id', None),
                    'user_name': entry.get('user_name', None),
                    'automatic_time': entry.get('automatic_time', 0),
                    'manual_time': entry.get('manual_time', 0),
                    'total_time': entry.get('time', 0),
                    'date': entry.get('date', None)
                }
                time_worked_filtrados.append(user_filtrado)
            else:
                print(f"Unexpected data format: {entry}")

        with open('time_worked_filtered.json', 'w') as json_file:
            json.dump(time_worked_filtrados, json_file, indent=4)

        return time_worked_filtrados

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Define o intervalo de datas
start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
end_date = datetime.now().strftime('%Y-%m-%d')

# Chama a função com as novas datas
fetch_runrunit_time_worked(start_date, end_date)
