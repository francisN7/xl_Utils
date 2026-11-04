# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S5d — recorte por quantidade de arquivos
- **Próxima:** S6a — histórico de execuções
  (`docs/sessions/S6a-historico-de-execucoes.md`) — spec pronta
- **Ciclo:** 0004 — Execução e robustez, Fase 2 concluída; resta o backlog
- **Decisões:** ADR 0011 (execução/cancelamento); ADR 0012 (CNJ sujo, dígito
  verificador não validado)

## Pronto

- S5d: a página de recorte alterna entre “Linhas por arquivo” e “Arquivos por
  aba”; a quantidade vale por aba, os blocos ficam equilibrados e o modo antigo
  não mudou.
- Quantidade acima do total de linhas é reduzida para não criar arquivo vazio;
  aba vazia continua gerando um arquivo.
- S5c: CNJ em texto sujo com separadores flexíveis; CPF e 21 dígitos seguidos
  fora; dígito verificador inválido não descarta o valor.
- S5b: log ao vivo na fila; “Executar” vira “Cancelar” e a parada cooperativa
  entre arquivos mantém a prévia parcial sem liberar salvar.
- S5a: handler em `asyncio.to_thread`, barra e contador via fila, entrada
  bloqueada; UI atualizada só no loop.
- S4c/S4b: UI e `shared/` em PT-BR, leitura fiel de CSV/HTML, code tour.

## Próximo passo

Executar a S6a: registrar as últimas execuções (ferramenta, arquivos, contagens,
resultado e saída) em armazenamento local e exibi-las sem conteúdo de célula.

## Arquivos-chave

- `core/tools/cut.py`, `controllers/cut.py` (dois modos de recorte)
- `ui/pages/cut.py` (seletor de modo e campos)
- `core/tools/cnj.py` (sanitização e regex flexível)
- `shared/progress.py`, `ui/components/tool_layout.py` (execução e cancelamento)
- `ui/components/result_panel.py`, `ui/pages/batch.py`, `ui/pages/*.py`
- `tests/test_cut.py`, `tests/test_cnj.py`, `tests/test_integration.py`
- `docs/adr/0011-execucao-fora-da-ui.md`, `docs/adr/0012-cnj-texto-sujo.md`

## Armadilhas

- Flet não é thread-safe: UI só no loop da página, via dispatcher e fila.
- Cancelar não interrompe pandas: só vale entre arquivos, nunca na chamada.
- Recorte por partes usa divisão equilibrada, não `ceil`; a diferença máxima é
  uma linha e a quantidade é limitada ao total de linhas.
- `rows_per_file` e `parts` não se misturam no controller; um dos dois é exigido.
- Sanear o texto na busca não pode alterar a planilha nem o diagnóstico.
- `keep_default_na=False`: célula vazia vira `""`, não `NaN`; merge usa `pd.NA`.
- `.xls` não tem leitor alternativo; falha do calamine é final.
- Python 3.15 aceita `except A, B:` sem parênteses; não “corrigir”.
- Nunca `push --force` na `main`; `legacy` é somente leitura.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check
src tests` · `uv run pytest` · `node scripts/check-docs.mjs`
