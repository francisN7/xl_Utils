# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S18 — Plugins no rodapé da sidebar
- **Próxima:** S19 — Remover Verificar Vínculos e preparar o repo de plugins
  (`docs/sessions/S19-remover-vinculos.md`)
- **Ciclo:** 0009 — Investigações de UI
- **Retorno:** `658af8f` — docs: amplia escopo da S22 para documentacao de onboarding
- **Decisões:** ADR 0026 — Picker JS no navegador com o token do login,
  `drive.file`, seletor do Drive em Flet descartado; demais nos ADRs 0014–0025.

## Pronto

- S18: Plugins é `FOOTER_PAGES` no rodapé da sidebar; `TOOLS` só tem as
  nativas; navegação por `id` (`HOME_ID = "home"`), `PAGES` junta tudo.
- S17: logo da sidebar é `assets/icon.png` (fallback “x”); ícone da janela
  `.ico` no Windows e `.png` no Linux via `ui/assets.py`; build leva
  `assets/`. Validação no Windows pendente (exe e instalador).
- S16: spike do Picker JS com `setOAuthToken` (ADR 0026); S24 no backlog.

## Próximo passo

Ler `docs/sessions/S19-remover-vinculos.md`: remover Verificar Vínculos de
`src/`, `tests/` e docs e criar o esqueleto de `xl_U-Plugins`. Depois S20–S23
até a release 0.4.0; a S24 (Picker JS) fica no backlog. Conferir o ícone no
build Windows na próxima vez que rodar `build_windows.ps1`.

## Arquivos-chave

- `src/xl_utils/ui/components/sidebar.py`, `src/xl_utils/app.py`
- `src/xl_utils/ui/pages/registry.py`, `src/xl_utils/ui/pages/home.py`
- `src/xl_utils/core/tools/link.py`, `controllers/link.py`, `ui/pages/link.py`
- `docs/reference/ui.md` → Layout/Início/Vinculação
- `docs/adr/0026-drive-sem-consentimento.md`, `docs/sessions/S24-*.md`

## Armadilhas

- Navegação por `id`; teste de todas as páginas usa `PAGES`, não `TOOLS`.
- `drive.file` só vê o que o app criou ou o Picker concedeu (listar dá 0).
- Picker JS com token inválido dá 403 sem callback: precisa de tempo-limite.
- O build não embute o cliente OAuth nem a API key (backlog); no Linux o
  `drive_client.json` fica em `~/.xl_utils/` e o DPAPI não existe.
- Diálogo de largura fixa corta em 125%: calcular por `page.width`.
- Spikes e capturas ficam em `artifacts/`; nunca commitar.
- `assets/` fica na raiz, fora do wheel: no exe só existe via `--add-data`.
  `ft.Image` recebe bytes para não depender do `assets_dir` do Flet.
- Abrir a área de plugins não importa `lib/`; só o primeiro Executar importa.
- Plugin em processo não tem sandbox; permissões são avisos.
- `.tar.xz` é tar + xz; sidecar SHA-256 obrigatório; nada de `extractall`.
- `flet pack` apaga `build/`; artefatos em `artifacts/`; o build exige
  `_lzma.pyd` e `python3t.dll` no bundle.
- `.iss` é UTF-8 com BOM; `Set-Content` corrompe acentos.
- Flet não é thread-safe: carregar e executar fora da UI thread.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check src tests` · `uv run pytest` · `uv run python scripts/check_docs.py` · `uv run xl-utils-plugin --help` · `powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1`
