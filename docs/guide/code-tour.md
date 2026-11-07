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
└─ ui/pages/registry.py         lista as ferramentas
   └─ ui/pages/<ferramenta>.py  conecta a página ao controller
      └─ ui/components/tool_layout.py
         │                      ciclo: entrada → formato → execução em segundo plano → prévia
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

`main` monta a sidebar, o hub e o conteúdo. Antes de qualquer controle, lê o
tema de `shared/settings.py` e chama `theme.apply(mode)`; `show(index)` troca a
página e `TOOLS`, em `ui/pages/registry.py`, é a única lista de ferramentas. Para
entender por que a sidebar não é `NavigationRail`, leia o ADR 0003.

**Observe:** o estado de cada ferramenta vive em `ui/state.py`, não na página.

### 2. Ciclo de uma ferramenta — `ui/components/tool_layout.py`

`_run` é o coração: valida o `ToolState`, chama `_check_formats`, bloqueia
formato não identificado e entrega o handler a `_execute_async`. Quando a página
define `pre_run` (vinculação), ele roda antes e pode abrir o diálogo de
reexecução. Com página, o trabalho vai para `asyncio.to_thread`; sem página,
roda no próprio loop. Os
marcos de `shared/progress.py` e as etapas dos controllers voltam por uma fila
e atualizam barra, texto e log no loop. Enquanto um arquivo roda, a barra fica
indeterminada; entre arquivos, ela avança. O botão vira “Cancelar” durante a
execução e aciona o `CancelToken` entregue ao handler. A gravação fica em
`_save_clicked`/`_pick_and_save`, que só gravam depois da escolha.

**Observe:** `_check_formats` é o gate de formato; ele não renomeia o arquivo.
`_fail` separa `WorkbookReadError`, `ValueError` e falha inesperada. Nenhum
`update` de UI parte da thread de trabalho: `ResultPanel` e `PreviewTable` usam
o dispatcher do loop.

### 3. Uma página — `ui/pages/all_str.py`

A página só coleta a entrada, chama o controller e mostra o resultado. Em
ferramentas de lote, `ui/pages/batch.py` junta logs e prévias de vários arquivos;
cada página checa o `CancelToken` entre arquivos e passa o reporter ao
controller. Assim as etapas viram log ao vivo sem a página conhecer os detalhes
de leitura e cálculo.

**Observe:** nenhuma regra de planilha mora aqui.

### 4. Controller — `controllers/all_str.py`

`run_all_str` recebe o caminho, as abas escolhidas e o reporter, chama
`prepare_workbook`, filtra com `filter_sheets` e devolve `AllStrOutcome` com
`SaveItem` e `RunLog`. As etapas são registradas com `reporter.note(...)`: vão
para o log final e aparecem durante a execução. Os demais controllers seguem o
mesmo desenho: `CnjOutcome`, `CutOutcome`, `MergeOutcome` e `LinkOutcome`.

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
- `cut.py`: `split_frame`/`split_workbook` e `split_frame_by_parts`/
  `split_workbook_by_parts`, sem tocar no disco.
- `merge.py`: `ColumnRef`/`ColumnGroup`, `move_column` e `merge_sheets`; o
  resultado abre com `ORIGEM` (`stem - aba`) e `LINHA_ORIGEM` (linha de dados
  numerada no total, com zeros à esquerda).
- `link.py`: `LinkConfig`/`SheetSpec`, `find_target_sheet`, `link_agenda` e
  `link_financeiro`; compara CNJ/PASTA/PROTOCOLO/nome brutos, grava `VINCULA?`
  e `VINCULA (POR NOME)?`, trata `MIGRAÇÃO` como sentinela e aplica as opções
  de nome na descrição e campo único. `shared/configs.py` carrega o
  `headers.json` empacotado ou o override local.

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
| `test_progress.py` | contagem, log ao vivo, token e cancelamento entre arquivos |
| `test_link.py` | prioridade, valor bruto, CNJ, FINANCEIRO, opções, `MIGRAÇÃO` e log por etapa |
| `test_link_page.py` | fluxos exigidos e opções habilitadas por arquivo |
| `test_layout.py` | o layout alterna cartões e preserva o estado do quadro |
| `test_merge_page.py` | a tela cheia preserva grupos, seleção e ordem |
| `test_theme.py` | contraste e troca de tema sem perder a estrutura |
| `test_settings.py` | a preferência de tema persiste e cai no escuro |
| `test_ui_state.py` | trocar o arquivo reseta o resultado sem perder opções |
| `test_configs.py` | JSON empacotado e override por `%LOCALAPPDATA%` |
| `test_integration.py` | as ferramentas de lote rodam nos quatro formatos |

## Onde mexer para…

| Quero… | Vá a |
|---|---|
| suportar um formato novo | `core/mime.py` + `core/io.py` + teste em `test_formats.py` |
| criar uma ferramenta | `core/tools/<nova>.py` + controller + página + `ui/pages/registry.py` |
| mudar a leitura de texto/emojis | `core/tools/all_str.py` + `core/text.py` |
| mudar nome de arquivo de saída | `controllers/cut.py` ou `core/paths.py` |
| mudar a tela de salvar | `ui/components/result_panel.py` + `core/save.py` |
| mudar a regra do merge | `core/tools/merge.py` |
| mudar a regra da vinculação | `core/tools/link.py` + `controllers/link.py` + `ui/pages/link.py` |
| mudar um cabeçalho padrão | `src/xl_utils/configs/headers.json` (ou override local) |
| mudar a regra do recorte | `core/tools/cut.py` + `controllers/cut.py` + `ui/pages/cut.py` |
| mudar o aviso de formato | `core/mime.py` + `ui/components/tool_layout.py` |
| mudar a barra de progresso | `shared/progress.py` + `ui/components/result_panel.py` |
| mudar o log ao vivo ou o cancelamento | `shared/progress.py` + `ui/components/tool_layout.py` + páginas |
| mudar tema ou preferência salva | `ui/theme.py` + `shared/settings.py` + `ui/components/sidebar.py` |

## Invariantes

- `core/` não importa Flet, não abre diálogo e não imprime.
- Toda ferramenta lê por `prepare_workbook`, antes da regra específica.
- A leitura é texto (`dtype=str`) e preserva zeros, CNJ, quebras e `NA`.
- O arquivo do usuário nunca é renomeado nem alterado.
- Nada é gravado antes da escolha; `SaveItem` vive em memória.
- Erros de leitura e escrita são tipados (`WorkbookReadError`, `SaveError`).
- A UI só é atualizada no loop da página; a thread de trabalho usa fila.

## Limites conhecidos

- Datas do Excel viram texto ISO (`2024-01-02 00:00:00`), não o formato exibido.
- `.xls` não tem leitor alternativo; se o calamine falhar, o erro é final.
- A detecção de separador de CSV pode errar em arquivo atípico com aspas
  inconsistentes; o fallback tenta o motor Python.
- HTML sem tabela e planilha sem aba útil falham com mensagem, nunca em silêncio.
