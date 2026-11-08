# S9b — Drive II: link, seletor e escrita do resultado

## Objetivo

Ler uma planilha do Drive escolhida pelo usuário e gravar o resultado de volta
no Drive, sem passar pelo `output/` local.

## Fora de escopo

- Exportar nas demais ferramentas e acabamento (S9c).
- Mudar o fluxo local de `output/`.
- Reautenticação silenciosa em segundo plano.

## Decisão que abre a sessão

O ADR 0018 fixou `drive.file`, que só enxerga arquivo **criado pelo app ou
escolhido no Google Picker** — link colado não basta. Antes do código, escolher:

- **(a) Google Picker:** fiel ao escopo mínimo, mas exige API key, JS e uma
  webview no Flet; peça nova só para escolher arquivo.
- **(b) Escopo `drive` em modo Testing:** o dono entra como *test user*, sem
  verificação; consentimento mais amplo e contas atuais precisam ser refeitas.
- **(c) Híbrido:** `drive.file` para o que o app criou e link só para esses
  arquivos; não cobre planilha antiga do usuário.

Recomendação: **(b)** enquanto o app é pessoal, com adendo no ADR 0018 dizendo
o que muda ao publicar para terceiros.

## Tarefas

1. Adendo ao ADR 0018 com a decisão de acesso e o efeito nas contas já salvas.
2. `shared/drive.py`: cliente REST com `requests` para baixar, exportar planilha
   nativa (`files.export`, mime de `.xlsx`), listar quando o escopo permitir,
   criar e atualizar (`files.create`/`files.update` multipart). Tratar 401,
   403, 404 e quota com mensagem em PT-BR.
3. Montar `Credentials` a partir da conta ativa (refresh token do store + client
   config) e renovar fora da UI thread; token expirado renova uma vez.
4. UI: no seletor de entrada da ferramenta, “Abrir do Drive” (link e/ou
   seletor); no painel de resultado, “Salvar no Drive” só quando houver prévia.
5. Pipeline: os bytes baixados viram arquivo temporário com o nome real e
   entram no `all_str`; a saída gerada é enviada ao Drive sem criar nada em
   `output/`.
6. Testes offline com transporte falso: download, export, upload, refresh em
   401 e erros legíveis. Nenhum teste faz rede.
7. Fechar com lint, testes, docs e commit.

## Aceite

- [ ] Planilha do Drive lida pelo link ou seletor e processada como local.
- [ ] Resultado salvo no Drive sem arquivo em `output/`.
- [ ] Token expirado renova uma vez; 403/404 viram mensagem clara.
- [ ] Testes offline verdes; ferramentas locais intactas.

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `CURRENT.md`, esta spec, o ADR 0018, `shared/drive_auth.py`,
`shared/accounts.py`, `ui/drive.py` e as assinaturas de `core/io.py` e
`core/save.py`. Não abrir as páginas das cinco ferramentas.

## Arquivos prováveis

- `docs/adr/0018-drive-autenticacao.md` (adendo), `docs/adr/README.md`
- `src/xl_utils/shared/drive.py`, `src/xl_utils/shared/accounts.py`
- `src/xl_utils/ui/drive.py`, `ui/components/file_input.py`
- `ui/components/result_panel.py`, `ui/components/tool_layout.py`
- `tests/test_drive_api.py`, `CHANGELOG.md`

## Riscos

- Escopo restrito pede consentimento novo: contas salvas param de valer.
- Planilha nativa do Google não é `.xlsx`; sem `files.export` a leitura falha.
- Nome duplicado no Drive e upload grande: não sobrescrever sem intenção.
- Refresh token revogado vira erro claro, nunca loop de login.

## Próximo depois desta

S9c — Drive III: exportação nas demais ferramentas e acabamento.
