import pandas as pd
import json

df = pd.read_excel("tarefas_raw.xlsx")
print(df.head())

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
df['campos personalizados'] = df['campos personalizados'].str.replace("'", '"')
df['campos personalizados'] = df['campos personalizados'].apply(json.loads)

# Aplicar a função a cada coluna de campos personalizados
for col in df['campos personalizados'][0].keys():
    print(col)

df["custom_37"] = df["campos personalizados"].apply(lambda x: extrair_labels(x["custom_37"]) if "custom_37" in x else None)
df["custom_38"] = df["campos personalizados"].apply(lambda x: extrair_labels(x["custom_38"]) if "custom_38" in x else None)
df["custom_39"] = df["campos personalizados"].apply(lambda x: extrair_labels(x["custom_39"]) if "custom_39" in x else None)
df["custom_40"] = df["campos personalizados"].apply(lambda x: extrair_labels(x["custom_40"]) if "custom_40" in x else None)

print(df.head()) 

# Renomear as colunas de campos customizáveis
df = df.rename(columns={
    'custom_37': 'tipo de solicitacao',
    'custom_38': 'tipo de job',
    'custom_39': 'aderencia ao briefing',
    'custom_40': 'numero de anexo esperados',
})

df.to_excel("tarefas_feitas.xlsx", index=False)