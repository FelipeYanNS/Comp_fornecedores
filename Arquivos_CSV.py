import os
import unicodedata
import pandas as pd
import ipywidgets as widgets
import numpy as np
from IPython.display import display
from google.colab import files
import chardet

# Caminho base
caminho_pasta = '/content/drive/MyDrive/Lançamentos Contábeis/'

# Remove acentos de uma string
def remover_acentos(txt):
    return unicodedata.normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

# Detecta a codificação de um arquivo
def detectar_encoding(caminho_arquivo):
    with open(caminho_arquivo, 'rb') as f:
        return chardet.detect(f.read(10000))['encoding']

# ------------------- ETAPA 1: LISTAGEM DE EMPRESAS -------------------

arquivos_csv = []
for raiz, dirs, arquivos in os.walk(caminho_pasta):
    for nome in arquivos:
        if nome.lower().endswith('.csv'):
            arquivos_csv.append(os.path.join(raiz, nome))

df_arquivos = pd.DataFrame(arquivos_csv, columns=['Caminho Completo'])
df_arquivos['Arquivo CSV'] = df_arquivos['Caminho Completo'].apply(os.path.basename)
df_arquivos['Diretoria'] = df_arquivos['Arquivo CSV'].str.extract(r'^(.*?)\s*-\s*')
empresas = sorted(df_arquivos['Diretoria'].dropna().unique().tolist())

# ------------------- ETAPA 2: LEITURA E CONSOLIDAÇÃO -------------------

def ao_clicar_botao(botao=None):
    empresa_escolhida = seletor_empresa.value
    print(f"\nEmpresa selecionada: {empresa_escolhida}")

    arquivos_filtrados = []
    for raiz, _, arquivos in os.walk(caminho_pasta):
        for nome in arquivos:
            if nome.lower().endswith('.csv'):
                if remover_acentos(nome).lower().startswith(remover_acentos(empresa_escolhida).lower()):
                    arquivos_filtrados.append(os.path.join(raiz, nome))

    lista_dfs = []
    for caminho in arquivos_filtrados:
        try:
            encoding = detectar_encoding(caminho)
            df = pd.read_csv(caminho, encoding=encoding, sep=None, engine='python')
            lista_dfs.append(df)
        except Exception as e:
            print(f"Erro ao ler o arquivo {caminho}: {e}")

    if lista_dfs:
        df1 = pd.concat(lista_dfs, ignore_index=True)

        # ------------------- ETAPA 3: PRÉ-PROCESSAMENTO -------------------

        df1['Valor'] = df1['Valor'].astype(str).str.replace(',', '.').str.strip()
        df1['Valor'] = pd.to_numeric(df1['Valor']) * 1

        df1 = df1.replace(['', 'Documento', np.nan], '0')
        df1['Documento'] = pd.to_numeric(df1['Documento'], errors='coerce').where(
            pd.to_numeric(df1['Documento'], errors='coerce').notna(),
            df1['Documento']
        )

        df1['Conta'] = df1['Conta'].astype(str)
        df1 = df1[df1['Conta'].str.startswith('2.1.2.01')]

        df1['Tipo'] = df1['Tipo'].astype(str)
        df1 = df1[df1['Tipo'].str.startswith(('1', '0'))]

        df1['Saldo'] = df1.apply(
            lambda row: row['Valor'] if row['Ação'] == 'C' else -row['Valor'],
            axis=1
        )

        # ------------------- ETAPA 4: TABELA DINÂMICA -------------------

        df1['Saldo'] = pd.to_numeric(df1['Saldo'], errors='coerce')
        soma_por_descricao = df1.groupby('Conta reduz.')['Saldo'].sum()

        descricoes_validas = soma_por_descricao[
            (soma_por_descricao.abs() > 0.009) & soma_por_descricao.notnull()
        ].index

        df1_filtrado = df1[df1['Conta reduz.'].isin(descricoes_validas)]

        tabela_dinamica = pd.pivot_table(
            df1_filtrado,
            index=['Conta reduz.', 'Documento'],
            values='Saldo',
            aggfunc='sum',
            sort=False
        ).reset_index()

        tabela_dinamica['Saldo'] = pd.to_numeric(tabela_dinamica['Saldo'], errors='coerce')

        # ------------------- ETAPA 5: COMPLEMENTAÇÃO -------------------

        df_unico = df1.drop_duplicates(
            subset=["Conta reduz.", "Documento"], keep="first"
        )[
            ["Conta reduz.", "Documento", "Descrição.1", "Data"]
        ]

        tabela_dinamica["Documento"] = tabela_dinamica["Documento"].astype(str)
        df_unico["Documento"] = df_unico["Documento"].astype(str)

        tabela_dinamica = tabela_dinamica.merge(
            df_unico,
            on=["Conta reduz.", "Documento"],
            how="left"
        )

        tabela_dinamica['Documento'] = pd.to_numeric(
            tabela_dinamica['Documento'], errors='coerce'
        ).where(
            pd.to_numeric(tabela_dinamica['Documento'], errors='coerce').notna(),
            tabela_dinamica['Documento']
        )

        tabela_dinamica = tabela_dinamica.rename(columns={
            "Descrição.1": "Fornecedor",
            "Documento": "Nota Fiscal",
            "Saldo": "Valor"
        })

        tabela_filtrada = tabela_dinamica[
            (tabela_dinamica["Valor"].abs() > 0.009) & tabela_dinamica["Valor"].notnull()
        ]

        colunas_ordenadas = ["Conta reduz.", "Fornecedor", "Nota Fiscal", "Data", "Valor"]
        tabela_filtrada = tabela_filtrada[colunas_ordenadas]

        # ------------------- ETAPA 6: EXPORTAÇÃO -------------------

        nome_arquivo = f"{empresa_escolhida} - Composição dos fornecedores.xlsx"
        tabela_filtrada.to_excel(nome_arquivo, index=False)
        display(files.download(nome_arquivo))

    else:
        print(f"\nNão foi possível ler os arquivos da empresa '{empresa_escolhida}'.")

# ------------------- INTERFACE -------------------

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
