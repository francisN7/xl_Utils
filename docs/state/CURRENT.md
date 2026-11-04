# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S4c — tradução de `ui/`/`shared/` e revisão do
  diagnóstico
- **Próxima:** S5a — execução fora da UI thread e barra de progresso
  (`docs/sessions/S5a-execucao-fora-da-ui.md`) — spec pronta
- **Ciclo:** 0004 — Execução e robustez, Fase 1
- **Decisões:** quatro sessões aprovadas; recorte por aba; CNJ sem validar
  dígito verificador

## Pronto

- Planejamento do ciclo 0004 e spec da S5a.
- CI corrigido: template de spec versionado; `docs:check` verde.
- S4c: `ui/`, `shared/`, shell e `__init__` em PT-BR; diagnóstico revisado.
- S4b: CSV/HTML fiéis, `.xlsm` equivalente a `.xlsx`, `.xls` sem falso reparo
  e code tour publicado.
- Ciclos 0002 e 0003 fechados; specs antigas fora do working tree.

## Próximo passo

Executar a S5a após confirmação: mover `_run` para segundo plano, reporter de
progresso por arquivo e barra no painel de resultado.

## Arquivos-chave

- `ui/components/tool_layout.py`, `ui/pages/*.py`
- `shared/progress.py` (novo), `shared/log.py`
- `docs/sessions/S5a-execucao-fora-da-ui.md`, `docs/roadmap/main.md`
- `tests/test_layout.py`, `tests/test_integration.py`

## Armadilhas

- Flet não é thread-safe: UI só no loop da página, via fila e `run_task`.
- `page.run_task` pode não existir em teste headless; manter caminho síncrono.
- `keep_default_na=False`: célula vazia vira `""`, não `NaN`; merge usa `pd.NA`.
- `.xls` não tem leitor alternativo; falha do calamine é final.
- Datas do Excel viram texto ISO, não o formato exibido.
- Python 3.15 aceita `except A, B:` sem parênteses; não “corrigir”.
- Nunca `push --force` na `main`; `legacy` é somente leitura.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run pytest` ·
`node scripts/check-docs.mjs`
