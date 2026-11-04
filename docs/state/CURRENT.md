# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S5a — execução fora da UI thread e barra de progresso
- **Próxima:** S5b — log ao vivo e cancelamento
  (`docs/sessions/S5b-log-ao-vivo-e-cancelamento.md`) — spec pronta
- **Ciclo:** 0004 — Execução e robustez, Fase 1
- **Decisões:** ADR 0011 (thread → Flet); merge reporta uma etapa

## Pronto

- S5a: handler roda em `asyncio.to_thread`; eventos de
  `shared/progress.py` chegam por fila ao loop e atualizam barra e contador.
- Entrada, chips de abas e “Executar” ficam bloqueados durante a execução.
- `ResultPanel`/`PreviewTable` só chamam `update` no loop; caminho síncrono
  preservado para testes headless.
- `tests/test_progress.py` cobre contagem e falha de callback; teste de layout
  confirma que o handler sai da thread da UI.
- S4c: tradução de `ui/`/`shared/` e revisão do diagnóstico.
- S4b: CSV/HTML fiéis, `.xlsm` equivalente a `.xlsx` e code tour publicado.

## Próximo passo

Executar a S5b: exibir eventos do log conforme são produzidos e permitir
cancelar entre arquivos/abas/células, sem gravar nada.

## Arquivos-chave

- `shared/progress.py`, `ui/components/tool_layout.py`
- `ui/components/result_panel.py`, `ui/components/preview_table.py`
- `ui/pages/*.py`, `docs/adr/0011-execucao-fora-da-ui.md`
- `tests/test_progress.py`, `tests/test_layout.py`, `tests/test_integration.py`

## Armadilhas

- Flet não é thread-safe: UI só no loop da página, via dispatcher e fila.
- `page.run_task` pode não existir em teste headless; manter o caminho síncrono.
- Merge é uma única chamada de controller; a contagem por origem exigiria mudar
  a regra.
- `keep_default_na=False`: célula vazia vira `""`, não `NaN`; merge usa `pd.NA`.
- `.xls` não tem leitor alternativo; falha do calamine é final.
- Python 3.15 aceita `except A, B:` sem parênteses; não “corrigir”.
- Nunca `push --force` na `main`; `legacy` é somente leitura.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check
src tests` · `uv run pytest` · `node scripts/check-docs.mjs`
