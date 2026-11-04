# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S4b — revisão fiel do core, comentários e code tour
- **Próxima:** S4c — tradução de `ui/` e `shared/` e revisão do diagnóstico
  (`docs/sessions/S4c-traducao-ui.md`) — proposta; confirmar com o dono
- **Ciclo:** 0003 — Qualidade e clareza — Fase 4
- **Decisões abertas:** confirmar S4c; prioridade do backlog

## Pronto

- CSV com `;`, tab e `|`: encoding e separador detectados; `NA`/`N/A`/`NULL`
  preservados como texto; HTML com `colspan` mantém zeros e achata o cabeçalho.
- `.xlsm` não é mais divergência; `.xls` falha com mensagem de “sem leitor
  alternativo”; `read_headers` de CSV lê amostra.
- `save_chosen` recusa arquivo no lote; `save_workbook` normaliza `.xlsx`;
  `safe_file_part` e `summarize_cnjs` vivem no core.
- Core e controllers com docstrings/comentários em PT-BR; `AGENTS.md`
  atualizado.
- `docs/guide/code-tour.md`, “Mapa do core” em `architecture.md`, ADR 0010 e o
  comando global em `setup.md`/`README.md`.
- Ciclo 0002 fechado em `docs/roadmap/0002-migracao.md`; `main.md` ativo é o
  ciclo 0003.

## Próximo passo

S4c: traduzir docstrings/comentários de `ui/` e `shared/`, revisar a cópia do
diagnóstico e atualizar o code tour se algum módulo mudar.

## Arquivos-chave

- `src/xl_utils/core/io.py`, `mime.py`, `tools/all_str.py`
- `docs/guide/code-tour.md`, `docs/reference/architecture.md`,
  `docs/adr/0010-leitura-fiel-csv-html.md`
- `tests/test_formats.py`, `tests/test_format_check.py`

## Armadilhas

- `keep_default_na=False`: célula vazia vira `""`, não `NaN`; o merge ainda
  preenche lacunas com `pd.NA`.
- `csv.Sniffer` pode errar em arquivo atípico; o fallback usa `sep=None` com
  engine Python.
- `.xls` não tem leitor alternativo; a falha do calamine é final.
- Datas do Excel viram texto ISO, não o formato exibido.
- Flet 1.0 não suporta drop do SO; merge usa `Draggable`/`DragTarget`.
- Nunca `push --force` na `main`; `legacy` é somente leitura.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run pytest` ·
`node scripts/check-docs.mjs`
