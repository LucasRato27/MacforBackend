import pandas as pd
from numpy import nan as NaN

def calcular_media_problemas(df):
    # Remover linhas com valores ausentes nas colunas de interesse
    df.replace("", NaN, inplace=True)
    df2 = df.dropna(subset=['motivacao da solicitacao', 'cliente', 'Time', 'tipo de solicitacao']).copy()
    
    # Verificar quantas linhas foram removidas
    print(f"Linhas removidas: {len(df) - len(df2)}")
    
    # Converter data ideal para datetime, caso não esteja
    df2['data ideal'] = pd.to_datetime(df2['data ideal'], errors='coerce')

    # Agrupar por cliente, time e tipo de solicitacao
    grouped_total = df2.groupby(['cliente', 'Time', 'tipo de solicitacao'])

    # Lista para armazenar os resultados
    resultados = []

    # Iterar sobre todos os grupos do total
    for (cliente, time, tipo_solicitacao), grupo_total in grouped_total:
        # Total de problemas (número de linhas)
        total_problemas_historico = len(grupo_total)

        # Calcular a média histórica
        menor_data = grupo_total['data ideal'].min()
        dias_totais = (pd.Timestamp.now() - menor_data).days
        media_historica = total_problemas_historico / dias_totais if dias_totais > 0 else 0

        # Filtrar para considerar apenas os últimos 14 dias
        data_limite = pd.Timestamp.now() - pd.Timedelta(days=14)
        grupo_14_dias = grupo_total[grupo_total['data ideal'] >= data_limite]

        # Total de problemas nos últimos 14 dias (número de linhas)
        total_problemas_14_dias = len(grupo_14_dias)

        # Se não houver problemas nos últimos 14 dias, a média é nula
        if total_problemas_14_dias > 0:
            media_problemas_14_dias = total_problemas_14_dias / 14  # média de problemas por dia nos últimos 14 dias
        else:
            media_problemas_14_dias = 0  # ou NaN, se preferir

        # Verificar se a média dos últimos 14 dias é maior que a média histórica
        acima_media_historica = media_problemas_14_dias > media_historica

        # Adicionar os resultados à lista
        resultados.append({
            'cliente': cliente,
            'time': time,
            'tipo de solicitacao': tipo_solicitacao,
            'media_problemas_14_dias': media_problemas_14_dias,
            'media_historica': media_historica,
            'acima_media_historica': acima_media_historica
        })

    # Converter a lista de resultados em um DataFrame
    resultados_df = pd.DataFrame(resultados)

    # Debug: Mostrar os resultados intermediários
    return resultados_df
