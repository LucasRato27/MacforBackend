import requests
import pandas as pd

# Função para fazer a chamada de API e retornar df.
def fetch_runrunit_feedback(
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

        df.to_excel('outputs/feedback_full.xlsx', index=False)

    except Exception as e:
        print(f"An error occurred: {e}")
        if 'tarefas_filtradas' in locals():
            df = pd.DataFrame(tarefas_filtradas)
            return df
        else:
            return pd.DataFrame()  # return an empty DataFrame if no data was fetched







