# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S1d — seleção de abas
- **Próxima:** S1e — merge (`docs/sessions/S1e-merge.md`)
- **Ciclo:** 0002 — Fase 1 — Migração dos scripts
- **Retorno:** `ui/components/sheet_selector.py` e `core/tools/sheets.py`

## Pronto

- Ambiente uv no Python 3.15, Flet desktop, pandas 3.1; MVC híbrido, app
  navegável e tema Dracula.
- `prepare_workbook(path)` lê tudo com `dtype=str`, remove emojis e preserva
  quebras de linha; falha de leitura tenta reparo e pode levantar
  `WorkbookReadError`.
- Texto, CNJ e recorte prontos e salvando em `output/`; a lista de CNJs sai como
  `PROCESSOS` em `<nome> lista cnj.xlsx` e o recorte usa `_Recorte_NNN`.
- `list_sheets` lista abas pelo tipo real; `filter_sheets` aplica a seleção e
  `default_selection` marca todas (1 arquivo) ou a primeira de cada (vários).
- Seletor de chips no card “1. Entrada” com “Todas”/“Limpar” e contador; a
  seleção vive em `ToolState` e recarrega quando a lista de arquivos muda.
- `all_str`, `cnj` e `cut` filtram as abas escolhidas; seleção vazia não executa.
- `all_str.py`, `cnjs.py` e `cut.py` removidos da raiz; resta `merge.py`.

## Próximo passo

S1e: migrar `merge` para um único modo — concatenar as abas selecionadas de
todos os arquivos na ordem, com coluna `ORIGEM` e alinhamento de colunas;
apagar `merge.py` e criar core + controller + página com testes.

## Decisões abertas

- S1e: alinhamento por dropdown (Flet 1.0 não tem drag); confirmar. ADR 0005.

## Arquivos-chave

- `core/io.py` (`list_sheets`) e `core/tools/sheets.py` (`filter_sheets`).
- `sheet_selector.py`, `state.py` e `tool_layout.py` — chips e seleção.

## Armadilhas

- Flet 1.0 não suporta drop de arquivos do SO; o dropzone é clicável.
- `puremagic` detecta HTML como `.txt`; `resolve_suffix` cai para a extensão
  original quando o detectado não é suportado.
- Quebras de linha são preservadas; `prepare_workbook` ainda não ajusta `.html`.
- `list_sheets` em HTML lê o arquivo inteiro em thread; erro de listagem fica
  fora de `selected_sheets` e a execução reporta a falha de leitura.
- `cut` usa o nome da aba no arquivo só com mais de uma aba processada.

## Como rodar

```bash
uv run xl-utils
uv run ruff check src tests
uv run pytest
node scripts/check-docs.mjs
```
