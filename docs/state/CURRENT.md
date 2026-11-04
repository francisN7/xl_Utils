# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S5c — extração de CNJ em texto sujo
- **Próxima:** S5d — recorte por quantidade de arquivos
  (`docs/sessions/S5d-recorte-por-arquivos.md`) — spec pronta
- **Ciclo:** 0004 — Execução e robustez, Fase 2
- **Decisões:** ADR 0011 (execução/cancelamento); ADR 0012 (CNJ sujo, dígito
  verificador não validado)

## Pronto

- S5c: a busca remove invisíveis, NBSP e travessões variantes de uma cópia do
  texto; aceita espaço, quebra, ponto, barra e hífen entre os blocos.
- CPF e sequência de 21 dígitos seguidos continuam fora; o dígito verificador
  não é validado e o CNJ inválido não é descartado.
- S5b: log ao vivo na fila; “Executar” vira “Cancelar” e a parada cooperativa
  entre arquivos mantém a prévia parcial sem liberar salvar.
- S5a: handler em `asyncio.to_thread`, barra e contador via fila, entrada
  bloqueada; UI atualizada só no loop.
- S4c/S4b: UI e `shared/` em PT-BR, leitura fiel de CSV/HTML, code tour.

## Próximo passo

Executar a S5d: alternar o recorte entre linhas por arquivo e quantidade de
arquivos, aplicando a quantidade **por aba** e preservando o nome de saída.

## Arquivos-chave

- `core/tools/cnj.py` (sanitização e regex flexível)
- `shared/progress.py`, `ui/components/tool_layout.py` (execução e cancelamento)
- `ui/components/result_panel.py`, `ui/pages/batch.py`, `ui/pages/*.py`
- `core/tools/cut.py`, `controllers/cut.py`, `ui/pages/cut.py`
- `tests/test_cnj.py`, `tests/test_progress.py`, `tests/test_layout.py`
- `docs/adr/0011-execucao-fora-da-ui.md`, `docs/adr/0012-cnj-texto-sujo.md`

## Armadilhas

- Flet não é thread-safe: UI só no loop da página, via dispatcher e fila.
- Cancelar não interrompe pandas: só vale entre arquivos, nunca na chamada.
- Merge é uma única chamada de controller; não há ponto de parada por origem.
- Sanear o texto na busca não pode alterar a planilha nem o diagnóstico.
- `keep_default_na=False`: célula vazia vira `""`, não `NaN`; merge usa `pd.NA`.
- `.xls` não tem leitor alternativo; falha do calamine é final.
- Python 3.15 aceita `except A, B:` sem parênteses; não “corrigir”.
- Nunca `push --force` na `main`; `legacy` é somente leitura.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check
src tests` · `uv run pytest` · `node scripts/check-docs.mjs`
