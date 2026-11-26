# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S23c — Release 0.4.0 (fecha o ciclo 0009)
- **Próxima:** S24 — Picker JS do Drive (`docs/sessions/S24-seletor-do-drive.md`)
- **Ciclo:** 0010 — Drive e ajuda no app (0009 em `docs/roadmap/0009-investigacoes-de-ui.md`)
- **Retorno:** `5060dc2` — S23b: encerra a sessão (roadmap, CURRENT e spec)
- **Decisões:** ADRs 0015–0032 (adendos: 0019 S22b, 0021 S23b; 0032: AppImage).

## Pronto

- S23c: `v0.4.0` publicada (Latest) com instalador, AppImage e `SHA256SUMS.txt`.
- S23b: `release.yml` manual (`confirmar=build`) gera instalador e AppImage com smoke test.

## Próximo passo

Abrir o ciclo 0010 com `uv lock --upgrade` (Manutenção do roadmap; subir o
Flet exige conferir o patch do `flet-cli`) e executar a S24.

## Arquivos-chave

- Versão: `pyproject.toml`, `src/xl_utils/__init__.py`, `installer/xl_utils.iss`
- Release: `.github/workflows/release.yml`, `scripts/build_{windows.ps1,linux.sh}`, `packaging/linux/`, `docs/guide/release-{windows,linux}.md`
- Contas: `shared/{accounts,profiles}.py`, `ui/components/{top_menu,account_settings}.py`

## Armadilhas

- `PopupMenuItem` (Flet 1.1.2) não tem submenu: painel é `MenuBar`; o
  `MenuStyle` escapa do `theme.restyle`, a troca de tema chama `refresh()`.
- `SubmenuButton` não tem `close()`: botão dentro do painel que abre diálogo
  é `MenuItemButton`; no `--web` o diálogo chega cerca de 1 s depois.
- Cabeçalhos reservam `theme.TOP_MENU_RESERVE`; nome/apelido no topo ≤16;
  `account_for` sem a conta de origem dá `None`; fakes de sessão têm `profile_for`.
- `drive.file` só vê o que o app criou ou o Picker concedeu; Picker JS com
  token inválido dá 403 sem callback (precisa de tempo-limite).
- No Linux tudo fica em `~/.xl_utils/`; o token vai para o chaveiro e os
  testes nunca o tocam (`conftest` troca `KeyringVault` por um em memória).
- `check_docs.py` exige todo `src/xl_utils/**/*.py` citado pelo caminho em
  `architecture.md` → **Mapa dos módulos** ou no code tour.
- Spikes em `artifacts/`, nunca commitados (`spike_s22b/shots.py`: capturas).
- Imagens do README e do site ficam em `docs/assets/`; mudar algo lá republica
  o Pages (adendo S22b da ADR 0019). `check_docs` não confere `srcset`.
- Diálogo de largura fixa corta em 125%: calcular por `page.width`.
- `assets/` fica na raiz, fora do wheel; `ft.Image` recebe bytes.
- Plugins: `check` recebe o `.tar.xz`; só o primeiro Executar importa `lib/`;
  sem sandbox; sidecar SHA-256; nada de `extractall`.
- `flet pack` apaga `build/`; exige `_lzma.pyd` e `python3t.dll`; `.iss` é
  UTF-8 com BOM. Flet não é thread-safe: trabalho pesado fora da UI thread.
- AppImage: piso glibc 2.39; janela é `com.appveyor.flet` (Flet ignora
  `FLET_APP_ID`); sem `--web` no executável; teste limpo via Podman + X11
  (`--ipc=host`, `XAUTHORITY`). Print do desktop só da janela do app.
- Build usa as versões do `uv.lock` (subir o Flet: conferir o patch do
  `flet-cli`); `.ps1` com BOM, senão o PowerShell 5.1 lê como ANSI.

## Como rodar

`uv run xl-utils` (`--web`) · `uv run ruff check src tests` · `uv run ruff format --check src tests` · `uv run pytest` · `uv run python scripts/check_docs.py` · `uv run xl-utils-plugin --help` · `powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1` · `bash scripts/build_linux.sh`
