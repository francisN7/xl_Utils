# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S19 — Remover Verificar Vínculos e preparar o repo de
  plugins
- **Próxima:** S20 — Leitura de planilhas pelo host e API 2 dos plugins
  (`docs/sessions/S20-api-2-leitor.md`)
- **Ciclo:** 0009 — Investigações de UI
- **Retorno:** `4be82ef` — docs: commit so local, push fica com o dono
- **Decisões:** ADR 0027 (vinculação vira plugin), 0026 (Picker JS) e 0015–0025.

## Pronto

- S19: quatro ferramentas nativas; vinculação, `headers.json`,
  `shared/configs.py` e o `pre_run` do `ToolLayout` removidos. Código guardado
  em `../xl_U-Plugins/link/referencia/` (repo privado, S01 de lá fechada).
- S18: Plugins é `FOOTER_PAGES` no rodapé; navegação por `id`.
- S17: ícone real na sidebar e na janela; validação no Windows pendente.

## Próximo passo

Executar a S20 (`reader` na API 2, sem compatibilidade com a 1) e depois
atualizar o `_molde/` do `xl_U-Plugins`. Em seguida S21–S23 até a 0.4.0; S24
(Picker JS) no backlog. Conferir o ícone no build Windows na próxima vez que
rodar `build_windows.ps1`.

## Arquivos-chave

- `src/xl_utils/shared/plugins/api.py`, `controllers/plugins.py`
- `src/xl_utils/core/plugins/manifest.py`, `core/tools/all_str.py`
- `src/xl_utils/ui/components/tool_layout.py`, `ui/pages/registry.py`
- `docs/plugins/api.md`, `docs/adr/0023-contrato-de-plugins.md`
- `../xl_U-Plugins/AGENTS.md`, `../xl_U-Plugins/link/README.md`

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
- Plugin em processo não tem sandbox; permissões são avisos.
- `.tar.xz` é tar + xz; sidecar SHA-256 obrigatório; nada de `extractall`.
- `flet pack` apaga `build/`; o build exige `_lzma.pyd` e `python3t.dll`.
- `.iss` é UTF-8 com BOM; `Set-Content` corrompe acentos.
- Flet não é thread-safe: carregar e executar fora da UI thread.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check src tests` · `uv run pytest` · `uv run python scripts/check_docs.py` · `uv run xl-utils-plugin --help` · `powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1`
