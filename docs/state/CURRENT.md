# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S9c — Drive III: gravação na pasta e exportação
- **Próxima:** S10 — fechar o ciclo 0006 e revisar o backlog
- **Ciclo:** 0006 — Backlog
- **Decisões:** comparação bruta; CNJ máscara ou 20 dígitos; `MIGRAÇÃO` é
  sentinela; config empacotada; ADRs 0014–0019; plugins em `.7z` privado.
  Drive: PKCE/`state`, `drive.file`, DPAPI, Picker desktop sem API key, pasta
  concedida por conta, raiz como fallback e nomes livres `_001`.

## Pronto

- S9c: “Salvar no Drive” só com origem no Drive; `drive/folders.json` por
  conta, upload multipart, `.xlsx` em memória, `_001`, “Abrir no Drive” e
  fallback para a raiz. Teste real validado em 2026-11-08.
- S9b: Picker desktop, leitura/exportação, botão na entrada e `login_hint`.
- S9a: login por DPAPI, menu de perfis, site público e atalho global.

## Próximo passo

Ler `docs/sessions/S10-fechar-ciclo-0006.md`: arquivar o roadmap em
`0006-backlog.md`, tirar as specs fechadas do working tree, revisar o backlog
(responsividade, e-mail longo, seletor integrado, consentimento do Drive e
plugins) e abrir o ciclo 0007. Antes, validar no app abrir do Drive, salvar,
repetir e ver `_001`.

## Arquivos-chave

- `shared/drive.py`, `drive_pick.py`, `drive_cache.py`, `drive_store.py`,
  `drive_auth.py`, `accounts.py`
- `ui/drive.py`, `ui/components/result_panel.py`, `ui/components/tool_layout.py`
- `core/io.py` (`dump_workbook`), `core/paths.py` (`free_name`)
- `tests/test_drive_write.py`, `test_drive_api.py`, `test_drive_pick.py`,
  `test_drive_session.py`
- `scripts/check-drive-picker.py`, `docs/adr/0018-drive-autenticacao.md`
- `docs/sessions/S10-fechar-ciclo-0006.md`

## Armadilhas

- `drive.file` só vê arquivo criado/escolhido; a pasta precisa ser concedida.
- `drive.file` não lê `files/root` (404); origem na raiz grava sem `parents`.
- Picker de desktop não tem “somente pastas”: `mimetypes` + validação.
- `login_hint` não força a conta; 403/404 viram `FolderPermissionError`.
- Nunca sobrescrever: `free_name` escolhe `_001`; `files.update` fora do escopo.
- A listagem da pasta pode não ver arquivos antigos; nada é alterado.
- Planilha nativa não é editada no lugar; o resultado é um `.xlsx` novo.
- Flet não é thread-safe: login, Picker, gravação e execução fora da UI thread.
- Pages: push de código não publica; use Actions → Pages → Run workflow.
- Nunca `push --force` na `main`; `legacy` é somente leitura.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check src tests` · `uv run pytest` · `node scripts/check-docs.mjs`
