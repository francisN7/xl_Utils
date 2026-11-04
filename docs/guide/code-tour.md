# Code tour — como ler o código

**O que responde:** por onde começar, em que ordem ler cada camada e onde mexer
para cada tipo de mudança. **O que não responde:** a arquitetura em detalhe
(ver [`../reference/architecture.md`](../reference/architecture.md)), a UI (ver
[`ui.md`](../reference/ui.md)) nem o porquê das decisões (ver [`../adr/`](../adr/)).

## Antes de começar

```bash
uv sync
uv run pytest
uv run xl-utils
```

Abra uma ferramenta e execute uma planilha pequena. O tour faz mais sentido
depois de ver o fluxo funcionando uma vez.

## Mapa em uma tela

```text
app.py                          monta a janela e a navegação
└─ ui/pages/registry.py         lista as quatro ferramentas
   └─ ui/pages/<ferramenta>.py  conecta a página ao controller
      └─ ui/components/tool_layout.py
         │                      ciclo: entrada → formato → execução → prévia
         └─ controllers/<ferramenta>.py
            │                   orquestra leitura, seleção e SaveItem
            └─ core/tools/all_str.py
               │                leitura segura + remoção de emojis
               ├─ core/io.py    lê/grava cada formato
               ├─ core/mime.py  descobre o formato real
               ├─ core/tools/sheets.py  filtra as abas escolhidas
               └─ core/tools/<regra>.py regra pura da ferramenta
                  └─ core/save.py          grava só depois da escolha
```

## As paradas

### 1. Shell e navegação — `src/xl_utils/app.py`

`main` monta a sidebar, o hub e o conteúdo. `show(index)` troca a página e
`TOOLS`, em `ui/pages/registry.py`, é a única lista de ferramentas. Para
entender por que a sidebar não é `NavigationRail`, leia o ADR 0003.

**Observe:** o estado de cada ferramenta vive em `ui/state.py`, não na página.

### 2. Ciclo de uma ferramenta — `ui/components/tool_layout.py`

`_run` é o coração: lê o `ToolState`, chama `_check_formats`, bloqueia formato
não identificado, dispara o controller e entrega o resultado ao painel. A
gravação fica em `_save_clicked`/`_pick_and_save`, que só gravam depois da
escolha.

**Observe:** `_check_formats` é o gate de formato; ele não renomeia o arquivo.
`_fail` separa `WorkbookReadError`, `ValueError` e falha inesperada.

### 3. Uma página — `ui/pages/all_str.py`

A página só coleta a entrada, chama o controller e mostra o resultado. Em
ferramentas de lote, `ui/pages/batch.py` junta logs e prévias de vários arquivos.

**Observe:** nenhuma regra de planilha mora aqui.

### 4. Controller — `controllers/all_str.py`

`run_all_str` recebe o caminho e as abas escolhidas, chama `prepare_workbook`,
filtra com `filter_sheets` e devolve `AllStrOutcome` com `SaveItem` e `RunLog`.
Os demais controllers seguem o mesmo desenho: `CnjOutcome`, `CutOutcome` e
`MergeOutcome`.

**Observe:** nada é gravado; o controller devolve dados em memória.

### 5. Leitura segura — `core/tools/all_str.py`

`prepare_workbook` é a porta de entrada de todas as ferramentas. Ele lê com
`dtype=str`, aplica `remove_emojis` célula a célula e tenta um leitor alternativo
quando a leitura normal falha. O arquivo original nunca é tocado.

**Observe:** a leitura distingue “falhou” de “leu errado”. CSV com `;` e HTML com
cabeçalho de dois níveis são tratados em `core/io.py`; `.xls` não tem leitor
alternativo e falha com mensagem clara.

### 6. Formatos — `core/io.py` e `core/mime.py`

`mime.resolve_suffix` decide o leitor pelo conteúdo; `check_format` alimenta o
aviso da UI. Em `io.read_workbook`, cada formato tem seu caminho: openpyxl
(`.xlsx`/`.xlsm`), calamine (`.xls`), CSV com separador/encoding detectados e
HTML com duas passadas de converters.

**Observe:** `keep_default_na=False` mantém `NA`, `N/A` e `NULL` como texto;
célula vazia vira `""`. `read_headers` lê só o necessário para a UI.

### 7. Regras puras — `core/tools/`

- `sheets.py`: `filter_sheets` e `default_selection`.
- `cnj.py`: regex com lookarounds, normalização e `summarize_cnjs` em uma passada.
- `cut.py`: `split_frame`/`split_workbook`, sem tocar no disco.
- `merge.py`: `ColumnRef`/`ColumnGroup`, `move_column` e `merge_sheets`; o
  `ORIGEM` conta linhas de dados, não linhas físicas da planilha.

**Observe:** nenhum módulo daqui importa Flet ou abre diálogo.

### 8. Saída — `core/save.py` e `core/paths.py`

`SaveItem` guarda o nome sugerido, as abas e a pasta `output/` da origem.
`save_chosen` grava um arquivo ou vários em uma pasta; `save_to_output` usa o
atalho. `paths.unique_path` resolve colisão (`saida_001.xlsx`) e
`safe_file_part` prepara nome de arquivo a partir do nome da aba.

**Observe:** `SaveError` embrulha qualquer falha; a prévia não é apagada.

### 9. Testes — `tests/`

| Arquivo | Prova que… |
|---|---|
| `test_formats.py` | os quatro formatos leem texto, cabeçalhos, `NA` e CSV com `;` |
| `test_all_str.py` | o pipeline remove emojis e preserva zeros/quebras |
| `test_cnj.py` | a regex não pega CPF e a deduplicação ordena |
| `test_cut.py` | o recorte mantém o resto e nomes seguros |
| `test_merge.py` | ordem, `ORIGEM`, lacunas e colunas repetidas |
| `test_save.py` | nada é gravado antes da escolha e o lote usa pasta |
| `test_format_check.py` | conteúdo vence o nome e `.xlsm` não é divergência |
| `test_integration.py` | as quatro ferramentas rodam nos quatro formatos |

## Onde mexer para…

| Quero… | Vá a |
|---|---|
| suportar um formato novo | `core/mime.py` + `core/io.py` + teste em `test_formats.py` |
| criar uma ferramenta | `core/tools/<nova>.py` + controller + página + `ui/pages/registry.py` |
| mudar a leitura de texto/emojis | `core/tools/all_str.py` + `core/text.py` |
| mudar nome de arquivo de saída | `controllers/cut.py` ou `core/paths.py` |
| mudar a tela de salvar | `ui/components/result_panel.py` + `core/save.py` |
| mudar a regra do merge | `core/tools/merge.py` |
| mudar o aviso de formato | `core/mime.py` + `ui/components/tool_layout.py` |

## Invariantes

- `core/` não importa Flet, não abre diálogo e não imprime.
- Toda ferramenta lê por `prepare_workbook`, antes da regra específica.
- A leitura é texto (`dtype=str`) e preserva zeros, CNJ, quebras e `NA`.
- O arquivo do usuário nunca é renomeado nem alterado.
- Nada é gravado antes da escolha; `SaveItem` vive em memória.
- Erros de leitura e escrita são tipados (`WorkbookReadError`, `SaveError`).

## Limites conhecidos

- Datas do Excel viram texto ISO (`2024-01-02 00:00:00`), não o formato exibido.
- `.xls` não tem leitor alternativo; se o calamine falhar, o erro é final.
- A detecção de separador de CSV pode errar em arquivo atípico com aspas
  inconsistentes; o fallback tenta o motor Python.
- HTML sem tabela e planilha sem aba útil falham com mensagem, nunca em silêncio.
