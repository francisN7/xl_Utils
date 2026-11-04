# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S0b — UI base (Dracula, sidebar, Início e componentes)
- **Próxima:** S1a — `all_str` (`docs/sessions/S1a-all-str.md`)
- **Ciclo:** Fase 1 — Migração dos scripts
- **Retorno:** `src/xl_utils/core/io.py` e `src/xl_utils/ui/components/`

## Pronto

- Ambiente uv no Python 3.15, Flet desktop, pandas 3.1, puremagic e emoji.
- Estrutura MVC híbrida e app desktop navegável.
- Tema Dracula, sidebar de 240 px, Início com 4 cartões alinhados à esquerda.
- Entrada clicável, resultado com caminho/log/prévia de 100 linhas e ação.
- Estado por ferramenta preservado; trocar o arquivo reseta opções e resultado.
- Escopo de 4 ferramentas: `all_str`, `cnj`, `cut`, `merge`.
- `convert`, `quick_replace` e `remove_emoji` removidos da raiz.
- Documentação, ADRs, screenshots, roadmap, `docs:check` e CI.

## Próximo passo

S1a: criar `core/tools/all_str.py` com o pipeline `prepare_workbook` (leitura
`dtype=str` + remoção de emojis, preservando quebras de linha), reparo sem
`xlsx2csv`/`shell=True`, página de Tratamento de Texto, testes e remoção de
`all_str.py` da raiz.

## Decisões abertas

- Onde fica o pipeline: `core/tools/all_str.py` exporta `prepare_workbook` ou
  `core/io.py` chama o módulo. Decidir na S1a.
- Estratégia de reparo de xlsx corrompido: `openpyxl` read-only ou erro tipado.

## Arquivos-chave

- `src/xl_utils/app.py` — shell e navegação.
- `src/xl_utils/ui/components/` — sidebar, entrada, resultado, prévia e layout.
- `src/xl_utils/core/io.py` — leitura/escrita compartilhada.
- `docs/reference/ui.md` — layout, componentes e tema.

## Armadilhas

- Flet 1.0 não suporta drop de arquivos do SO; o dropzone é clicável.
- `puremagic` detecta HTML como `.txt`; `resolve_suffix` cai para a extensão
  original quando o detectado não é suportado.
- Não normalizar quebras de linha: o texto da célula deve ser preservado.
- Scripts legados restantes (`all_str`, `cnjs`, `cut`, `merge`) ainda não têm
  lint limpo; saem nas sessões de migração.

## Como rodar

```bash
uv sync
uv run xl-utils
uv run ruff check src tests
uv run pytest
node scripts/check-docs.mjs
```
