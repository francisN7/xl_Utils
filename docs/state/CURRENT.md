# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S20 — Leitura de planilhas pelo host e API 2 dos
  plugins
- **Próxima:** S21 — Menu de perfis do Drive sem troca de conta
  (`docs/sessions/S21-perfis-do-drive.md`)
- **Ciclo:** 0009 — Investigações de UI
- **Retorno:** `7fd9cc8` — chore: tira .claude do repo
- **Decisões:** ADR 0028 (API 2, `reader`), 0027 (vinculação vira plugin),
  0026 (Picker JS) e 0015–0025.

## Pronto

- S20: `request.reader.read(path)` lê pelo `prepare_workbook` só as abas
  marcadas (`all_sheets=True` traz todas); API 1 inválida com motivo;
  exemplos 2.0.0; `_molde` do `xl_U-Plugins` na API 2 (commit local lá).
- Pós-S19: `uv run xl-utils --web` abre a mesma UI na porta 8550.
- S19: quatro ferramentas nativas; vinculação guardada em
  `../xl_U-Plugins/link/referencia/`, volta como plugin na S02 de lá.

## Próximo passo

Executar a S21 (abre com questionário: conta do "Abrir do Drive"). Depois
S22–S23 até a 0.4.0; S24 (Picker JS) no backlog. Teste real de plugin é
gatilho (plugin de Vínculo). Conferir o ícone no build Windows.

## Arquivos-chave

- `src/xl_utils/ui/components/top_menu.py`, `src/xl_utils/ui/drive.py`
- `src/xl_utils/shared/accounts.py`, `docs/adr/0026-drive-sem-consentimento.md`
- Plugins: `shared/plugins/{api,reader}.py`, `docs/plugins/api.md`

## Armadilhas

- Navegação por `id`; teste de todas as páginas usa `PAGES`, não `TOOLS`.
- `configs/` só tem o modelo `drive_client.json` (campos vazios); o build
  ainda leva a pasta com `--add-data`.
- `xl-utils-plugin check` recebe o `.tar.xz`, não a pasta.
- `drive.file` só vê o que o app criou ou o Picker concedeu (listar dá 0).
- Picker JS com token inválido dá 403 sem callback: precisa de tempo-limite.
- O build não embute o cliente OAuth nem a API key (backlog); no Linux o
  `drive_client.json` fica em `~/.xl_utils/` e o DPAPI não existe.
- Diálogo de largura fixa corta em 125%: calcular por `page.width`.
- Spikes e capturas ficam em `artifacts/`; nunca commitar.
- `assets/` fica na raiz, fora do wheel; `ft.Image` recebe bytes.
- Abrir a área de plugins não importa `lib/`; só o primeiro Executar importa.
- `RunLog()` vazio é falsy: use `is None`, não `log or RunLog()`.
- Plugin em processo não tem sandbox; permissões são avisos.
- `.tar.xz` é tar + xz; sidecar SHA-256 obrigatório; nada de `extractall`.
- `flet pack` apaga `build/`; o build exige `_lzma.pyd` e `python3t.dll`.
- `.iss` é UTF-8 com BOM; `Set-Content` corrompe acentos.
- Flet não é thread-safe: carregar e executar fora da UI thread.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check src tests` · `uv run pytest` · `uv run python scripts/check_docs.py` · `uv run xl-utils-plugin --help` · `powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1`
