# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** fechamento do ciclo 0004 (S5a–S5d)
- **Próxima:** S6a — tema claro opcional
  (`docs/sessions/S6a-tema-claro.md`) — spec pronta
- **Ciclo:** 0005 — Polimento, Fase 1
- **Decisões:** histórico de execuções descartado; tema claro aplicado só ao
  reabrir o app; ADR 0011 e ADR 0012 seguem valendo

## Pronto

- Ciclo 0004 fechado: execução fora da UI, log ao vivo/cancelamento, CNJ em
  texto sujo e recorte por quantidade de arquivos.
- S5d: recorte com “Linhas por arquivo” ou “Arquivos por aba”; a quantidade vale
  por aba e os blocos ficam equilibrados.
- S5c: CNJ em texto sujo com separadores flexíveis; CPF e 21 dígitos seguidos
  fora; dígito verificador inválido não descarta o valor.
- S5b: log ao vivo na fila; “Executar” vira “Cancelar” e a parada cooperativa
  entre arquivos mantém a prévia parcial sem liberar salvar.
- S4c/S4b: UI e `shared/` em PT-BR, leitura fiel de CSV/HTML, code tour.

## Próximo passo

Executar a S6a: tokenizar as cores, criar a paleta clara, salvar a preferência
local e aplicar o tema na abertura; a troca na sidebar pede reabertura.

## Arquivos-chave

- `ui/theme.py`, `app.py`, `ui/components/sidebar.py`
- `shared/progress.py`, `ui/components/tool_layout.py` (execução/cancelamento)
- `ui/components/result_panel.py`, `ui/pages/batch.py`, `ui/pages/*.py`
- `core/tools/cut.py`, `controllers/cut.py`, `ui/pages/cut.py`
- `core/tools/cnj.py` (sanitização e regex flexível)
- `tests/test_cut.py`, `tests/test_cnj.py`, `tests/test_integration.py`
- `docs/roadmap/0004-execucao-e-robustez.md` (histórico do ciclo fechado)

## Armadilhas

- Flet não é thread-safe: UI só no loop da página, via dispatcher e fila.
- A preferência de tema precisa ser lida antes de montar a UI; troca ao vivo
  está fora de escopo nesta fase.
- Componentes devem usar `theme.X`; import direto de constante ignora a paleta.
- Cancelar não interrompe pandas: só vale entre arquivos, nunca na chamada.
- Recorte por partes usa divisão equilibrada, limitada ao total de linhas.
- `rows_per_file` e `parts` não se misturam no controller.
- Sanear o texto na busca não altera a planilha nem o diagnóstico.
- `keep_default_na=False`: célula vazia vira `""`, não `NaN`; merge usa `pd.NA`.
- `.xls` não tem leitor alternativo; falha do calamine é final.
- Python 3.15 aceita `except A, B:` sem parênteses; não “corrigir”.
- Nunca `push --force` na `main`; `legacy` é somente leitura.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check
src tests` · `uv run pytest` · `node scripts/check-docs.mjs`
