# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S16 — Drive sem consentimento repetido (investigação)
- **Próxima:** S17 — ícone da sidebar e da janela
  (`docs/sessions/S17-icone-da-sidebar.md`)
- **Ciclo:** 0009 — Investigações de UI
- **Retorno:** `e7fa4ad` — docs: adapta ao padrao novo das skills de sessao
- **Decisões:** ADR 0026 — Picker JS no navegador com o token do login,
  `drive.file`, seletor do Drive em Flet descartado; demais nos ADRs 0014–0025.

## Pronto

- S16: spike do Picker JS em `127.0.0.1` com `setOAuthToken`; consentimento só
  no login, arquivo escolhido acessível ao token do login, `drive.file` lista 0
  itens sem Picker. ADR 0026; S24 reescrita para o Picker JS.
- S15: spike em Flet puro com 25.000 arquivos; ADR 0025 (com adendos).
- S14: área Plugins, carregamento sob demanda, CLI e guia do autor.
- S12: `v0.3.0`, build Windows e instalador.

## Próximo passo

Ler `docs/sessions/S17-icone-da-sidebar.md`: trocar o “x” de `Sidebar._logo`
por `assets/icon.png`, ícone da janela com `assets/icon.ico` e `assets/` no
build. Depois S18–S23 até a release 0.4.0; a S24 (Picker JS) fica no backlog.

## Arquivos-chave

- `src/xl_utils/ui/components/sidebar.py`, `src/xl_utils/app.py`, `assets/`
- `scripts/build_windows.ps1`, `docs/reference/ui.md` → Layout
- `docs/adr/0026-drive-sem-consentimento.md`, `docs/sessions/S24-*.md`
- `artifacts/spike_drive/` (ignorado; spike do Picker JS)

## Armadilhas

- `drive.file` só enxerga o que o app criou ou o Picker concedeu; listar o
  Drive com o token do login devolve 0 itens.
- Picker JS com token inválido mostra 403 e não chama o callback: precisa de
  tempo-limite.
- O build não embute o cliente OAuth nem a API key (backlog); no Linux o
  `drive_client.json` fica em `~/.xl_utils/` e o DPAPI não existe.
- Largura fixa de diálogo corta em 125% de escala; calcular a partir de
  `page.width` e testar 100/125/150%.
- Spikes e capturas ficam em `artifacts/`; nunca commitar.
- Abrir a área de plugins não importa `lib/`; só o primeiro Executar importa.
- Plugin em processo não tem sandbox; permissões são avisos.
- `.tar.xz` é tar + xz; sidecar SHA-256 obrigatório; nada de `extractall`.
- `flet pack` apaga `build/`; artefatos em `artifacts/`; o build exige
  `_lzma.pyd` e `python3t.dll` no bundle.
- `.iss` é UTF-8 com BOM; `Set-Content` corrompe acentos.
- Flet não é thread-safe: carregar e executar fora da UI thread.
- Ciclos fechados ficam em `docs/roadmap/`; não recriar `docs/history/`.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check src tests` · `uv run pytest` · `uv run python scripts/check_docs.py` · `uv run xl-utils-plugin --help` · `powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1`
