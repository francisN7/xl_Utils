# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S3b — `legacy` travada no GitHub
- **Próxima:** S4a — fechar ciclo 0002 e abrir a Fase 4
  (`docs/sessions/S4a-fechar-ciclo.md`)
- **Ciclo:** 0002 — Fase 3 — Publicação (concluída)
- **Decisões abertas:** item que abre a Fase 4 (S4a)

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
- `main` é a versão com UI e a branch padrão (`feat/ui` removida); `legacy`
  parte de `68ce5e0`, só acrescenta o aviso e é citada no README da `main`.
- Tag `legacy-v1` e rulesets ativos (branch `26547015`, tag `26547017`)
  bloqueiam push, force-push e exclusão, sem bypass.

## Próximo passo

S4a: revisar o backlog com o dono, fechar o ciclo 0002, criar o roadmap da
Fase 4 e a spec da primeira sessão.

## Arquivos-chave

- `README.md`, `docs/adr/0009-publicacao-main-legacy.md` e
  `docs/sessions/S4a-fechar-ciclo.md`.
- Saída: `core/save.py`, `ui/components/result_panel.py`,
  `ui/components/tool_layout.py` e `tests/test_save.py`.

## Armadilhas

- Nunca `push --force` na `main` nem recriar `feat/ui`; a `legacy` é somente
  leitura e o GitHub não tem selo nativo de branch.
- Flet 1.0 não suporta drop do SO; merge usa `Draggable`/`DragTarget`.
- `FilePicker` fica em `page.services`; salvar/cancelar é assíncrono e `None`.
- Cabeçalhos repetidos ganham sufixo `_2`; uma aba dá no máximo uma coluna por
  saída.
- `puremagic` pode dar `.txt`; a extensão suportada vence e o gate só bloqueia
  sem formato suportado. `.xls` usa `calamine`; `read_html` não aceita `dtype`.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run pytest` ·
`node scripts/check-docs.mjs`
