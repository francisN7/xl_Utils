import pandas as pd
import json

dados = None
with open('pesquisa.json', 'r', encoding='utf-8') as json_f:
    dados = json.load(json_f)

dados = dados['resultado']
df = pd.DataFrame(dados)

df.to_excel('processos_completos.xlsx', index=False)