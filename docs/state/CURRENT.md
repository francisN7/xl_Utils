# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S5b — log ao vivo e cancelamento cooperativo
- **Próxima:** S5c — extração de CNJ em texto sujo
  (`docs/sessions/S5c-cnj-texto-sujo.md`) — spec pronta
- **Ciclo:** 0004 — Execução e robustez, Fase 2
- **Decisões:** ADR 0011 com adendo de S5b (log na fila, token cooperativo)

## Pronto

- S5b: a fila transporta linhas de log; cada arquivo aparece no painel assim que
  termina. “Executar” vira “Cancelar” durante a execução.
- Cancelamento entre arquivos: a chamada em curso termina, a prévia parcial fica
  em memória e “Execução cancelada” não libera salvar nem grava nada.
- `CancelToken` em `shared/progress.py` entregue ao handler como 4º parâmetro;
  merge só cancela antes de começar (etapa única).
- S5a: handler em `asyncio.to_thread`, barra e contador via fila, entrada
  bloqueada; UI atualizada só no loop.
- S4c/S4b: UI e `shared/` em PT-BR, leitura fiel de CSV/HTML, code tour.

## Próximo passo

Executar a S5c: extrair CNJ de texto sujo com normalização de espaços, quebras,
travessões e invisíveis, aceitando separadores flexíveis e mantendo a rejeição a
CPF e números maiores.

## Arquivos-chave

- `shared/progress.py` (`CancelToken`, evento `log`)
- `ui/components/tool_layout.py` (fila, botão Cancelar, token)
- `ui/components/result_panel.py` (`apply_progress`, `set_cancelled`)
- `ui/pages/batch.py` (`report_cancelled`), `ui/pages/*.py`
- `tests/test_progress.py`, `tests/test_layout.py`, `tests/test_integration.py`
- `docs/adr/0011-execucao-fora-da-ui.md`

## Armadilhas

- Flet não é thread-safe: UI só no loop da página, via dispatcher e fila.
- `page.run_task` pode não existir em teste headless; manter o caminho síncrono.
- Cancelar não interrompe pandas: só vale entre arquivos, nunca no meio da chamada.
- Merge é uma única chamada de controller; não há ponto de parada por origem.
- `keep_default_na=False`: célula vazia vira `""`, não `NaN`; merge usa `pd.NA`.
- `.xls` não tem leitor alternativo; falha do calamine é final.
- Python 3.15 aceita `except A, B:` sem parênteses; não “corrigir”.
- Nunca `push --force` na `main`; `legacy` é somente leitura.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check
src tests` · `uv run pytest` · `node scripts/check-docs.mjs`
