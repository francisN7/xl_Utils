# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S22b — README e site com banner, badges e screenshots
- **Próxima:** S23 — Release 0.4.0 e fechamento do ciclo
  (`docs/sessions/S23-release-0-4-0.md`)
- **Ciclo:** 0009 — Investigações de UI
- **Retorno:** `800b326` — S22a: encerra a sessão (roadmap, CURRENT e spec)
- **Decisões:** ADRs 0015–0031 (0019 com adendo S22b: imagens no Pages).

## Pronto

- S22b: banner animado, badges e capturas dos dois temas no README e no site.
- S22a: docs auditados; `guide/onboarding.md`, `reference/glossary.md`,
  `CONTRIBUTING.md`; diagramas e **Mapa dos módulos** em `architecture.md`.

## Próximo passo

Executar a S23 (0.4.0, build Windows com Pillow, Sandbox, release, fechar o
ciclo 0009). Com o dono: push, conferir README/site no GitHub (temas, badges,
deploy do Pages), foto e login reais. S24 e versão Linux no backlog.

## Arquivos-chave

- Versão: `pyproject.toml`, `src/xl_utils/__init__.py`, `installer/xl_utils.iss`
- Release: `scripts/build_windows.ps1`, `docs/guide/release-windows.md`
- Contas: `shared/{accounts,profiles}.py`, `ui/components/{top_menu,account_settings}.py`

## Armadilhas

- `PopupMenuItem` (Flet 1.1.2) não tem submenu: painel é `MenuBar`; o
  `MenuStyle` escapa do `theme.restyle`, a troca de tema chama `refresh()`.
- `SubmenuButton` não tem `close()`: botão dentro do painel que abre diálogo
  é `MenuItemButton`; no `--web` o diálogo chega cerca de 1 s depois.
- Cabeçalhos reservam `theme.TOP_MENU_RESERVE`; nome/apelido no topo ≤16.
- `account_for` nunca cai na conta selecionada: sem a de origem, `None`.
- Fakes de sessão em `test_drive_write`/`test_file_input_drive` têm `profile_for`.
- `drive.file` só vê o que o app criou ou o Picker concedeu (listar dá 0).
- Picker JS com token inválido dá 403 sem callback: precisa de tempo-limite.
- No Linux tudo fica em `~/.xl_utils/`; o token vai para o chaveiro e os
  testes nunca o tocam (`conftest` troca `KeyringVault` por um em memória).
- `check_docs.py` exige todo `src/xl_utils/**/*.py` citado pelo caminho em
  `architecture.md` → **Mapa dos módulos** ou no code tour.
- Spikes em `artifacts/`, nunca commitados; `spike_s22b/shots.py` (`ft.Screenshot`,
  `LOCALAPPDATA` temporário) só captura com a aba renderizando.
- Imagens do README e do site ficam em `docs/assets/`; mudar algo lá republica
  o Pages (adendo S22b da ADR 0019). `check_docs` não confere `srcset`.
- Diálogo de largura fixa corta em 125%: calcular por `page.width`.
- `assets/` fica na raiz, fora do wheel; `ft.Image` recebe bytes.
- Plugins: `check` recebe o `.tar.xz`; só o primeiro Executar importa `lib/`;
  sem sandbox; sidecar SHA-256; nada de `extractall`.
- `flet pack` apaga `build/`; exige `_lzma.pyd` e `python3t.dll`; `.iss` é
  UTF-8 com BOM. Flet não é thread-safe: trabalho pesado fora da UI thread.

## Como rodar

`uv run xl-utils` (`--web`) · `uv run ruff check src tests` · `uv run ruff format --check src tests` · `uv run pytest` · `uv run python scripts/check_docs.py` · `uv run xl-utils-plugin --help` · `powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1`
