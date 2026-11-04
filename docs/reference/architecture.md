# Arquitetura

**O que responde:** camadas, fluxo de dados, leitura segura, detecção de
formato e convenções do core. **O que não responde:** a interface (ver
`ui.md`) nem o porquê das decisões (ver `../adr/`).

## Camadas

| Camada | Pasta | Regra |
|---|---|---|
| Core | `src/xl_utils/core/` | Regra pura, sem Flet, sem diálogo, sem `print`. |
| Controllers | `src/xl_utils/controllers/` | Orquestra core + threading + progresso. |
| UI | `src/xl_utils/ui/` | Coleta entrada e exibe resultado; não contém regra. |
| Shared | `src/xl_utils/shared/` | Logging, config e clipboard. |

Uma ferramenta = um módulo em `core/tools/` + um controller + uma página.

## Fluxo de dados

```text
arquivo escolhido
  → controller
  → all_str.prepare_workbook (leitura segura + emojis)
  → sheets.filter_sheets (abas escolhidas)
  → regra da ferramenta em core/tools/
  → save_workbook / resultado em memória
  → result panel (status, caminho, log e prévia)
```

## Leitura segura

Toda ferramenta começa pelo pipeline do `all_str`, sempre antes da regra
específica:

1. lê todas as abas com `dtype=str`;
2. remove emojis com `emoji.replace_emoji`;
3. preserva o texto da célula, inclusive quebras de linha;
4. só tenta reparo quando a leitura falha, sem `shell=True`.

Excel é lido com `openpyxl` para `.xlsx`/`.xlsm` e com `calamine` para `.xls`
(pacote `python-calamine`). `core/tools/all_str.py` expõe
`prepare_workbook(path)`, que devolve `{nome_da_aba: DataFrame}` já limpo. As
demais ferramentas importam essa função antes de aplicar a própria regra.
`controllers/all_str.py` orquestra a leitura, a gravação em `output/` e o log;
`ui/pages/all_str.py` só conecta a página.

Quando a leitura normal falha, o pipeline tenta **um** leitor mais tolerante,
de acordo com o formato real: `openpyxl` em modo somente leitura para
`.xlsx`/`.xlsm`, codificações alternativas (`utf-8-sig`, `cp1252`, `latin-1`)
para `.csv` e outros parsers para `.html`. Se ainda assim falhar, levanta
`WorkbookReadError` com a causa original — nunca renomeia nem altera o arquivo
do usuário.

O objetivo é não perder zeros à esquerda, CNJ/CPF e valores que o Excel
converteria em notação científica. A ferramenta “Tratamento de texto” também
expõe esse pipeline sozinha, para conversão e reparo explícitos. O
`read_html` do pandas não aceita `dtype`; para HTML, a leitura faz uma segunda
passada com converters e mantém os zeros à esquerda.

## Seleção de abas

`core/io.list_sheets(path)` devolve os nomes na ordem do arquivo. Excel lê só os
metadados com `pd.ExcelFile` e o engine do formato real; CSV devolve
`["Planilha1"]`; HTML precisa ser lido, porque cada tabela vira `PáginaN`.
Falha de leitura sobe como `ValueError` com o nome do arquivo.

`core/tools/sheets.filter_sheets(sheets, selected)` mantém apenas as abas
escolhidas, na ordem original e com os mesmos nomes. `None` significa todas;
conjunto vazio ou nome inexistente levanta `ValueError`.
`default_selection` define o padrão conforme a ferramenta: no lote (texto, CNJ
e recorte) todas as abas de todos os arquivos; no merge, a primeira de cada um.
Ver ADR 0006.

A seleção vive em `ToolState.sheet_names` e `ToolState.selected_sheets`, por
arquivo; trocar a lista de arquivos recarrega os nomes e reaplica o padrão. Os
controllers recebem `selected` e filtram logo depois do `prepare_workbook`,
antes da regra da ferramenta.

## Lote de arquivos

Texto, CNJ e recorte aceitam vários arquivos. A página monta a lista de
`(origem, abas)` com `ui/pages/batch.py`, chama o controller uma vez por arquivo
e junta logs e prévias; cada saída fica no `output/` da própria origem. O merge
continua sendo o único que produz uma saída única. Ver ADR 0006.

## Detecção de formato

`core/mime.py` usa `puremagic` no conteúdo e nunca renomeia o arquivo do
usuário. Quando o detectado é genérico (`.txt`) e a extensão original é
suportada, a extensão original vence. Formatos: `.xlsx`, `.xlsm`, `.xls`,
`.csv`, `.html` e `.htm`.

## Saída

`core/paths.py` cria a pasta e devolve um nome livre (`saida_001.xlsx`).
`core/io.py` grava todas as abas em um `.xlsx` com nomes saneados (limite de 31
caracteres e caracteres inválidos do Excel). O arquivo de origem nunca é
alterado.

## Ferramentas

| Ferramenta | Módulo | Estado |
|---|---|---|
| Tratamento de texto | `core/tools/all_str.py` | pronta |
| Extrair CNJs | `core/tools/cnj.py` | pronta |
| Recortar planilha | `core/tools/cut.py` | pronta |
| Mesclar planilhas | `core/tools/merge.py` | pronta |

## Extração de CNJ

`core/tools/cnj.py` reconhece o formato pontuado
(`NNNNNNN-DD.AAAA.J.TR.OOOO`) e 20 dígitos consecutivos, sem aceitar trecho de
número maior. `normalize_cnj` devolve sempre o formato pontuado; `collect_cnjs`
percorre todas as abas e célula a célula, remove duplicatas e ordena a lista.
`controllers/cnj.py` grava `output/<nome> lista cnj.xlsx` com a coluna
`PROCESSOS` e registra encontrados, duplicados e únicos no log.

## Recorte

`core/tools/cut.py` divide cada aba em blocos sequenciais de N linhas; o resto
fica no último bloco e uma aba vazia ainda gera um arquivo. `controllers/cut.py`
lê pelo `prepare_workbook`, filtra as abas escolhidas, salva cada bloco em
`output/` e usa `<stem>_Recorte_NNN.xlsx` (ou `<stem>_<aba>_Recorte_NNN.xlsx`
com várias abas processadas), saneando caracteres inválidos de nome de arquivo.
O campo de linhas é editável na página e vive em `ToolState.options`.

## Mesclagem

`core/tools/merge.py` recebe uma sequência de `(arquivo, aba, DataFrame)` e uma
lista de `ColumnGroup`, concatena na mesma ordem e descarta apenas abas sem
linhas. Cada grupo vira uma coluna de saída: o primeiro `ColumnRef` define o
cabeçalho e os demais alimentam a mesma coluna; `group_by_name` agrupa
automaticamente colunas de mesmo nome. O núcleo valida que uma aba contribui com
no máximo uma coluna por saída, preenche lacunas com `NaN`, insere `ORIGEM` como
primeira coluna no formato `<arquivo> - <aba> - <linha>` e desempata cabeçalhos
repetidos com sufixo `_2`.

`controllers/merge.py` lê cada fonte pelo `prepare_workbook`, filtra as abas com
`filter_sheets` e chama `merge_sheets`; exige ao menos duas abas com dados e
grava `output/Merge.xlsx` na pasta da primeira origem. `inspect_columns` usa
`core/io.read_headers` para devolver os `ColumnRef`s sem carregar as linhas; a
página monta o quadro arrastável e guarda os grupos em `ToolState.options`.
`move_column` concentra a regra de mover/juntar chips. O painel é reconstruído
quando arquivos ou abas mudam.

## Testes

O core é testado com `pytest` e `tmp_path`; a UI é validada por smoke manual
enquanto não houver regressão que justifique teste de widget. O teste funcional
do `all_str` gera 1.000 linhas fictícias em memória, roda em CSV e XLSX e
confere zeros à esquerda, numeração CNJ-like, remoção de emojis e quebras de
linha.

`tests/test_formats.py` percorre `.xlsx`, `.xls`, `.csv` e `.html` com as mesmas
linhas fictícias e confere `read_workbook`, `list_sheets`, `read_headers` e
`prepare_workbook`; `tests/test_integration.py` roda as quatro ferramentas sobre
os quatro formatos, incluindo origens mistas no merge e a imutabilidade das
origens. O `.xls` é uma fixture binária mínima em `tests/fixtures/minimo.xls`,
gerada uma vez com `xlwt` e **sem** adicionar a dependência ao projeto.

## Decisões

- [ADR 0001](../adr/0001-stack-ui-e-ambiente.md) — stack, uv e Flet.
- [ADR 0002](../adr/0002-arquitetura-core-ui.md) — camadas.
- [ADR 0004](../adr/0004-leitura-segura-e-emojis.md) — leitura segura e emojis.
