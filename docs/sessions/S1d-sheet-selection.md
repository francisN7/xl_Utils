# S1d — Seleção de abas

## Objetivo

Permitir escolher, por planilha, quais abas entram na ferramenta; a seleção vale
para `all_str`, `cnj` e `cut`, e os nomes das abas são preservados na saída.

## Fora de escopo

Migrar `merge` (S1e); arrastar colunas; mudar a regra de cada ferramenta além do
filtro de abas; selecionar abas por intervalo (ex.: “1 a 5”).

## Tarefas

1. Criar `core/io.list_sheets(path)`:
   - Excel lê só os nomes (`pd.ExcelFile`) com o engine correto;
   - CSV devolve `["Planilha1"]`;
   - HTML devolve os nomes sintéticos de `read_workbook`;
   - erro de leitura sobe como exceção clara.
2. Criar `core/tools/sheets.py` com `filter_sheets(sheets, selected)`:
   - `None` mantém tudo; conjunto vazio ou nome inexistente levanta
     `ValueError`;
   - preserva a ordem original e os mesmos nomes.
3. Criar `ui/components/sheet_selector.py`:
   - chips pequenos e clicáveis, agrupados por arquivo quando houver vários;
   - “Todas” e “Limpar” + contador “N de M”;
   - seleção padrão: um arquivo → todas; vários → primeira aba de cada;
   - callback entrega `dict[Path, set[str]]`.
4. Guardar em `ToolState`:
   - `sheet_names: dict[Path, list[str]]`;
   - `selected_sheets: dict[Path, set[str]]`;
   - trocar arquivo recarrega nomes e reaplica o padrão.
5. Integrar o seletor ao card “1. Entrada” do `ToolLayout`, abaixo da lista de
   arquivos, sem quebrar as ferramentas que ainda não têm run handler.
6. Atualizar os controllers e as páginas:
   - `run_all_str(source, selected=None)` salva só as abas escolhidas;
   - `run_cnj(source, selected=None)` procura só nas abas escolhidas;
   - `run_cut(source, rows_per_file, selected=None)` recorta só as escolhidas;
   - seleção vazia mostra erro claro na UI antes de executar.
7. Criar `tests/test_sheets.py` e ampliar os testes das três ferramentas:
   - `list_sheets`, filtro, ordem, nome inexistente e seleção vazia;
   - saída do `all_str` só com as abas marcadas;
   - CNJ de aba não marcada não aparece;
   - recorte só das abas marcadas e nomes coerentes.
8. Atualizar `CURRENT.md`, roadmap, `CHANGELOG.md`, `reference/architecture.md`
   e `reference/ui.md`.

## Aceite

- [ ] chips aparecem após escolher o arquivo e refletem a seleção
- [ ] “Todas” marca tudo e “Limpar” desmarca tudo
- [ ] padrão é todas as abas para um arquivo e primeira de cada para vários
- [ ] `all_str` grava só as abas selecionadas, com os mesmos nomes
- [ ] `cnj` ignora abas não selecionadas
- [ ] `cut` recorta só as abas selecionadas
- [ ] seleção vazia não executa e mostra mensagem clara
- [ ] `ruff`, `pytest` e `docs:check` verdes

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec,
`docs/reference/architecture.md`, `docs/reference/ui.md`,
`core/io.py`, `core/tools/all_str.py`, `controllers/all_str.py`,
`controllers/cnj.py`, `controllers/cut.py` e `ui/components/tool_layout.py`.
Consultar `ui/pages/*.py` só ao conectar a seleção.

## Arquivos prováveis

- `src/xl_utils/core/io.py`
- `src/xl_utils/core/tools/sheets.py`
- `src/xl_utils/ui/components/sheet_selector.py`
- `src/xl_utils/ui/components/tool_layout.py`
- `src/xl_utils/ui/state.py`
- `src/xl_utils/controllers/all_str.py`, `cnj.py`, `cut.py`
- `src/xl_utils/ui/pages/all_str.py`, `cnj.py`, `cut.py`
- `tests/test_sheets.py`

## Riscos

- `list_sheets` em HTML exige leitura; não bloquear a UI em arquivo gigante.
- CSV/HTML têm nomes sintéticos; não prometer abas que não existem.
- Seleção presa a um arquivo antigo após trocar a lista; sempre recarregar.
- Chip com nome longo pode estourar a largura; usar `Row(wrap=True)`.
- `cut` muda o padrão de nome conforme a quantidade de abas selecionadas.

## Próximo depois desta

S1e — merge em um único modo, com coluna `ORIGEM` e alinhamento manual de
colunas (ver ADR 0005).
