# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S6c — tema claro opcional; ciclo 0005 fechado
- **Próxima:** escolher um item do backlog (vinculação, alinhamento em tela
  cheia ou Drive) e escrever a spec antes de codar
- **Ciclo:** 0006 — Backlog
- **Decisões:** tema trocado ao vivo via `theme.restyle`; settings em
  `%LOCALAPPDATA%/xl_utils/settings.json`; ADR 0013

## Pronto

- S6c: `DARK`/`LIGHT` em `ui/theme.py`, `theme.apply(mode)` antes de montar a
  UI e botão na sidebar grava e aplica na hora via `theme.restyle`, sem perder
  o estado; settings ausente/corrompido cai no escuro. Contraste AA coberto.
- S6b: log por etapa e barra indeterminada por arquivo nas quatro ferramentas.
- S6a: `ORIGEM` = `<stem> - <aba>` e `LINHA_ORIGEM` no resultado inteiro.

## Próximo passo

Escolher o item do backlog com o dono e criar `docs/sessions/S7a-*.md` a partir
do `_TEMPLATE.md`; nenhuma spec existe ainda.

## Arquivos-chave

- `ui/theme.py`, `shared/settings.py`, `app.py`, `ui/components/sidebar.py`
- `tests/test_theme.py`, `tests/test_settings.py`
- `docs/reference/ui.md`, `docs/adr/0013-tema-claro-e-preferencia.md`
- `shared/progress.py`, `controllers/*.py` (etapas)
- `core/tools/merge.py` (`ORIGEM`/`LINHA_ORIGEM`)

## Armadilhas

- Tokens mudam com `theme.apply`; componente novo deve ler `theme.X` na
  montagem, nunca `from ...theme import TEXT`.
- `theme.restyle` só toca campos de cor; não percorrer `value`/`data`, senão
  um log com hex seria alterado. Controles são mutados no lugar, mas `Border`,
  `BorderSide`, `TextStyle`, `ButtonStyle` e `Gradient` são recriados inteiros:
  mutar `BorderSide` ao vivo faz o `Container` perder o `border_radius`.
- `settings.json` guarda só preferência, nunca caminho de planilha.
- Flet não é thread-safe: UI só no loop da página.
- Sem `await asyncio.sleep(0)` entre eventos, lotes rápidos acumulam no fim.
- Cancelar não interrompe pandas: só vale entre arquivos.
- `LINHA_ORIGEM` usa a largura do total do resultado.
- `.xls` não tem leitor alternativo; falha do calamine é final.
- Nunca `push --force` na `main`; `legacy` é somente leitura.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check
src tests` · `uv run pytest` · `node scripts/check-docs.mjs`
