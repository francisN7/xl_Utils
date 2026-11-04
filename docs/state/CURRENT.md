# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S1c — recorte de planilha
- **Próxima:** S1d — seleção de abas (`docs/sessions/S1d-sheet-selection.md`)
- **Ciclo:** 0002 — Fase 1 — Migração dos scripts
- **Retorno:** `src/xl_utils/ui/components/tool_layout.py` e `core/io.py`

## Pronto

- Ambiente uv no Python 3.15, Flet desktop, pandas 3.1, puremagic e emoji.
- Estrutura MVC híbrida, app navegável e tema Dracula.
- `prepare_workbook(path)` lê todas as abas com `dtype=str`, remove emojis e
  preserva quebras de linha; falha de leitura tenta reparo e pode levantar
  `WorkbookReadError`.
- Tratamento de Texto executa pela página e salva em `output/`.
- Extração de CNJs padroniza, deduplica, ordena e salva `PROCESSOS` em
  `output/<nome> lista cnj.xlsx`.
- Recorte divide cada aba em blocos de N linhas, salva em `output/` com nomes
  `_Recorte_NNN` e usa campo de linhas editável em `ToolState.options`.
- `all_str.py`, `cnjs.py` e `cut.py` removidos da raiz; resta `merge.py`.

## Próximo passo

S1d: seletor de abas com chips + “Todas”/“Limpar”, `list_sheets` e
`filter_sheets` no core, e filtro em `all_str`, `cnj` e `cut` preservando os
nomes das abas na saída.

## Decisões abertas

- S1e: merge em um único modo, coluna `ORIGEM` e alinhamento manual de colunas; ver ADR 0005.

## Arquivos-chave

- `src/xl_utils/core/io.py` — `list_sheets` e leitura/escrita.
- `src/xl_utils/ui/components/tool_layout.py` — integra o seletor.
- `src/xl_utils/ui/state.py` — abas por arquivo.
- `src/xl_utils/controllers/` — filtro em all_str, cnj e cut.

## Armadilhas

- Flet 1.0 não suporta drop de arquivos do SO; o dropzone é clicável.
- `puremagic` detecta HTML como `.txt`; `resolve_suffix` cai para a extensão
  original quando o detectado não é suportado.
- Não normalizar quebras de linha: o texto da célula deve ser preservado.
- `prepare_workbook` não converte tipos de `.html` para texto; revisar na S2a.
- Seleção vazia precisa de erro claro, não execução silenciosa.

## Como rodar

```bash
uv sync
uv run xl-utils
uv run ruff check src tests
uv run pytest
node scripts/check-docs.mjs
```
