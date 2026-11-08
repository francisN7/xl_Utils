# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S9a1 — Drive I.1 (login testável e importação do cliente)
- **Próxima:** S9b — Drive II (link, seletor e escrita)
- **Ciclo:** 0006 — Backlog
- **Decisões:** comparação bruta; CNJ máscara ou 20 dígitos; `MIGRAÇÃO` é
  sentinela; config empacotada; ADRs 0014–0018; plugins em `.7z` privado (ADR
  pendente); `id`, `link` e “vinculação” continuam. Drive: `google-auth-oauthlib`
  1.5 com PKCE/`state`, `drive.file`, contas com DPAPI, cliente importado, saída adiada.

## Pronto

- S9a1: JSON do cliente OAuth importado e validado (64 KB, UTF-8, HTTPS em
  domínio do Google); login bloqueado sem cliente; teste offline com Google
  falso (PKCE, `state`, negação, timeout) e script para o consentimento real.
- S9a: ADR 0018, login, contas com DPAPI, menu e cartão. S8: tela cheia;
  S7d/S7c/S7a/S7b: vinculação completa.

## Próximo passo

Ler `docs/sessions/S9b-drive-planilha.md`. O navegador já tem teste offline; o
consentimento real fica com `scripts/check-drive-login.py`. A primeira decisão
da S9b é como chegar ao arquivo: `drive.file` não lê planilha antiga por link;
escolher Google Picker ou escopo `drive` em Testing antes de qualquer código.

## Arquivos-chave

- `shared/drive_auth.py`, `shared/accounts.py`, `ui/drive.py`
- `ui/components/client_import.py`, `top_menu.py`, `drive_status.py`, `app.py`
- `tests/test_drive_flow.py`, `scripts/check-drive-login.py`
- `configs/drive_client.json`, `configs/headers.json`, `shared/configs.py`
- `core/tools/link.py`, `ui/components/tool_layout.py`, `ui/theme.py`
- `docs/adr/0018-drive-autenticacao.md`, `docs/sessions/S9b-drive-planilha.md`

## Armadilhas

- `drive.file` só vê arquivo criado pelo app ou escolhido no Picker.
- Sem cliente importado o login é bloqueado; o card oferece **Configurar**.
- O JSON importado é validado; `token_uri` fora do Google é recusado.
- DPAPI é Windows-only; fora dele o store recusa gravar.
- Token e client secret nunca em log, diagnóstico ou `repr`.
- `drive_client.json` empacotado nasce vazio; teste impede credencial real.
- Timeout do login é 180 s; negar no navegador vira erro tratado.
- Sair apaga só a conta ativa; trocar exige ferramenta ociosa.
- Comparação bruta: CNJ mascarado × 20 dígitos crus não vincula.
- CNJ numérico no Excel perde precisão; a coluna deve ser texto.
- `PROCESSO ORIGINÁRIO` contém “PROCESSO”; o match é exato, nunca substring.
- `MIGRAÇÃO` na AGENDA dispara o pop-up; confirmar não reescreve.
- AGENDA sem PROCESSOS bloqueia tudo; só CLIENTES não valida CNJ.
- Flet não é thread-safe: login e execução rodam fora da UI thread.
- Plugins: `.7z` precisa recusar path traversal, symlink e zip bomb.
- Nunca `push --force` na `main`; `legacy` é somente leitura.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check src tests` · `uv run pytest` · `node scripts/check-docs.mjs`
