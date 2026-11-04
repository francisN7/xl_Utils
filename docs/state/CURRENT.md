# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S1b — extração de CNJ
- **Próxima:** S1c — recorte (`docs/sessions/S1c-cut.md`)
- **Ciclo:** 0002 — Fase 1 — Migração dos scripts
- **Retorno:** `src/xl_utils/core/tools/cnj.py` e `src/xl_utils/ui/pages/cnj.py`

## Pronto

- Ambiente uv no Python 3.15, Flet desktop, pandas 3.1, puremagic e emoji.
- Estrutura MVC híbrida, app navegável e tema Dracula.
- `prepare_workbook(path)` lê todas as abas com `dtype=str`, remove emojis e
  preserva quebras de linha; é o pipeline obrigatório das ferramentas.
- Falha de leitura tenta um reparo tolerante por formato e, se necessário,
  levanta `WorkbookReadError` — sem `shell=True` e sem `xlsx2csv`.
- Tratamento de Texto executa pela página e salva em `output/`.
- Extração de CNJs padroniza, deduplica, ordena e salva `PROCESSOS` em
  `output/<nome> lista cnj.xlsx`, com log de encontrados/duplicados.
- `all_str.py` e `cnjs.py` removidos da raiz; restam `cut.py` e `merge.py`.

## Próximo passo

S1c: criar `core/tools/cut.py` com recorte puro por quantidade de linhas sobre
`prepare_workbook`, controller salvando cada parte em `output/`, página com
campo de linhas ativo e remoção de `cut.py` da raiz.

## Decisões abertas

- Nenhuma bloqueante.

## Arquivos-chave

- `src/xl_utils/core/tools/all_str.py` — pipeline seguro e erro tipado.
- `src/xl_utils/core/tools/cnj.py` — regex, normalização e deduplicação.
- `src/xl_utils/controllers/cnj.py` e `ui/pages/cnj.py` — execução e página.
- `src/xl_utils/core/io.py` — leitura/escrita compartilhada.
- `docs/reference/architecture.md` — camadas e fluxo.

## Armadilhas

- Flet 1.0 não suporta drop de arquivos do SO; o dropzone é clicável.
- `puremagic` detecta HTML como `.txt`; `resolve_suffix` cai para a extensão
  original quando o detectado não é suportado.
- Não normalizar quebras de linha: o texto da célula deve ser preservado.
- `prepare_workbook` não converte tipos de `.html` para texto; revisar na S2a.
- Scripts legados restantes (`cut`, `merge`) não têm lint limpo.

## Como rodar

```bash
uv sync
uv run xl-utils
uv run ruff check src tests
uv run pytest
node scripts/check-docs.mjs
```
