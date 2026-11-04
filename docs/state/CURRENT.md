# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S4c — tradução de `ui/`/`shared/` e revisão do
  diagnóstico
- **Próxima:** nenhuma definida; aguardando feedback do dono sobre o backlog em
  `docs/roadmap/main.md`
- **Ciclo:** 0003 fechado em `docs/roadmap/0003-qualidade.md`; nenhum ciclo ativo
- **Decisões abertas:** qual item do backlog vira a próxima sessão, quando
  houver um novo ciclo

## Pronto

- `ui/`, `shared/`, shell (`app.py`) e `__init__` com docstrings e comentários
  em PT-BR; identificadores seguem em inglês.
- `build_diagnostics` revisado: versões, caminho do arquivo, abas por nome,
  formato, opções, resultado, erro, causa e traceback limitado a 4.000
  caracteres; nenhum conteúdo de célula entra no texto.
- `AGENTS.md` sem o backlog de tradução; `reference/architecture.md` corrigido
  para a composição real de `shared/`.
- S4b anterior: CSV/HTML fiéis, `.xlsm` equivalente a `.xlsx`, `.xls` sem falso
  reparo, core/controllers em PT-BR e code tour publicado.
- Ciclo 0002 em `docs/roadmap/0002-migracao.md`; specs de fases fechadas fora do
  working tree.

## Próximo passo

Sem sessão agendada e sem ciclo ativo. Quando houver feedback, escolher o novo
ciclo, um item do backlog e escrever a spec antes de codar.

## Arquivos-chave

- `src/xl_utils/ui/` e `src/xl_utils/shared/log.py`, `system.py`
- `docs/reference/architecture.md`, `docs/guide/code-tour.md`
- `docs/roadmap/0003-qualidade.md`, `docs/roadmap/main.md`
- `tests/test_log.py`, `tests/test_layout.py`, `tests/test_ui_state.py`

## Armadilhas

- `keep_default_na=False`: célula vazia vira `""`, não `NaN`; o merge ainda
  preenche lacunas com `pd.NA`.
- `csv.Sniffer` pode errar em arquivo atípico; o fallback usa `sep=None` com
  engine Python.
- `.xls` não tem leitor alternativo; a falha do calamine é final.
- Datas do Excel viram texto ISO, não o formato exibido.
- Flet 1.0 não suporta drop do SO; merge usa `Draggable`/`DragTarget`.
- Python 3.15 aceita `except A, B:` sem parênteses; não “corrigir” para sintaxe
  antiga.
- Nunca `push --force` na `main`; `legacy` é somente leitura.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run pytest` ·
`node scripts/check-docs.mjs`
