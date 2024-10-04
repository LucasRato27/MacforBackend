from utils.upload_to_sheets import upload_to_sheets
from utils.read_sheet import read_google_sheet
from pathlib import Path
import numpy as np
import pandas as pd

def calculate_heathscore():
    # Construir o caminho de forma agnóstica ao sistema operacional
    file_path = Path("outputs") / "feedback_full.xlsx"

    # Ler o arquivo Excel
    df = pd.read_excel(file_path)

    criterios = read_google_sheet(
        "https://docs.google.com/spreadsheets/d/1YyiI5GZWP8orU-3YMEln6hKYKUJVrriTgiTyB6849qE/edit?gid=124241289#gid=124241289")
    # drop all cols after Pontuacoes
    criterios = criterios.loc[:, :'Pontuacoes']

    # calculate the change in healthscore for each row comparing with Ranking_de_Eventos and ocorridos
    df = df.merge(criterios, how='left', left_on='ocorridos', right_on='Ranking_de_Eventos')

    df.rename(columns={'Pontuacoes': 'Delta'}, inplace=True)

    # convert Delta to float
    df['Delta'] = df['Delta'].str.replace(',', '.').astype(float)
    # change data to datetime
    df['data'] = pd.to_datetime(df['data'], errors='coerce')

    df.dropna(subset=['Ranking_de_Eventos', 'Delta'], inplace=True)

    # sort by data
    df.sort_values(by='data', inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Inicializa o healthscore para cada cliente
    df['Healthscore'] = 10

    # Dicionário para manter o healthscore por cliente
    healthscore_dict = {}

    # Specify the healthscore column type.
    df['Healthscore'] = df['Healthscore'].astype(float)

    # Calcula o healthscore acumulado para cada cliente
    for index, row in df.iterrows():
        cliente = row['cliente']
        delta = row['Delta']

        if cliente not in healthscore_dict:
            healthscore_dict[cliente] = 10

        # Aplica o delta ao healthscore do cliente
        healthscore_dict[cliente] += delta

        # Garante que o healthscore esteja entre 0 e 10
        if healthscore_dict[cliente] > 10:
            healthscore_dict[cliente] = 10
        elif healthscore_dict[cliente] < 0:
            healthscore_dict[cliente] = 0

        # Atualiza o valor no DataFrame
        df.at[index, 'Healthscore'] = healthscore_dict[cliente]

    # cap healthscore at 10
    df['Healthscore'] = np.minimum(df['Healthscore'], 10)

    upload_to_sheets(df, sheet_name="Macfor", sheet_url = "https://docs.google.com/spreadsheets/d/1O1yv8pKPViWHIO-jH_NDG1N2Uy26QLM3WHSu56c4sD8/edit?gid=0#gid=0")

    # Remover as linhas duplicadas mantendo apenas a última ocorrência de cada semana
    df_last_occurrences = df.drop_duplicates(subset=['cliente', 'data'], keep='last')

    # Selecionar apenas as colunas desejadas
    df_last_occurrences = df_last_occurrences[['cliente', 'data', 'Healthscore']]

    upload_to_sheets(df_last_occurrences, sheet_name="New Macfor", sheet_url = "https://docs.google.com/spreadsheets/d/14fyrPri8Fr_6qL2rgnzKNoT3k6T3nR6Tyq0k1VEfhQ4/edit?gid=0#gid=0")

    # Inicializar o novo dataframe com as datas únicas, sorteadas em ordem crescente
    dates = pd.DataFrame(df_last_occurrences['data'].unique(), columns=['data'])
    dates = dates.sort_values(by='data').reset_index(drop=True)

    # Criar um dicionário para armazenar as notas de cada cliente, inicializando em 10
    clientes = df_last_occurrences['cliente'].unique()
    notas = {cliente: [10] * len(dates) for cliente in clientes}

    # Para cada cliente, atualizar as notas no dicionário conforme os ocorridos
    for _, row in df_last_occurrences.iterrows():
        cliente = row['cliente']
        data = row['data']
        nota = row['Healthscore']

        # Encontrar o índice correspondente à data no dataframe de datas
        date_index = dates[dates['data'] == data].index[0]

        # Atualizar todas as entradas seguintes com a nova nota
        notas[cliente][date_index:] = [nota] * (len(dates) - date_index)

    # Transformar o dicionário em um dataframe
    df_final = pd.DataFrame(notas)
    df_final.insert(0, 'data', dates['data'])

    # Definir a coluna 'data' como índice
    df_final.set_index('data', inplace=True)

    # Reamostrar o índice de datas para incluir todos os dias
    df_final = df_final.resample('D').asfreq()

    # Preencher os valores NaN resultantes da reamostragem com a última nota conhecida (forward fill)
    df_final.ffill(inplace=True)

    # Resetar o índice para transformar a coluna de datas em uma coluna novamente
    df_final.reset_index(inplace=True)

    upload_to_sheets(df_final, sheet_name="Macfor_Temporal_Series", sheet_url = "https://docs.google.com/spreadsheets/d/1G1-H1ztNkEE7oHINc02nAwvQGGLR_0useJIwL2t1kxw/edit?gid=0#gid=0")

    # save df to excel
    df.to_excel("outputs\\healthscore_calculado.xlsx", index=False)
    df_last_occurrences.to_excel("outputs\\healthscore_intermediario.xlsx", index=False)
    df_final.to_excel("outputs\\serie_temporal.xlsx", index=False)




