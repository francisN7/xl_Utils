# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S2b — logging e erros
- **Próxima:** S2c — opções reais ou nada (`docs/sessions/S2c-opcoes-reais.md`)
- **Ciclo:** 0002 — Fase 2 — Consolidação
- **Retorno:** `shared/log.py`, `result_panel.py`, `tool_layout.py`, `state.py`
- **Decisões abertas:** nenhuma

## Pronto

- Ambiente uv/Python 3.15, Flet desktop e pandas 3.1; MVC híbrido e tema Dracula.
- `prepare_workbook` lê como texto, remove emojis, repara e falha como
  `WorkbookReadError`.
- Texto, CNJ, recorte e merge salvam em `output/`; os três primeiros aceitam
  lote e processam cada origem separadamente.
- Seleção de abas por chips e `default_selection` por ferramenta; merge com
  `ORIGEM` e quadro de colunas arrastáveis (chips).
- Integração cobre `.xlsx`, `.xls`, `.csv` e `.html`; `.xls` usa
  `tests/fixtures/minimo.xls`.
- HTML preserva zeros à esquerda com a segunda passada de converters.
- Reparo testado com CSV cp1252; arquivo inválido sobe `WorkbookReadError`.
- `RunLog` grava `(nível, texto)`, itera como linhas e alimenta o `ToolState.log`.
- `ToolLayout._run` separa leitura, seleção e falha inesperada; guarda traceback
  em `error_detail` e mostra a mensagem original.
- “Copiar diagnóstico” traz versões (fallback “desconhecida”), arquivos, abas,
  opções, causa e traceback.

## Próximo passo

S2c: remover os checkboxes desabilitados de Texto e CNJ e só mostrar o card
“2. Opções” quando houver algo editável (linhas do recorte, colunas do merge).

## Arquivos-chave

- `shared/log.py` (`RunLog`, `build_diagnostics`) e `ui/components/tool_layout.py`.
- `core/tools/merge.py` (`ColumnGroup`, `move_column`) e `ui/pages/merge.py`.
- `tests/test_log.py`, `test_integration.py` e `test_merge.py`.

## Armadilhas

- Flet 1.0 não suporta drop de arquivos do SO; o merge usa
  `Draggable`/`DragTarget` para o quadro de colunas.
- Uma aba contribui com no máximo uma coluna por saída; cabeçalhos repetidos
  ganham sufixo `_2`.
- `puremagic` lê HTML como `.txt`; `resolve_suffix` usa a extensão original.
- `.xls` é lido com o engine `calamine` (`python-calamine`); `xlrd` saiu.
- HTML sem `<meta charset>` pode perder acentos; as fixtures declaram UTF-8.
- `read_html` não aceita `dtype`; a segunda passada com converters é necessária.
- `merge` marca só a primeira aba por arquivo quando há vários.
- Log não pode carregar valores de célula; só passos, contagens e caminhos.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run pytest` ·
`node scripts/check-docs.mjs`
