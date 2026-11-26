# S24 — Picker JavaScript do Drive (implementação)

> **Ciclo 0010:** primeira sessão, depois da 0.4.0. Spec escrita após o ADR
> 0026 (S16). **Arquivo local continua no seletor nativo do sistema
> operacional.** O seletor do Drive em Flet foi descartado.

## Objetivo

Trocar o Picker de desktop, que pede consentimento a cada escolha, pelo Picker
JavaScript aberto no navegador padrão a partir de uma página em `127.0.0.1`,
usando o token de acesso da conta do app. Consentimento só no login, escopo
`drive.file`, download e gravação como estão.

## Fora de escopo

- Trocar escopo, pedir verificação do Google ou listar o Drive pelo app.
- Seletor em Flet, webview embutida ou migração de stack.
- Menu de perfis (S21) e o fluxo de gravação além da escolha da pasta.

## Tarefas

1. Config: API key e número do projeto ao lado do cliente OAuth
   (`drive_client.json` ou arquivo irmão), com validação e override local;
   nunca no Git. Mensagem clara quando faltarem (cai no Picker de desktop).
2. `shared/drive_pick.py`: servidor efêmero em `127.0.0.1`, caminho com nonce,
   `no-store`, página com `DocsView(DOCS)` + `setParent('root')` +
   `setIncludeFolders(true)` + filtro de planilhas; modo pasta com
   `ViewId.FOLDERS` + `setSelectFolderEnabled(true)`; múltipla escolha.
3. Token: renovar o de acesso da conta antes de servir a página; tempo-limite e
   cancelar, porque o Picker não chama o callback com token inválido (403).
4. Integrar onde hoje se chama `pick_files` (leitura e concessão de pasta);
   remover o segundo OAuth (`trigger_onepick`) ou deixá-lo como fallback.
5. Testes offline: página gerada, nonce, retorno de IDs, cancelar, timeout e
   ausência do token em log/erro; um teste manual com a conta de teste.
6. Medir o que a S16 não mediu: `files.list` dentro da pasta concedida.
7. Atualizar `docs/reference/ui.md`, `architecture.md`, code tour e CHANGELOG.

## Aceite

- [ ] Escolher arquivo e pasta não mostra tela de consentimento após o login.
- [ ] O Picker abre no Meu Drive, com pastas e só planilhas.
- [ ] O arquivo escolhido vira o mesmo caminho de cache de hoje.
- [ ] Token inválido ou expirado vira mensagem clara, sem traceback nem espera
  infinita.
- [ ] Sem API key configurada, o app usa o Picker de desktop.
- [ ] `ruff`, `pytest` e `uv run python scripts/check_docs.py` verdes.

## Orçamento de contexto (≤90 linhas)

Ler o ADR 0026, o adendo S9b/S9c do ADR 0018, `shared/drive_pick.py`,
`drive_auth.py`, `drive.py` → `token_provider`, `ui/drive.py` e
`docs/reference/architecture.md` → **Drive**. O spike da S16 ficou fora do Git;
o desenho da página está no ADR 0026.

## Arquivos prováveis

- `src/xl_utils/shared/drive_pick.py`, `src/xl_utils/shared/drive_auth.py`
- `src/xl_utils/ui/drive.py`, `tests/test_drive_pick.py`
- `docs/reference/ui.md`, `docs/reference/architecture.md`,
  `docs/guide/code-tour.md`, `docs/guide/setup.md`, `CHANGELOG.md`

## Riscos

- O token de acesso vai para uma página local: só `127.0.0.1`, nonce, `no-store`
  e servidor que morre após o retorno; nunca em log.
- API key restrita por HTTP referrer pode quebrar o Picker; restringir por API.
- O Picker JS carrega `apis.google.com`: sem rede, mensagem clara.
- Conta errada no navegador: o token é da conta do app, então o Picker usa
  essa conta; conferir se a concessão vale para o token salvo.

## Próximo depois desta

Embutir cliente OAuth, API key e número do projeto no build para distribuir.
