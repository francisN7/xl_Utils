# S9a1 — Login testável e importação do cliente OAuth

## Objetivo

Fechar a pendência da S9a: o login do Drive precisa de teste automático (ou
semi-automático, com intervenção do dono) e o dono não pode ser obrigado a
editar o JSON do cliente OAuth à mão.

## Fora de escopo

- Ler ou gravar planilhas no Drive (S9b).
- Exportar nas demais ferramentas (S9c).
- Publicar um cliente OAuth no repositório público.

## Decisões

- **Importação pelo app:** o JSON baixado do Google Cloud Console entra por um
  seletor nativo (menu hamburger ou cartão do hub) e é validado antes de
  gravar. Nada de editar arquivo.
- **Validação:** no máximo 64 KB, UTF-8, objeto JSON, `client_id` no alfabeto
  do Google, `auth_uri`/`token_uri` em HTTPS e em `google.com`/`googleapis.com`.
  Só os campos usados são copiados para `%LOCALAPPDATA%/xl_utils/drive_client.json`,
  de forma atômica.
- **Teste offline de ponta a ponta:** servidor falso em `127.0.0.1` faz o papel
  do Google e confere PKCE e `state`; o navegador vira uma função que busca a
  URL. Nenhuma credencial real e nenhuma rede.
- **Teste semi-automático:** `scripts/check-drive-login.py` exercita o
  consentimento real do Google e imprime só e-mail, nome, escopos e a presença
  do refresh token.
- **Repositório público:** o JSON empacotado continua vazio; um teste impede
  que credencial real seja commitada. `.gitignore` cobre `drive_client.json`
  local e os nomes usuais de download.

## Tarefas

1. `save_client`/`import_client`/`is_configured` em `shared/drive_auth.py`,
   com validação e escrita atômica.
2. `DriveSession.configured` e `import_client`; login bloqueado sem cliente.
3. `ClientImport` (seletor nativo) e botão **Configurar** no cartão e no menu.
4. `tests/test_drive_flow.py`: sucesso, acesso negado, `state` estranho,
   timeout e mensagem sem token.
5. Testes de importação: round-trip, campos descartados, arquivo grande,
   arquivo não UTF-8, endpoint fora do Google e JSON empacotado vazio.
6. Script `scripts/check-drive-login.py` e documentação (setup, testes, UI,
   arquitetura, SECURITY e adendo ao ADR 0018).
7. Fechar com lint, testes, docs e commit.

## Aceite

- [x] Login de navegador testado de ponta a ponta, offline, com PKCE e `state`.
- [x] Importar o JSON pelo app funciona sem edição manual e sem sair do perfil.
- [x] JSON inválido, grande ou apontando para fora do Google é recusado.
- [x] Nenhuma credencial real no repositório nem no histórico; teste guarda o
      JSON empacotado vazio.
- [x] Script semi-automático imprime só o necessário e não grava conta.

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `CURRENT.md`, esta spec, o ADR 0018 e
`shared/drive_auth.py`. Consultar `ui/drive.py`, `ui/components/top_menu.py`
e `tests/test_drive_flow.py` só no que a importação tocar.

## Arquivos prováveis

- `src/xl_utils/shared/drive_auth.py`, `src/xl_utils/ui/drive.py`
- `src/xl_utils/ui/components/client_import.py`,
  `ui/components/top_menu.py`
- `tests/test_drive_flow.py`, `tests/test_drive_auth.py`,
  `tests/test_drive_session.py`
- `scripts/check-drive-login.py`, `.gitignore`, `SECURITY.md`
- `docs/adr/0018-drive-autenticacao.md`, `docs/guide/setup.md`,
  `docs/guide/testing.md`, `docs/reference/ui.md`,
  `docs/reference/architecture.md`

## Riscos

- O seletor nativo pode não estar disponível em ambiente headless; o teste
  cobre a sessão e a validação, não o diálogo do sistema.
- O consentimento real do Google continua dependendo do dono e de um projeto
  no Google Cloud; nenhum código contorna isso.
- Um `client_secret` de app desktop não é confidencial, mas o refresh token é;
  só ele fica sob DPAPI.

## Próximo depois desta

S9b — Drive II: link/seletor e escrita do resultado.
