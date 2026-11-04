# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S1c — recorte de planilha
- **Próxima:** S1d — mesclagem (`docs/sessions/S1d-merge.md`)
- **Ciclo:** 0002 — Fase 1 — Migração dos scripts
- **Retorno:** `src/xl_utils/core/tools/cut.py` e `src/xl_utils/ui/pages/cut.py`

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

S1d: criar `core/tools/merge.py` com concatenação pura por arquivos ou abas
sobre `prepare_workbook`, controller salvando em `output/`, seletor de modo
ativo na página e remoção de `merge.py` da raiz.

## Decisões abertas

- Nenhuma bloqueante.

## Arquivos-chave

- `src/xl_utils/core/tools/all_str.py` — pipeline seguro e erro tipado.
- `src/xl_utils/core/tools/cnj.py` — regex, normalização e deduplicação.
- `src/xl_utils/core/tools/cut.py`, `controllers/cut.py` e `ui/pages/cut.py` — recorte e saída.
- `src/xl_utils/core/io.py` — leitura/escrita compartilhada.
- `docs/reference/architecture.md` — camadas e fluxo.

## Armadilhas

- Flet 1.0 não suporta drop de arquivos do SO; o dropzone é clicável.
- `puremagic` detecta HTML como `.txt`; `resolve_suffix` cai para a extensão
  original quando o detectado não é suportado.
- Não normalizar quebras de linha: o texto da célula deve ser preservado.
- `prepare_workbook` não converte tipos de `.html` para texto; revisar na S2a.

## Como rodar

```bash
uv sync
uv run xl-utils
uv run ruff check src tests
uv run pytest
node scripts/check-docs.mjs
```
