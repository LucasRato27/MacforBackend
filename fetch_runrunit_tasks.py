import requests
import json
import pandas as pd
import streamlit as st
from utils.upload_to_sheets import upload_to_sheets
from media_problemas import calcular_media_problemas

"""
Url da planilha sendo editada: https://docs.google.com/spreadsheets/d/1OWdcEc5NozVGXvDkAlrlCgs-5HUc8KeH3BXF-QqHlf4/edit?gid=1456452784#gid=1456452784
"""

def fetch_runrunit_tasks(n_pags):
    def calcular_taxa_atraso_por_colaborador(df):
        # Verificar se as colunas 'atraso' e 'colaborador' existem
        if 'atraso' not in df.columns or 'colaborador' not in df.columns:
            raise KeyError("As colunas 'atraso' ou 'colaborador' não foram encontradas no dataframe.")

        # Converter 'data de inicio' para formato datetime e remover NaT
        df['data de inicio'] = pd.to_datetime(df['data de inicio'], errors='coerce')
        df = df.dropna(subset=['data de inicio'])

        # Criar uma nova coluna 'mes_ano' para agrupar por mês e ano
        df['mes_ano'] = df['data de inicio'].dt.to_period('M')

        # Filtrar tarefas de atraso (2. Atrasado e 3. Muito atrasado)
        df_atraso = df[df['atraso'].isin(['2. Atrasado', '3. Muito atrasado'])]

        # Contar o total de tarefas por colaborador e mês
        total_tarefas_mes_colaborador = df.groupby(['mes_ano', 'colaborador']).size().unstack(fill_value=0)

        # Contar o total de atrasos por colaborador e mês
        total_atraso_mes_colaborador = df_atraso.groupby(['mes_ano', 'colaborador']).size().unstack(fill_value=0)

        # Calcular a taxa de atraso como uma porcentagem e garantir que os valores sejam numéricos
        taxa_atraso_colaborador = (total_atraso_mes_colaborador / total_tarefas_mes_colaborador * 100).fillna(0)

        # Resetar o índice para adicionar 'mes_ano' como uma coluna em vez de índice
        taxa_atraso_colaborador = taxa_atraso_colaborador.reset_index()

        # Converter o 'mes_ano' para string no formato 'MM/AAAA'
        taxa_atraso_colaborador['mes_ano_str'] = taxa_atraso_colaborador['mes_ano'].dt.strftime('%m/%Y')

        # Assegurar que todas as colunas numéricas fiquem no formato float (sem aspas)
        for col in taxa_atraso_colaborador.columns:
            if col not in ['mes_ano', 'mes_ano_str']:
                taxa_atraso_colaborador[col] = taxa_atraso_colaborador[col].astype(float)

        # Exibir o DataFrame final para verificação
        print("DataFrame final de taxa de atraso por colaborador:\n", taxa_atraso_colaborador)

        return taxa_atraso_colaborador

    def calcular_taxa_refacao_por_colaborador(df):
        # Verificar se as colunas 'tipo de job' e 'colaborador' existem
        if 'tipo de job' not in df.columns or 'colaborador' not in df.columns:
            raise KeyError("As colunas 'tipo de job' ou 'colaborador' não foram encontradas no dataframe.")

        # Converter 'data de inicio' para formato datetime e remover NaT
        df['data de inicio'] = pd.to_datetime(df['data de inicio'], errors='coerce')
        df = df.dropna(subset=['data de inicio'])

        # Criar uma nova coluna 'mes_ano' para agrupar por mês e ano
        df['mes_ano'] = df['data de inicio'].dt.to_period('M')

        # Filtrar tarefas de Refação ou Retrabalho
        df_refacao = df[
            df['tipo de job'].str.contains('Refação|Retrabalho|Ajuste Complexo|Ajuste Simples', case=False, na=False)]

        # Contar o total de tarefas por colaborador e mês
        total_tarefas_mes_colaborador = df.groupby(['mes_ano', 'colaborador']).size().unstack(fill_value=0)

        # Contar o total de refações por colaborador e mês
        total_refacao_mes_colaborador = df_refacao.groupby(['mes_ano', 'colaborador']).size().unstack(fill_value=0)

        # Calcular a taxa de refação como uma porcentagem e garantir que os valores sejam numéricos
        taxa_refacao_colaborador = (total_refacao_mes_colaborador / total_tarefas_mes_colaborador * 100).fillna(0)

        # Resetar o índice para adicionar 'mes_ano' como uma coluna em vez de índice
        taxa_refacao_colaborador = taxa_refacao_colaborador.reset_index()

        # Converter o 'mes_ano' para string no formato 'MM/AAAA'
        taxa_refacao_colaborador['mes_ano_str'] = taxa_refacao_colaborador['mes_ano'].dt.strftime('%m/%Y')

        # Assegurar que todas as colunas, exceto 'mes_ano' e 'mes_ano_str', são numéricas
        for col in taxa_refacao_colaborador.columns:
            if col not in ['mes_ano', 'mes_ano_str']:
                taxa_refacao_colaborador[col] = pd.to_numeric(taxa_refacao_colaborador[col], errors='coerce').fillna(0)

        # Exibir o DataFrame final para verificação
        print("DataFrame final de taxa de refação por colaborador:\n", taxa_refacao_colaborador)

        return taxa_refacao_colaborador

    def calcular_taxa_refacao(df):
        # Verificar se as colunas 'tipo de job' e 'cliente' existem
        if 'tipo de job' not in df.columns or 'cliente' not in df.columns:
            raise KeyError("As colunas 'tipo de job' ou 'cliente' não foram encontradas no dataframe.")

        # Converter 'data de inicio' para formato datetime e remover NaT
        df['data de inicio'] = pd.to_datetime(df['data de inicio'], errors='coerce')
        df = df.dropna(subset=['data de inicio'])

        # Criar uma nova coluna 'mes_ano' para agrupar por mês e ano
        df['mes_ano'] = df['data de inicio'].dt.to_period('M')

        # Filtrar tarefas de Refação ou Retrabalho
        df_refacao = df[
            df['tipo de job'].str.contains('Refação|Retrabalho|Ajuste Complexo|Ajuste Simples', case=False, na=False)]

        # Contar o total de tarefas por cliente e mês
        total_tarefas_mes_cliente = df.groupby(['mes_ano', 'cliente']).size().unstack(fill_value=0)

        # Contar o total de refações por cliente e mês
        total_refacao_mes_cliente = df_refacao.groupby(['mes_ano', 'cliente']).size().unstack(fill_value=0)

        # Calcular a taxa de refação como uma porcentagem e garantir que os valores sejam numéricos
        taxa_refacao_cliente = (total_refacao_mes_cliente / total_tarefas_mes_cliente * 100).fillna(0)

        # Resetar o índice para adicionar 'mes_ano' como uma coluna em vez de índice
        taxa_refacao_cliente = taxa_refacao_cliente.reset_index()

        # Converter o 'mes_ano' para string no formato 'MM/AAAA' para evitar problemas de interpretação como data
        taxa_refacao_cliente['mes_ano_str'] = taxa_refacao_cliente['mes_ano'].dt.strftime('%m/%Y')

        # Formatar as colunas numéricas para utilizar vírgula como separador decimal
        for col in taxa_refacao_cliente.columns:
            if col not in ['mes_ano', 'mes_ano_str']:
                # Formatar números com vírgula para separar decimais
                taxa_refacao_cliente[col] = pd.to_numeric(taxa_refacao_cliente[col], errors='coerce').fillna(0)

        # Exportar ou exibir para garantir que os valores estão corretos
        print("DataFrame final de taxa de refação por cliente:\n", taxa_refacao_cliente)

        return taxa_refacao_cliente

    def calcular_taxa_atraso(df):
        # Verificar se as colunas 'atraso' e 'cliente' existem
        if 'atraso' not in df.columns or 'cliente' not in df.columns:
            raise KeyError("As colunas 'atraso' ou 'cliente' não foram encontradas no dataframe.")

        # Converter 'data de inicio' para formato datetime e remover NaT
        df['data de inicio'] = pd.to_datetime(df['data de inicio'], errors='coerce')
        df = df.dropna(subset=['data de inicio'])

        # Criar uma nova coluna 'mes_ano' para agrupar por mês e ano
        df['mes_ano'] = df['data de inicio'].dt.to_period('M')

        # Filtrar tarefas de atraso (2. Atrasado e 3. Muito atrasado)
        df_atraso = df[df['atraso'].isin(['2. Atrasado', '3. Muito atrasado'])]

        # Contar o total de tarefas por cliente e mês
        total_tarefas_mes_cliente = df.groupby(['mes_ano', 'cliente']).size().unstack(fill_value=0)

        # Contar o total de atrasos por cliente e mês
        total_atraso_mes_cliente = df_atraso.groupby(['mes_ano', 'cliente']).size().unstack(fill_value=0)

        # Calcular a taxa de atraso como uma porcentagem e garantir que os valores sejam numéricos
        taxa_atraso_cliente = (total_atraso_mes_cliente / total_tarefas_mes_cliente * 100).fillna(0)

        # Resetar o índice para adicionar 'mes_ano' como uma coluna em vez de índice
        taxa_atraso_cliente = taxa_atraso_cliente.reset_index()

        # Converter o 'mes_ano' para string no formato 'MM/AAAA' para evitar problemas de interpretação como data
        taxa_atraso_cliente['mes_ano_str'] = taxa_atraso_cliente['mes_ano'].dt.strftime('%m/%Y')

        # Formatar as colunas numéricas para utilizar vírgula como separador decimal
        for col in taxa_atraso_cliente.columns:
            if col not in ['mes_ano', 'mes_ano_str']:
                # Formatar números com vírgula para separar decimais
                taxa_atraso_cliente[col] = pd.to_numeric(taxa_atraso_cliente[col], errors='coerce').fillna(0)

        # Exibir o DataFrame final para verificação
        print("DataFrame final de taxa de atraso por cliente:\n", taxa_atraso_cliente)

        return taxa_atraso_cliente

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

                # Processar os assignments de cada tarefa
                assignments = tarefa.get("assignments", [])
                for assignment in assignments:
                    tarefa_filtrada = {
                        'data de inicio': assignment.get('start_date', 'N/A'),
                        'data de fechamento': assignment.get('close_date', 'N/A'),
                        'data ideal': tarefa['desired_date'],
                        'data ideal de inicio': tarefa['desired_start_date'],
                        'data estimada de entrega': tarefa['estimated_delivery_date'],
                        'data fim gantt': tarefa['gantt_bar_end_date'],
                        'id Runrunit': tarefa['id'],
                        'titulo': tarefa['title'],
                        'cliente': tarefa['client_name'],
                        'projeto': tarefa['project_name'],
                        'tipo de tarefa': tarefa['type_name'],
                        'colaborador': assignment.get('assignee_name', 'N/A'),
                        'estado': tarefa['state'],
                        'status': tarefa['task_status_name'],
                        'etapa': tarefa['board_stage_name'],
                        'board_stage_description': tarefa['board_stage_description'],
                        "board_stage_position": tarefa['board_stage_position'],
                        'atraso': tarefa['overdue'],
                        'Time': assignment.get('team_name', 'N/A'),
                        'board': tarefa['board_name'],
                        'foi reaberto': tarefa['was_reopened'],
                        'fechado?': assignment.get('is_closed', 'N/A'),
                        'numero de subtarefas': tarefa['subtasks_count'],
                        'tempo trabalhado': assignment.get('time_worked', 'N/A'),
                        'priority': assignment.get('priority', 'N/A'),
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
            df["custom_37"] = df["custom_37"].str.split(', ')
            df = df.explode('custom_37')
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

            # Ler a planilha de pontuações do Google Sheets
            pontuacoes = read_google_sheet(
                "https://docs.google.com/spreadsheets/d/1iDxF2ONzwaZAdIcuWE-adMyDIEVHGUx6F9nQsG0nYME/edit?gid=0#gid=0")

            # Mesclar com o DataFrame principal com base no tipo de job
            df = df.merge(pontuacoes, how='left', left_on='tipo de job', right_on='Tipo_de_Job')

            # Preencher valores NaN na coluna 'Multiplicador' com 0, remover espaços em branco, e substituir vírgulas por pontos
            df['Multiplicador'] = df['Multiplicador'].fillna(0).astype(str).str.strip().replace(',', '.', regex=True)

            # Converter 'Multiplicador' para numérico, convertendo erros para NaN, e preencher NaN com 0
            df['Multiplicador'] = pd.to_numeric(df['Multiplicador'], errors='coerce').fillna(0)

            # Renomear 'Multiplicador' para 'Pontuação'
            df = df.rename(columns={'Multiplicador': 'Pontuação'})

            # Converter a coluna 'Pontuação' para ter duas casas decimais e substituir pontos por vírgulas
            df['Pontuação'] = df['Pontuação'].apply(lambda x: f"{x:.2f}".replace('.', ','))

            # Remover a coluna 'Tipo_de_Job' após o merge
            df = df.drop(columns=['Tipo_de_Job'])

            # Substituir valores de atraso para os textos desejados
            df["atraso"] = df["atraso"].replace({
                "on_schedule": "1. No prazo",
                "soft_overdue": "2. Atrasado",
                "hard_overdue": "3. Muito atrasado"
            })

            # Coluna de data base
            data_base = "data ideal"

            # Converter a coluna data_base para datetime, ignorando erros
            df[data_base] = pd.to_datetime(df[data_base], errors='coerce')

            # Extrai o primeiro dia do mês e ano da data
            df['mes da tarefa'] = df[data_base].dt.to_period('M')
            df["mes do ano"] = df[data_base].dt.month
            df['ano da tarefa'] = df[data_base].dt.year

            df[data_base] = df[data_base].astype(str)
            df[data_base] = df[data_base].str.replace("NaT", "")

            # Converter a coluna 'data ideal de inicio' para datetime, preservando apenas a data
            df['data ideal de inicio'] = pd.to_datetime(df['data ideal de inicio'], errors='coerce').dt.strftime('%Y-%m-%d')

            df.to_excel('outputs/tarefas.xlsx', index=False)

            print("Dataframe fetched with dimensions: ", df.shape)

        except Exception as e:
            print(f"An error occurred: {e}")
            st.write(f"An error occurred: {e}")
            st.write(f"Se ocorreu um erro, rode novamente o script. Se ele for de conexão, tentar novamente tende a resolver. Se persistir, entre em contato com o desenvolvedor.")
            df = pd.DataFrame()  # return an empty DataFrame if no data was fetched

        return df


    # Chamar a função para buscar os dados
    df = fetch_runrunit_tasks(
        pages=n_pags,
        sort_dir="desc",
        sort="id"
    )

    # Aplicar a função no dataframe de tarefas
    df_taxa_refacao = calcular_taxa_refacao(df)
    df_taxa_refacao.to_excel('outputs/refacao.xlsx', index=False)

    df_taxa_atraso = calcular_taxa_atraso(df)
    df_taxa_atraso.to_excel('outputs/atraso.xlsx', index=False)

    df_taxa_refacao_colaborador = calcular_taxa_refacao_por_colaborador(df)
    df_taxa_refacao_colaborador.to_excel('outputs/refacao_col.xlsx',index=False)

    df_taxa_atraso_colaborador = calcular_taxa_atraso_por_colaborador(df)
    df_taxa_atraso_colaborador.to_excel('outputs/atraso_col.xlsx',index=False)

    media_problemas = calcular_media_problemas(df)

    # Fazer o upload dos dados para o Google Sheets
    upload_to_sheets(media_problemas, sheet_name="Macfor 3",sheet_url="https://docs.google.com/spreadsheets/d/1mctKJamrrVljxAoyxwMlpkcGCDEfWEFkii28vydsfXI/edit?gid=0#gid=0")
    upload_to_sheets(df, sheet_name="Macfor",sheet_url="https://docs.google.com/spreadsheets/d/1HSn9o3EeBk49dm0OdlBUKaTkdTVj2NsRQWnuDp5tD9o/edit?gid=0#gid=0")
    upload_to_sheets(df_taxa_refacao, sheet_name="Macfor 2",sheet_url="https://docs.google.com/spreadsheets/d/1o1ukAgKqjchHLttsLx9jukNbxx5XfIeoAwm69NoFIS0/edit?gid=0#gid=0")
    upload_to_sheets(df_taxa_atraso, sheet_name="Macfor - Taxa de Atraso",sheet_url="https://docs.google.com/spreadsheets/d/1UL6Ya0MJRK0AMFFDCo_kKd3DyKfvY6oDcGMKGT-ZQ8o/edit?gid=0#gid=0")
    upload_to_sheets(df_taxa_refacao_colaborador, sheet_name="Macfor 3",sheet_url="https://docs.google.com/spreadsheets/d/1V2vN67Y2Av-xmuCAbTe6B0rKQYgf8TibPTVzer5VwVU/edit?gid=0#gid=0")
    upload_to_sheets(df_taxa_atraso_colaborador, sheet_name="Macfor 4",sheet_url="https://docs.google.com/spreadsheets/d/1L6T3MYyE74v7ElVhp9AjIt5ZTI1zJv4oYaPM4Up2L1s/edit?gid=0#gid=0")