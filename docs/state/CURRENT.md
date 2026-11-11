# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S15 — seletor de arquivos (investigação)
- **Próxima:** S16 — Drive sem consentimento repetido (investigação)
- **Ciclo:** 0009 — Investigações de UI
- **Decisões:** ADR 0025 — seletor em Flet puro, paginado (300), listagem fora
  da UI thread, nativo/Picker como fallback; demais nos ADRs 0014–0024.

## Pronto

- S15: spike em Flet puro com 25.000 arquivos, filtro por formato, busca,
  recentes, subpasta e seleção; nenhum fluxo padrão mudou. ADR 0025 com as
  medições e a spec de implementação em `docs/sessions/S24-seletor-em-flet.md`.
- S14: área Plugins (válidos/inválidos, instalar, remover, abrir pasta),
  carregamento sob demanda, página declarativa, CLI e guia do autor. 595 testes.
- S13: ADR 0023; `core/plugins/` e `shared/plugins/`; instalação atômica e CLI.
- S12: `v0.3.0`, build Windows e instalador.

## Próximo passo

Ler `docs/sessions/S16-drive-sem-consentimento.md`: inventariar o fluxo atual
(`drive.file` + Picker + concessão de pasta) e medir um spike de listagem com o
token do login, sem trocar escopo. A decisão vira ADR 0026. O seletor próprio
(S24) fica para depois da 0.4.0; a release é a S23.

## Arquivos-chave

- `docs/adr/0025-seletor-de-arquivos.md`, `docs/sessions/S16-*.md`
- `docs/reference/ui.md` → Entrada de arquivos
- `src/xl_utils/shared/drive.py`, `drive_auth.py`, `drive_pick.py`,
  `drive_store.py`, `ui/drive.py`, `ui/components/file_input.py`
- `artifacts/spike_selector/` (ignorado; spike descartável e captura local)

## Armadilhas

- Flet não virtualiza a lista no processo Python: 5.000 `ListTile` custam
  ~10 MB e ~500 ms; paginar em 300 e listar em `asyncio.to_thread`.
- `os.scandir` é ~2,7× mais rápido que `Path.iterdir` + `is_dir` (46 ms vs
  125 ms em 10.000 itens); usar `DirEntry.is_dir`.
- Largura fixa de diálogo corta em 125% de escala; calcular a partir de
  `page.width` e testar 100/125/150%.
- O spike tem caminho pessoal na captura; não commitar `artifacts/`.
- Abrir a área de plugins não importa `lib/`; só o primeiro Executar importa.
- Plugin em processo não tem sandbox; permissões são avisos.
- `.tar.xz` é tar + xz; sidecar SHA-256 obrigatório; nada de `extractall`.
- `flet pack` apaga `build/`; artefatos em `artifacts/`; o build exige
  `_lzma.pyd` e `python3t.dll` no bundle.
- `.iss` é UTF-8 com BOM; `Set-Content` corrompe acentos.
- Flet não é thread-safe: carregar e executar fora da UI thread.
- Ciclos fechados ficam em `docs/roadmap/`; não recriar `docs/history/`.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check src tests` · `uv run pytest` · `node scripts/check-docs.mjs` · `uv run xl-utils-plugin --help` · `powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1`
