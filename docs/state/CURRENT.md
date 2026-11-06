# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S6b — progresso e log por estágio; depois, curadoria do
  backlog (Drive e vinculação)
- **Próxima:** S6c — tema claro opcional
  (`docs/sessions/S6c-tema-claro.md`) — spec pronta
- **Ciclo:** 0005 — Polimento, Fase 2
- **Decisões:** tema claro ao reabrir; histórico descartado; ADRs 0005 e 0011 atualizados

## Pronto

- S6b: as quatro ferramentas emitem etapas no log ao vivo (leitura, planilha
  carregada, cálculo); a barra fica indeterminada durante cada arquivo e avança
  ao concluí-lo. O loop cede entre eventos para a tela renderizar.
- S6a: `ORIGEM` = `<stem> - <aba>` e `LINHA_ORIGEM` numera o resultado inteiro
  com zeros à esquerda; colunas de mesmo nome viram `_original`.
- S5d: recorte com “Linhas por arquivo” ou “Arquivos por aba”, quantidade por
  aba e blocos equilibrados.
- S5c: CNJ em texto sujo; dígito verificador inválido não descarta o valor.

## Próximo passo

Executar a S6c: tokenizar as cores, criar a paleta clara, salvar a preferência
local e aplicar o tema na abertura; a troca na sidebar pede reabertura.

## Arquivos-chave

- `ui/theme.py`, `app.py`, `ui/components/sidebar.py`
- `shared/progress.py`, `controllers/*.py` (etapas)
- `ui/components/result_panel.py`, `ui/components/tool_layout.py`
- `core/tools/merge.py` (`ORIGEM`/`LINHA_ORIGEM`)
- `core/tools/cut.py`, `controllers/cut.py`, `ui/pages/cut.py`
- `tests/test_merge.py`, `tests/test_progress.py`, `tests/test_layout.py`
- `docs/adr/0005-selecao-de-abas-e-merge.md`,
  `docs/adr/0011-execucao-fora-da-ui.md`

## Armadilhas

- Flet não é thread-safe: UI só no loop da página; o `apply_progress` atualiza
  direto porque já roda no loop.
- Sem `await asyncio.sleep(0)` entre eventos, lotes rápidos acumulam tudo no fim.
- A preferência de tema precisa ser lida antes de montar a UI; troca ao vivo
  está fora de escopo nesta fase.
- Cancelar não interrompe pandas: só vale entre arquivos.
- `LINHA_ORIGEM` usa a largura do total do resultado, não de cada aba/arquivo.
- `ORIGEM`/`LINHA_ORIGEM` são reservados: coluna de origem vira `_original`.
- Recorte por partes usa divisão equilibrada, limitada ao total de linhas.
- `keep_default_na=False`: célula vazia vira `""`, não `NaN`; merge usa `pd.NA`.
- `.xls` não tem leitor alternativo; falha do calamine é final.
- Python 3.15 aceita `except A, B:` sem parênteses; não “corrigir”.
- Nunca `push --force` na `main`; `legacy` é somente leitura.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check
src tests` · `uv run pytest` · `node scripts/check-docs.mjs`
