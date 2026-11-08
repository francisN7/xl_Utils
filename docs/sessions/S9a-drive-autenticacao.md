# S9a — Drive I: ADR, OAuth, contas e shell

## Objetivo

Entrar no Google Drive pelo navegador, alternar entre contas e sair pela tela
inicial, sem ainda ler ou gravar planilhas.

## Fora de escopo

- Link da planilha, seletor de arquivos do Drive e transferência (S9b).
- Exportação das demais ferramentas para o Drive (S9c).
- Mudar o pipeline de saída atual em `output/`.
- Reautenticação silenciosa em segundo plano.

## Tarefas

1. Escrever o ADR 0018 decidindo: escopo OAuth (`drive.file`), biblioteca,
   formato do client ID/secret, armazenamento de tokens e identidade das contas.
   O destino da saída fica para a S9c. Ligar no índice.
2. Implementar o fluxo de autorização para app desktop: PKCE, `state`,
   redirecionamento em `127.0.0.1` com porta efêmera, abertura pelo navegador
   padrão e timeout claro quando o usuário cancela.
3. Guardar contas por e-mail em `%LOCALAPPDATA%/xl_utils/`, com gravação atômica
   e sem token em texto no log, diagnóstico ou mensagem de erro.
4. Adicionar o menu hamburger no canto superior e o estado do Drive na tela
   inicial: entrar, conta ativa, trocar e sair. Nada disso pode bloquear a
   navegação existente.
5. Testar store de contas, montagem da URL de autorização e troca de conta com
   transporte falso; nenhum teste faz rede.
6. Fechar com lint, testes, docs e commit.

## Aceite

- [x] ADR 0018 aceito e indexado.
- [ ] Login abre o navegador e retorna sem terminal; cancelar não deixa a UI
      travada. *(implementado e testado com transporte falso; o login real
      depende do `drive_client.json` do dono)*
- [x] Token e client secret nunca aparecem em log, diagnóstico ou screenshot.
- [x] Duas contas alternáveis; “Sair” remove a conta ativa sem apagar as outras.
- [x] Testes offline verdes e navegação das ferramentas intacta.

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `CURRENT.md`, esta spec, a seção **Navegação e estado** de
`docs/reference/ui.md` e `app.py`. Consultar `sidebar.py`, `shared/settings.py`
e `ui/state.py` só no que a autenticação tocar. Nada de código do Drive antes
do ADR.

## Arquivos prováveis

- `docs/adr/0018-drive-autenticacao.md`, `docs/adr/README.md`
- `src/xl_utils/shared/drive_auth.py`, `src/xl_utils/shared/accounts.py`
- `src/xl_utils/ui/components/top_menu.py`
- `src/xl_utils/app.py`, `tests/test_drive_auth.py`, `CHANGELOG.md`

## Riscos

- Client secret de app desktop não é segredo; o ADR precisa assumir PKCE e
  tratar o client ID como público.
- Token em URL, log ou traceback: redigir antes de qualquer diagnóstico.
- Porta de callback ocupada ou navegador fechado: bind efêmero + timeout e
  mensagem acionável.
- Alternar conta durante execução: permitir só com `state.running` falso.
- Dependência nova pode quebrar Python 3.15; validar no `uv add` antes de
  espalhar o uso.

## Próximo depois desta

S9b — Drive II: link/seletor de planilha e escrita do resultado.
