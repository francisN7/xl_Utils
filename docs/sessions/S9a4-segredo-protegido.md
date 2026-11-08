# S9a4 — Segredo do cliente OAuth protegido

## Objetivo

Instalar o cliente OAuth baixado do Google Cloud no perfil do usuário, apagar o
arquivo de download e reduzir o risco do segredo em repouso. No Windows, o
`client_secret` passa a ser gravado cifrado por DPAPI.

## Fora de escopo

- Distribuir o cliente no repositório público.
- Criptografar o JSON inteiro; só o segredo é confidencial.
- Trocar o fluxo OAuth ou o escopo `drive.file`.

## Decisões

- **DPAPI no campo `client_secret_dpapi`:** o JSON local mantém `client_id`,
  `auth_uri` e `token_uri` legíveis e guarda o segredo cifrado. `load_client`
  decripta em memória para o fluxo.
- **Fallback fora do Windows:** o segredo fica no campo `client_secret` em
  texto, porque o segredo de app desktop não é confidencial e o CI roda em
  Linux.
- **`repr=False`:** `ClientConfig` não mostra o segredo em `repr`, log ou
  diagnóstico.
- **Download descartado:** após a importação, o JSON baixado é sobrescrito com
  zeros e apagado. Em SSD a sobrescrita é melhor esforço, não garantia física.
- **Nada no Git:** o cliente instalado fica em `%LOCALAPPDATA%`; o JSON
  empacotado continua vazio e o `.gitignore` cobre os nomes de download.

## Tarefas

1. Gravar o segredo com DPAPI no `save_client`.
2. Ler e decriptar o campo no `_parse`, com erro amigável se o blob falhar.
3. Esconder o segredo do `repr` do `ClientConfig`.
4. Testes: ida e volta, segredo ausente do arquivo, `repr`, blob inválido.
5. Instalar o cliente real, verificar o estado e apagar o download.
6. Atualizar setup, SECURITY, ADR 0018, roadmap, CHANGELOG e estado.

## Aceite

- [x] Cliente instalado em `%LOCALAPPDATA%/xl_utils/drive_client.json`.
- [x] JSON local com `client_secret` vazio e `client_secret_dpapi` presente.
- [x] `is_configured()` verdadeiro e URL de consentimento montada.
- [x] Download apagado e nenhuma cópia em arquivo rastreado.
- [x] Docs, lint e testes verdes.

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `CURRENT.md`, esta spec e `shared/drive_auth.py`. Consultar
`shared/accounts.py` só para o DPAPI e `tests/test_drive_auth.py` para os
casos de segredo.

## Arquivos prováveis

- `src/xl_utils/shared/drive_auth.py`
- `tests/test_drive_auth.py`
- `docs/guide/setup.md`, `SECURITY.md`, `docs/adr/0018-drive-autenticacao.md`
- `docs/roadmap/main.md`, `docs/state/CURRENT.md`, `CHANGELOG.md`

## Riscos

- O blob DPAPI é atrelado ao usuário do Windows; trocar de perfil exige
  reimportar o JSON.
- Sobrescrever o download não garante remoção física em SSD.
- O JSON empacotado no build continua em texto; ele não é segredo de usuário.

## Próximo depois desta

S9b — Drive II: link/seletor e escrita do resultado.
