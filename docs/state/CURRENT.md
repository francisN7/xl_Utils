# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S21c — Login do Drive no Linux (chaveiro); antes, S21a
- **Próxima:** S21b — Engrenagem da conta: foto e apelido
  (`docs/sessions/S21b-config-da-conta.md`)
- **Ciclo:** 0009 — Investigações de UI
- **Retorno:** `d0982d5` — S21a: painel de perfis do Drive
- **Decisões:** ADR 0030 (token no chaveiro), 0029 (painel de perfis), 0028
  (API 2), 0027 (vinculação vira plugin), 0026 (Picker JS) e 0015–0025.

## Pronto

- S21c: fora do Windows o token vai para o chaveiro (`KeyringVault`).
- S21a: avatar + nome da conta selecionada no topo; painel `MenuBar` +
  `SubmenuButton` com “Outras contas” retrátil, “Adicionar conta” e “Sair”;
  “Abrir do Drive” sem diálogo; salvar só na conta de origem, com aviso.
- S20: `request.reader.read(path)` lê pelo `prepare_workbook` só as abas
  marcadas; API 1 inválida com motivo; `_molde` do `xl_U-Plugins` na API 2.

## Próximo passo

Executar a S21b (abre com questionário: diálogo ou página, foto). O dono
confere login real e painel no Linux. Depois S22–S23 até a 0.4.0; S24 (Picker
JS) e versão Linux no backlog; o próximo ciclo planeja Windows e Linux.

## Arquivos-chave

- `src/xl_utils/ui/components/{top_menu,account_label}.py`, `ui/drive.py`
- `src/xl_utils/shared/accounts.py`, `docs/adr/0029-painel-de-perfis-do-drive.md`
- Plugins: `shared/plugins/{api,reader}.py`, `docs/plugins/api.md`

## Armadilhas

- `PopupMenuItem` (Flet 1.1.2) não tem submenu: painel é `MenuBar`; o
  `MenuStyle` escapa do `theme.restyle`, a troca de tema chama `refresh()`.
- Cabeçalhos reservam `theme.TOP_MENU_RESERVE`; nome no topo ≤16 caracteres.
- `account_for` nunca cai na conta selecionada: sem a de origem, `None`.
- Navegação por `id`; teste de todas as páginas usa `PAGES`, não `TOOLS`.
- `configs/` só tem o modelo `drive_client.json`; o build leva a pasta.
- `drive.file` só vê o que o app criou ou o Picker concedeu (listar dá 0).
- Picker JS com token inválido dá 403 sem callback: precisa de tempo-limite.
- No Linux tudo fica em `~/.xl_utils/`; o token vai para o chaveiro e os
  testes nunca o tocam (`conftest` troca `KeyringVault` por um em memória).
- Spikes em `artifacts/`, nunca commitados; `spike_s21a/panel.py` roda o app
  com contas falsas na 8551, mas trocar o tema lá grava a preferência real.
- Diálogo de largura fixa corta em 125%: calcular por `page.width`.
- `assets/` fica na raiz, fora do wheel; `ft.Image` recebe bytes.
- Plugins: `check` recebe o `.tar.xz`; só o primeiro Executar importa `lib/`;
  sem sandbox; sidecar SHA-256; nada de `extractall`.
- `RunLog()` vazio é falsy: use `is None`, não `log or RunLog()`.
- `flet pack` apaga `build/`; exige `_lzma.pyd` e `python3t.dll`; `.iss` é
  UTF-8 com BOM. Flet não é thread-safe: trabalho pesado fora da UI thread.

## Como rodar

`uv run xl-utils` (`--web`) · `uv run ruff check src tests` · `uv run ruff format --check src tests` · `uv run pytest` · `uv run python scripts/check_docs.py` · `uv run xl-utils-plugin --help` · `powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1`
