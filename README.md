
---

## 📊 Funcionalidade Geral

Cada script permite:

- Selecionar uma empresa a partir do nome dos arquivos (o critério é até o sinal de menos - ).
- Ler e consolidar arquivos contábeis de diferentes formatos conforme cada código.
- Tratar e limpar dados (valores, documentos, contas, datas).
- Filtrar lançamentos da conta `2.1.2.01`(Código contábel da conta de Fornecedores do Passivo).
- Calcular saldos com base no tipo de ação (Crédito ou Débito).
- Agrupar dados por fornecedor e nota fiscal.
- Gerar automaticamente um arquivo Excel por empresa.

---
## ✅ Descrição dos Notebooks

### `Arquivos_CSV.py`

Processa múltiplos arquivos da extenção `.csv`

**Principais recursos:**
- Busca e filtra arquivos `.csv` na estrutura de pastas.
- Filtra por lançamentos da conta `2.1.2.01`.
- Calcula saldos e agrupa por `Código do Fornecedor` e `Nota Fiscal`.
- Exporta o resultado para Excel.

📎 **Saída:**  
`<Nome da Empresa> - Composição dos fornecedores.xlsx`

---

### `Arquivos_txt.py`

Processa múltiplos arquivos da extenção ".txt" 

**Principais recursos:**
- Busca e filtra arquivos `.txt` na estrutura de pastas.
- Remove acentuação dos nomes de arquivos para normalização.
- Filtra por lançamentos da conta `21201`.
- Calcula saldos e agrupa por `Nome do Fornecedor` e `Nota Fiscal`.
- Exporta o resultado para Excel.

📎 **Saída:**  
`<Nome da Empresa> - Composição dos fornecedores.xlsx`

---

### `Arquivos_xls_e_xlsx.py`

Processa múltiplos arquivos da extenção `.xls` ou `.xlsx`

**Principais recursos:**
- Busca e filtra arquivos `.xls` ou `.xlsx` na estrutura de pastas.
- Filtra por lançamentos da conta `2.1.2.01`.
- Calcula saldos e agrupa por `Código do Fornecedor` e `Nota Fiscal`.
- Exporta o resultado para Excel.

📎 **Saída:**  
`<Nome da Empresa> - Composição dos fornecedores.xlsx`

---

## 🛠️ Requisitos

- O código foi feito e pensado para ser utilizado no [Google Colab](https://colab.research.google.com/) em conjunto com o [Google Drive](https://drive.google.com/).
- Os dados devem ser extraido dos lançamentos contábeis no sistema [ERP UAU - Globaltec](https://www.globaltec.com.br/erp-uau/).


