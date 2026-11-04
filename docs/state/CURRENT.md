# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S3a — publicação (`main` com UI, `legacy` histórica)
- **Próxima:** S3b — sinalizar a `legacy` no GitHub
  (`docs/sessions/S3b-legacy-github.md`)
- **Ciclo:** 0002 — Fase 3 — Publicação
- **Decisões abertas:** tag e proteção da `legacy` (S3b)

## Pronto

- uv/Python 3.15, Flet desktop, pandas 3.1 e tema Dracula; `prepare_workbook`
  lê como texto, remove emojis, repara e falha como `WorkbookReadError`.
- Texto, CNJ, recorte e merge devolvem `SaveItem` em memória; nada é gravado
  até a escolha. `core/save.py` grava arquivo, lote ou atalho `output/`, com
  `unique_path` e `SaveError`.
- Painel “Pronto para salvar” com prévia, **Salvar**, **Salvar em output/**,
  cancelamento sem efeito e “Abrir pasta” depois de gravar.
- Abas por chips e `default_selection`; merge com `ORIGEM` e colunas
  arrastáveis. Integração cobre `.xlsx`, `.xls` (fixture), `.csv` e `.html`.
- `RunLog` e diagnóstico com arquivos, formato, abas, opções, causa e
  traceback; `ToolLayout._run` separa leitura, seleção e falha.
- `FormatCheck` mostra o tipo real, avisa divergência e bloqueia quando nada é
  identificável; texto e CNJ usam `note`, e “2. Opções” só aparece quando há o
  que editar.
- `main` é a versão com UI (fast-forward de `feat/ui`) e a branch padrão;
  `feat/ui` foi removida local e remotamente.
- `legacy` parte de `68ce5e0` e só acrescenta o aviso de descontinuação; o
  README da `main` aponta para ela.

## Próximo passo

S3b: criar a tag `legacy-v1`, aplicar ruleset/proteção na `legacy` e registrar o
aviso no README/desenvolvimento.

## Arquivos-chave

- `README.md`, `docs/adr/0009-publicacao-main-legacy.md` e
  `docs/sessions/S3b-legacy-github.md`.
- Saída: `core/save.py`, `ui/components/result_panel.py`,
  `ui/components/tool_layout.py` e `tests/test_save.py`.

## Armadilhas

- Nunca `push --force` na `main` (fast-forward) nem recriar `feat/ui`; o GitHub
  não tem selo de “legacy”, então restam nome, tag, README e ruleset.
- Flet 1.0 não suporta drop do SO; merge usa `Draggable`/`DragTarget`.
- `FilePicker` fica em `page.services`; salvar/cancelar é assíncrono e `None`.
- Cabeçalhos repetidos ganham sufixo `_2`; uma aba dá no máximo uma coluna por
  saída.
- `puremagic` pode dar `.txt`; a extensão suportada vence e o gate só bloqueia
  sem formato suportado. `.xls` usa `calamine`; `read_html` não aceita `dtype`.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run pytest` ·
`node scripts/check-docs.mjs`
