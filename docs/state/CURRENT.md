# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S1a — pipeline do `all_str`
- **Próxima:** S1b — extração de CNJ (`docs/sessions/S1b-cnj.md`)
- **Ciclo:** 0002 — Fase 1 — Migração dos scripts
- **Retorno:** `src/xl_utils/core/tools/all_str.py` e `src/xl_utils/ui/pages/all_str.py`

## Pronto

- Ambiente uv no Python 3.15, Flet desktop, pandas 3.1, puremagic e emoji.
- Estrutura MVC híbrida, app navegável e tema Dracula.
- `prepare_workbook(path)` lê todas as abas com `dtype=str`, remove emojis e
  preserva quebras de linha; é o pipeline obrigatório das ferramentas.
- Falha de leitura tenta um reparo tolerante por formato e, se necessário,
  levanta `WorkbookReadError` — sem `shell=True` e sem `xlsx2csv`.
- Tratamento de Texto executa pela página, salva em `output/` ao lado da
  planilha e mostra caminho, log e prévia.
- `all_str.py` da raiz removido; restam `cnjs.py`, `cut.py` e `merge.py`.

## Próximo passo

S1b: criar `core/tools/cnj.py` com regex pura (20 dígitos ou formato CNJ),
padronização, deduplicação e extração por todas as colunas, sempre sobre
`prepare_workbook`; conectar a página e apagar `cnjs.py` da raiz.

## Decisões abertas

- Saída do CNJ: uma aba `PROCESSOS` em `output/<nome> lista cnj.xlsx` ou um
  painel apenas em memória. Decidir na S1b.

## Arquivos-chave

- `src/xl_utils/core/tools/all_str.py` — pipeline seguro e erro tipado.
- `src/xl_utils/controllers/all_str.py` — execução, saída e log.
- `src/xl_utils/ui/pages/all_str.py` — página e opções fixas.
- `src/xl_utils/core/io.py` — leitura/escrita compartilhada.
- `docs/reference/architecture.md` — camadas e fluxo.

## Armadilhas

- Flet 1.0 não suporta drop de arquivos do SO; o dropzone é clicável.
- `puremagic` detecta HTML como `.txt`; `resolve_suffix` cai para a extensão
  original quando o detectado não é suportado.
- Não normalizar quebras de linha: o texto da célula deve ser preservado.
- `prepare_workbook` não converte tipos de `.html` para texto; revisar na S2a.
- Scripts legados restantes (`cnjs`, `cut`, `merge`) não têm lint limpo.

## Como rodar

```bash
uv sync
uv run xl-utils
uv run ruff check src tests
uv run pytest
node scripts/check-docs.mjs
```
