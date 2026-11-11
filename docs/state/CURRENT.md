# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S13 — contrato de plugins e instalação `.tar.xz`
- **Próxima:** S14 — área Plugins, carregamento e guia prático
- **Ciclo:** 0008 — Plugins
- **Decisões:** plugins em `.tar.xz` com stdlib, `plugin.toml`, `run(request)`,
  mesmo processo, permissões declarativas e sidecar SHA-256 (ADR 0023);
  `flet pack` + Inno Setup (ADR 0021); demais regras nos ADRs 0014–0022.

## Pronto

- S13: ADR 0023; `core/plugins/` (manifesto e pacote); `shared/plugins/`
  (instalação atômica, descoberta e desinstalação); CLI
  `pack/check/install/list/uninstall`; contrato em `docs/plugins/`; 92 testes
  de plugins. Build 85,1 MB e app abriu.
- S12b: ciclos 0001–0007 em `docs/roadmap/`; ADR 0022 substitui a 0020.
- S12: `v0.3.0` publicada; build em `scripts/build_windows.ps1` e guia em
  `docs/guide/release-windows.md`.

## Próximo passo

Ler `docs/sessions/S14-plugins-ui.md`: área “Plugins”, instalar/remover pela
tela, carregamento isolado e guia prático com exemplos. Não há mudança no
formato `.tar.xz` nem no contrato da API 1.

## Arquivos-chave

- `src/xl_utils/core/plugins/`, `src/xl_utils/shared/plugins/api.py`
- `src/xl_utils/shared/plugins/install.py`, `scripts/plugin_cli.py`
- `docs/plugins/`, `docs/adr/0023-contrato-de-plugins.md`
- `docs/sessions/S14-plugins-ui.md`, `tests/test_plugin_*.py`

## Armadilhas

- Sidecar SHA-256 é obrigatório; hash é integridade, não autoria.
- `.tar.xz` é tar + xz; não usar `extractall` nem confiar no cabeçalho.
- Plugin em processo não tem sandbox; permissões são avisos.
- A promoção é atômica; staging fica no mesmo volume e id duplicado não
  sobrescreve.
- O PyInstaller só embute `shared/plugins` quando a S14 ligar a UI; validar
  `_lzma` no bundle daquela sessão.
- `flet pack` apaga `build/` e `--distpath`: artefatos em `artifacts/`.
- Sem `python3t.dll` de `abi3t-compat/`, o google-auth quebra no exe.
- `.iss` é UTF-8 com BOM; `Set-Content` do PowerShell corrompe acentos.
- Flet não é thread-safe: carregar/executar fora da UI thread.
- Ciclos fechados ficam em `docs/roadmap/`; não recriar `docs/history/`.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check src tests` · `uv run pytest` · `node scripts/check-docs.mjs` · `uv run python scripts/plugin_cli.py --help` · `powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1`
