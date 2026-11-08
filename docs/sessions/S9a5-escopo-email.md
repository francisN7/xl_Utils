# S9a5 — Login com escopo de e-mail canônico

## Objetivo

Corrigir a falha do login real que aparecia como “Não foi possível concluir a
entrada no Google.”, mesmo com o navegador mostrando a página de sucesso.

## Causa

O app pedia o atalho `email`; o Google devolvia o escopo canônico
`https://www.googleapis.com/auth/userinfo.email`. O `oauthlib` compara os dois
conjuntos e lança um `Warning` quando muda o escopo, o que o app tratava como
falha genérica.

## Decisões

- **Pedir o canônico:** `SCOPES` usa
  `https://www.googleapis.com/auth/userinfo.email` no lugar de `email`. O
  consentimento mostra a mesma permissão e o `id_token` continua trazendo o
  e-mail.
- **Sem relaxar a validação:** não usar `OAUTHLIB_RELAX_TOKEN_SCOPE`; alinhar o
  pedido é mais simples e mantém a checagem de escopo do `oauthlib`.
- **Teste de regressão:** um teste garante que o atalho `email` não volta.

## Tarefas

1. Trocar o escopo no `drive_auth.SCOPES`.
2. Ajustar o teste de credenciais e adicionar o teste de regressão.
3. Repetir o login real e confirmar refresh token, id_token e escopos.
4. Atualizar ADR 0018, setup, política, roadmap, CHANGELOG e estado.

## Aceite

- [x] Login real conclui sem `Warning` de escopo.
- [x] `refresh_token` e `id_token` presentes.
- [x] Testes, lint e docs verdes.
- [x] Documentação usa o escopo canônico.

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `CURRENT.md`, esta spec e `shared/drive_auth.py`. Consultar
`tests/test_drive_auth.py` e `tests/test_drive_flow.py` só no que o escopo tocar.

## Arquivos prováveis

- `src/xl_utils/shared/drive_auth.py`
- `tests/test_drive_auth.py`, `tests/test_drive_flow.py`
- `docs/adr/0018-drive-autenticacao.md`, `docs/guide/setup.md`,
  `docs/privacy.html`, `docs/roadmap/main.md`, `docs/state/CURRENT.md`,
  `CHANGELOG.md`

## Riscos

- Se o consentimento no Google Cloud ainda listar só `email`, adicionar
  `https://www.googleapis.com/auth/userinfo.email` em **Acesso a dados**.
- O app em execução precisa ser reiniciado para carregar a lista nova de
  escopos.

## Próximo depois desta

S9b — Drive II: link/seletor e escrita do resultado.
