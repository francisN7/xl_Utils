# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S14 — área Plugins, carregamento sob demanda e guia
- **Próxima:** S15 — seletor de arquivos integrado à UI (investigação)
- **Ciclo:** 0009 — Investigações de UI
- **Decisões:** import do plugin só na primeira execução, pacote sintético e
  cache (ADR 0024); `.tar.xz`, mesmo processo e permissões declarativas (ADR
  0023); demais nos ADRs 0014–0022.

## Pronto

- S14: área Plugins (válidos/inválidos, instalar com confirmação, remover,
  abrir pasta), carregamento sob demanda sem tocar no `sys.path`, página
  declarativa com os quatro tipos de opção, slots nomeados, log, progresso e
  cancelamento; CLI como `xl-utils-plugin`; guia e exemplos executáveis. 595
  testes, docs ok, build com `_lzma` e exe abrindo.
- S13: ADR 0023; `core/plugins/` e `shared/plugins/`; instalação atômica e CLI.
- S12: `v0.3.0`, build Windows e instalador.

## Próximo passo

Ler `docs/sessions/S15-seletor-de-arquivos.md`: medir o seletor próprio com
spike descartável e decidir no ADR 0025, sem mudar o fluxo padrão. A release
0.4.0 está no backlog; o dono decide quando empacotar.

## Arquivos-chave

- `src/xl_utils/ui/pages/plugins.py`, `plugin_tool.py`
- `src/xl_utils/shared/plugins/loader.py`, `controllers/plugins.py`
- `src/xl_utils/core/plugins/page.py`
- `src/xl_utils/plugin_cli.py`, `docs/plugins/`
- `docs/adr/0024-carregamento-sob-demanda.md`
- `tests/test_plugin_loader.py`, `test_plugins_ui.py`, `test_plugin_examples.py`

## Armadilhas

- Abrir a área não importa `lib/`; só o primeiro Executar importa e o cache só
  cai ao instalar/remover.
- Imports entre arquivos do plugin são relativos; `sys.path` nunca muda.
- Plugin em processo não tem sandbox; permissões são avisos.
- Falha de import aparece no Executar, não na lista (lista = manifesto).
- `.tar.xz` é tar + xz; sidecar SHA-256 obrigatório; nada de `extractall`.
- `flet pack` apaga `build/`; artefatos em `artifacts/`; o build exige
  `_lzma.pyd` no bundle.
- Sem `python3t.dll` de `abi3t-compat/`, o google-auth quebra no exe.
- `.iss` é UTF-8 com BOM; `Set-Content` corrompe acentos.
- Flet não é thread-safe: carregar e executar fora da UI thread.
- Ciclos fechados ficam em `docs/roadmap/`; não recriar `docs/history/`.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check src tests` · `uv run pytest` · `node scripts/check-docs.mjs` · `uv run xl-utils-plugin --help` · `powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1`
