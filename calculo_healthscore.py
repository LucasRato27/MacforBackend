import logging
import numpy as np
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials

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

df = pd.read_excel("outputs\\feedback_full.xlsx")

criterios = read_google_sheet("https://docs.google.com/spreadsheets/d/1YyiI5GZWP8orU-3YMEln6hKYKUJVrriTgiTyB6849qE/edit?gid=124241289#gid=124241289")
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

#Specify the healthscore column type.
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
        "https://docs.google.com/spreadsheets/d/1rGiD4Zab5BzY7xJYtnA1GfwqRH4pjlP-i8S-CE5cihs/edit?gid=0#gid=0").sheet1

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

upload_to_sheets(df, sheet_name="Macfor")

print(df)
# save df to excel

df.to_excel("outputs\\healthscore_calculado.xlsx", index=False)
