# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S9b — Picker do Drive, leitura e botão na entrada
- **Próxima:** S9c — gravação na pasta e exportação
- **Ciclo:** 0006 — Backlog
- **Decisões:** comparação bruta; CNJ máscara ou 20 dígitos; `MIGRAÇÃO` é
  sentinela; config empacotada; ADRs 0014–0019; plugins em `.7z` privado; `id`,
  `link` e “vinculação” continuam. Drive: PKCE/`state`, `drive.file`, DPAPI,
  Picker de desktop sem API key e segunda autorização sem offline.

## Pronto

- S9b: Picker de desktop (`drive_pick.py`), cliente REST (`drive.py`), cache
  local (`drive_cache.py`), botão do Drive na entrada e escolha de conta.
  Acabamento: vínculos voltou a abrir; botão 44 px no topo; `login_hint`.
- S9a6: atalho global reinstalado; janela não é reposicionada; Flet 1.1.2.
- S9a4/S9a5: segredo do cliente por DPAPI; e-mail canônico no login.
- S9a3: site no GitHub Pages; publicação por workflow desde a S9b.

## Próximo passo

Ler `docs/sessions/S9c-drive-escrita.md`. A primeira decisão é como gravar na
pasta de origem: `drive.file` concede arquivo por arquivo, então a pasta precisa
ser escolhida uma vez (`allow_folder_selection=true`) ou o resultado cai na raiz
do Meu Drive. O Picker foi validado com conta real em 2026-11-08.

## Arquivos-chave

- `shared/drive.py`, `drive_pick.py`, `drive_cache.py`, `drive_auth.py`
- `shared/accounts.py`, `ui/drive.py`, `ui/components/file_input.py`
- `ui/components/tool_layout.py`, `ui/pages/registry.py`, `app.py`
- `tests/test_drive_api.py`, `test_drive_pick.py`, `test_drive_session.py`
- `scripts/check-drive-login.py`, `check-drive-picker.py`
- `docs/adr/0018-drive-autenticacao.md`, `docs/sessions/S9c-drive-escrita.md`

## Armadilhas

- `drive.file` só vê arquivo criado pelo app ou escolhido no Picker.
- A pasta do arquivo escolhido **não** vem concedida; gravar nela dá 403.
- Picker: só `drive.file`, sem `offline`, e consentimento a cada escolha.
- Planilha nativa precisa de `files.export` (`.xlsx`); limite de 10 MB.
- **Google Picker API** precisa estar ativa no projeto, além da Drive API.
- Sem cliente, o 1º **Entrar com Google** pede o JSON uma vez; depois não pede.
- Login não é ferramenta: não recriar cartão do Drive no hub.
- DPAPI é Windows-only; fora dele o store recusa gravar.
- Comparação bruta: CNJ mascarado × 20 dígitos não vincula; coluna em texto.
- `PROCESSO ORIGINÁRIO` contém “PROCESSO”; o match é exato, nunca substring.
- `MIGRAÇÃO` na AGENDA dispara o pop-up; confirmar não reescreve.
- AGENDA sem PROCESSOS bloqueia tudo; só CLIENTES não valida CNJ.
- Flet não é thread-safe: login, Picker e execução fora da UI thread.
- Pages: push de código não publica; use Actions → Pages → Run workflow.
- Nunca `push --force` na `main`; `legacy` é somente leitura.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check src tests` · `uv run pytest` · `node scripts/check-docs.mjs`
