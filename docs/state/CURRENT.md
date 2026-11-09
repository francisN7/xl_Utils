# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S12 — instalador 0.3.0 e release
- **Próxima:** S13 — plugins: contrato e extração segura
- **Ciclo:** 0008 — Plugins
- **Decisões:** `flet pack` + Inno Setup, por usuário, desinstalação destrutiva
  com cache Flet por fingerprint (ADR 0021); comparação bruta; CNJ máscara ou 20
  dígitos; `MIGRAÇÃO` é sentinela; config empacotada; ADRs 0014–0019; Drive:
  PKCE/`state`, `drive.file`, DPAPI, Picker desktop, pasta concedida e `_001`;
  histórico em texto (ADR 0020).

## Pronto

- S12: `v0.3.0` publicada — instalador 85,1 MB, SHA-256 `7c8dcb95…`, menu
  Iniciar, atalho opcional, ícone 2b (arte dupla 16–32/48–256 px), desinstalação
  que apaga `%LOCALAPPDATA%\xl_utils` e o cache do cliente em
  `%USERPROFILE%\.flet`. Build em `scripts/build_windows.ps1`; guia em
  `docs/guide/release-windows.md`; decisão no ADR 0021.
- S11: 0.2.0 no pyproject, lock, `__version__` e diagnóstico; cartões do Início e
  e-mail do menu de perfis sem estouro, com tooltip de 3 s.
- S10: ciclo 0006 arquivado; ciclo 0007 aberto. S9c: “Salvar no Drive” na pasta
  de origem, concessão por conta e nomes `_001`.

## Próximo passo

Ler `docs/sessions/S13-plugins-contrato.md`: ADR do contrato de plugins e
instalação segura do `.7z` em `%LOCALAPPDATA%/xl_utils/plugins/`.

## Arquivos-chave

- `docs/sessions/S13-plugins-contrato.md`, `docs/roadmap/main.md`
- `scripts/build_windows.ps1`, `installer/xl_utils.iss`, `scripts/make_icons.py`
- `scripts/pack_entry.py`, `assets/icon.*`, `docs/guide/release-windows.md`
- `pyproject.toml`, `src/xl_utils/shared/`

## Armadilhas

- `flet pack` apaga `build/` e o `--distpath`: artefatos sempre em `artifacts/`.
- Sem `python3t.dll` de `abi3t-compat/`, o google-auth quebra no exe.
- `flet-cli` 1.1.2: o build aplica o patch `open(..., "ab")`.
- `.iss` é UTF-8 **com BOM**; `Set-Content` do PowerShell corrompe acentos.
- Desinstalador acha o cache Flet pelo fingerprint do zip; não apagar `.flet`
  inteiro (outros apps Flet usam o mesmo `client`).
- `gh` fica em `C:\Program Files\GitHub CLI\gh.exe`, fora do PATH do shell.
- Flet não é thread-safe: login, Picker, gravação e execução fora da UI thread.
- `drive.file` só vê arquivo criado/escolhido; a pasta precisa ser concedida.
- Fechar o app não fecha o `flet.exe` do cliente; ele segura o cache.
- Sandbox: pasta mapeada é somente leitura e o build apaga `artifacts/installer`;
  compartilhar por `artifacts/share`.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check src tests` · `uv run pytest` · `node scripts/check-docs.mjs` · `powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1`
