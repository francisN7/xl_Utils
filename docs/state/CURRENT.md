# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S22a — Auditoria dos docs e documentação para quem chega
- **Próxima:** S22b — README e site com banner, badges e screenshots
  (`docs/sessions/S22b-readme-e-site.md`)
- **Ciclo:** 0009 — Investigações de UI
- **Retorno:** `25fce82` — S21d: merge acima do limite em varios arquivos
- **Decisões:** ADR 0031 (perfil local), 0030 (chaveiro), 0029 (painel de
  perfis), 0028 (API 2), 0027 (vinculação), 0026 (Picker JS) e 0015–0025.

## Pronto

- S22a: docs auditados; `guide/onboarding.md`, `reference/glossary.md`,
  `CONTRIBUTING.md`; diagramas e **Mapa dos módulos** em `architecture.md`.
- S21d: aba >1.000.000 linhas vira arquivos `_parte1`, `_parte2`… (`split_item`).
- S21b: foto (Pillow, PNG 256 px) e apelido (≤16) em `drive/profiles/`.

## Próximo passo

Executar a S22b (banner, badges, screenshots dos dois temas no README e no
site). O dono confere no desktop: foto real, login real e painel no Linux.
Depois S23 (0.4.0, build Windows com Pillow); S24 e versão Linux no backlog.

## Arquivos-chave

- `src/xl_utils/ui/components/{top_menu,account_label,account_settings}.py`
- `src/xl_utils/shared/{accounts,profiles}.py`, `ui/drive.py`
- Plugins: `shared/plugins/{api,reader}.py`, `docs/plugins/api.md`

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
- Spikes em `artifacts/`, nunca commitados; `spike_s21b/panel.py` (8552) usa
  contas e foto falsas em raiz temporária, mas o tema grava a preferência real.
- Diálogo de largura fixa corta em 125%: calcular por `page.width`.
- `assets/` fica na raiz, fora do wheel; `ft.Image` recebe bytes.
- Plugins: `check` recebe o `.tar.xz`; só o primeiro Executar importa `lib/`;
  sem sandbox; sidecar SHA-256; nada de `extractall`.
- `flet pack` apaga `build/`; exige `_lzma.pyd` e `python3t.dll`; `.iss` é
  UTF-8 com BOM. Flet não é thread-safe: trabalho pesado fora da UI thread.

## Como rodar

`uv run xl-utils` (`--web`) · `uv run ruff check src tests` · `uv run ruff format --check src tests` · `uv run pytest` · `uv run python scripts/check_docs.py` · `uv run xl-utils-plugin --help` · `powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1`
