# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S1d — seleção de abas
- **Próxima:** S1e — merge (`docs/sessions/S1e-merge.md`)
- **Ciclo:** 0002 — Fase 1 — Migração dos scripts
- **Retorno:** `ui/components/sheet_selector.py` e `core/tools/sheets.py`

## Pronto

- Ambiente uv/Python 3.15, Flet desktop e pandas 3.1; MVC híbrido e tema Dracula.
- `prepare_workbook` lê tudo como texto, remove emojis, preserva quebras e tenta
  reparo; falha vira `WorkbookReadError`.
- Texto, CNJ e recorte prontos e salvando em `output/`; aceitam lote e processam
  cada origem separadamente. CNJ sai como `PROCESSOS`; recorte usa `_Recorte_NNN`.
- `list_sheets` lista abas pelo tipo real; `filter_sheets` aplica a seleção e
  `default_selection` marca todas no lote e a primeira de cada no merge.
- Seletor de chips com “Todas”/“Limpar”, contador e spinner; tipografia mínima
  de 12 px em toda a UI.
- As duas colunas rolam sem barra visível; log de até 160 px e prévia de 240 px
  com rolagem nos dois eixos. Seleção vazia bloqueia o lote.
- `all_str.py`, `cnjs.py` e `cut.py` removidos da raiz; resta `merge.py`.

## Próximo passo

S1e: migrar `merge` para um único modo — concatenar as abas selecionadas de
todos os arquivos na ordem, com coluna `ORIGEM` e alinhamento de colunas;
apagar `merge.py` e criar core + controller + página com testes.

## Decisões abertas

- S1e: alinhamento por dropdown (Flet 1.0 não tem drag); confirmar. ADR 0005.

## Arquivos-chave

- `core/io.py` (`list_sheets`) e `core/tools/sheets.py` (`filter_sheets`).
- `sheet_selector.py`, `state.py` e `tool_layout.py` — chips e layout.

## Armadilhas

- Flet 1.0 não suporta drop de arquivos do SO; o dropzone é clicável.
- `puremagic` lê HTML como `.txt`; `resolve_suffix` usa a extensão original.
- Quebras de linha são preservadas; `prepare_workbook` ainda não ajusta `.html`.
- `list_sheets` em HTML lê tudo em thread; erro de listagem reporta a falha.
- `cut` usa o nome da aba no arquivo só com mais de uma aba processada.

## Como rodar

```bash
uv run xl-utils
uv run ruff check src tests
uv run pytest
node scripts/check-docs.mjs
```
