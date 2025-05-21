import os
import unicodedata
import pandas as pd
import ipywidgets as widgets
from IPython.display import display
from google.colab import files

# Caminho base
caminho_pasta = '/content/drive/MyDrive/Lançamentos Contábeis/'

# Remove acentos
def remover_acentos(txt):
    return unicodedata.normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

# ------------------- ETAPA 1: LISTAGEM DE EMPRESAS -------------------

arquivos_txt = []
for raiz, dirs, arquivos in os.walk(caminho_pasta):
    for nome in arquivos:
        if nome.endswith('.txt'):
            arquivos_txt.append(os.path.join(raiz, nome))

df_arquivos = pd.DataFrame(arquivos_txt, columns=['Caminho Completo'])
df_arquivos['Arquivo .txt'] = df_arquivos['Caminho Completo'].apply(os.path.basename)
df_arquivos['Diretoria'] = df_arquivos['Arquivo .txt'].str.extract(r'^(.*?)\s*-\s*')
empresas = sorted(df_arquivos['Diretoria'].dropna().unique().tolist())

# ------------------- ETAPA 2: PROCESSAMENTO -------------------

def ao_clicar_botao(botao=None):
    empresa = seletor_empresa.value
    print(f"\nEmpresa selecionada: {empresa}")

    arquivos_filtrados = []
    for raiz, _, arquivos in os.walk(caminho_pasta):
        for nome in arquivos:
            if nome.endswith('.txt'):
                if remover_acentos(nome).startswith(remover_acentos(empresa)):
                    arquivos_filtrados.append(os.path.join(raiz, nome))

    lista_dfs = []
    for caminho in arquivos_filtrados:
        try:
            df = pd.read_csv(caminho, sep='\t', encoding='latin1')
            lista_dfs.append(df)
        except Exception as e:
            print(f"Erro ao ler {caminho}: {e}")

    if lista_dfs:
        df1 = pd.concat(lista_dfs, ignore_index=True)
        df1['Valor'] = pd.to_numeric(df1['Valor'].astype(str).str.replace(',', '.').str.strip(), errors='coerce')
        df1['Conta'] = df1['Conta'].astype(str)
        df1 = df1[df1['Conta'].str.startswith('21201')]
        df1['Saldo'] = df1.apply(lambda row: row['Valor'] if row['Ação'] == 'C - Crédito' else -row['Valor'], axis=1)

        soma = df1.groupby('Descrição.1')['Saldo'].sum()
        descricoes_validas = soma[(soma.abs() > 0.009) & (soma.notnull())].index
        df1 = df1[df1['Descrição.1'].isin(descricoes_validas)]

        tabela = pd.pivot_table(df1, index=['Descrição.1', 'Documento'], values='Saldo', aggfunc='sum').reset_index()
        tabela['Documento'] = tabela['Documento'].astype(str).str.extract('(\d+)')[0].astype('Int64')
        tabela = tabela[tabela['Saldo'] != 0]

        df_meta = df1.drop_duplicates(subset="Descrição.1", keep="last")[["Descrição.1", "Conta reduz.", "Data"]]
        tabela = tabela.merge(df_meta, on="Descrição.1", how="left")

        tabela = tabela.rename(columns={
            "Descrição.1": "Fornecedor",
            "Documento": "Nota Fiscal",
            "Saldo": "Valor"
        })[["Conta reduz.", "Fornecedor", "Nota Fiscal", "Data", "Valor"]]

        nome_arquivo = f"{empresa} - Composição dos fornecedores.xlsx"
        tabela.to_excel(nome_arquivo, index=False)
        display(files.download(nome_arquivo))
    else:
        print(f"\nNão foi possível ler os arquivos da empresa '{empresa}'.")

# ------------------- ETAPA 3: INTERFACE -------------------

seletor_empresa = widgets.Dropdown(
    options=empresas,
    description='Empresa:',
    layout=widgets.Layout(width='50%')
)

botao_confirmar = widgets.Button(
    description='Confirmar',
    button_style='success'
)

botao_confirmar.on_click(ao_clicar_botao)
display(seletor_empresa, botao_confirmar)
