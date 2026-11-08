# S9c — Drive III: gravar na pasta e exportar

## Objetivo

Salvar o resultado no Drive, dentro da pasta do arquivo de origem, sem passar
por `output/`; levar “Salvar no Drive” às demais ferramentas e fechar o
acabamento do Drive.

## Decisão que abre a sessão

`drive.file` concede arquivo por arquivo: ler `parents` do arquivo escolhido
funciona, mas `files.create` com essa pasta tende a responder 403 porque a pasta
não foi concedida. Antes do código, confirmar no teste real:

- **(a) Concessão da pasta uma vez:** o usuário escolhe a pasta no Picker com
  `allow_folder_selection=true`; a concessão é guardada por conta em
  `%LOCALAPPDATA%/xl_utils/drive/folders.json` e as próximas gravações naquela
  pasta não perguntam nada.
- **(b) Criar na raiz do Meu Drive:** nada novo para pedir, mas o arquivo não
  fica ao lado do original.
- **(c) Escopo `drive`:** resolve tudo e quebra a promessa de acesso mínimo.

Recomendação: **(a)**, com (b) como saída quando o usuário recusar a pasta.

## Tarefas

1. Adendo ao ADR 0018 com a concessão de pasta e o cache por conta.
2. `drive_pick`: aceitar `allow_folder_selection=true` e devolver também pastas.
3. `shared/drive.py`: `files.create` multipart e, se necessário, `files.update`
   para sobrescrever com confirmação.
4. `shared/drive_store.py` ou equivalente: `folders.json` atômico, por conta.
5. `DriveSession.save_to_drive(account, sheets, name)`, fora da UI thread.
6. `core/io.dump_workbook`: gerar os bytes do `.xlsx` sem gravar em `output/`.
7. `ResultPanel`/`ToolLayout`: “Salvar no Drive” só quando houver prévia; erro
   de pasta vira diálogo de concessão, não falha seca.
8. Recusa de nome duplicado: nunca sobrescrever sem intenção.
9. Testes offline: criação com e sem pasta concedida, 403 de pasta, cache de
   concessão, upload multipart e mensagens.
10. Docs, lint, testes e commit.

## Aceite

- [ ] Resultado salvo na pasta do arquivo de origem, sem `output/`.
- [ ] Segunda gravação na mesma pasta não pede permissão de novo.
- [ ] Pasta recusada cai na raiz com mensagem clara, sem perder o resultado.
- [ ] Arquivo existente nunca é sobrescrito sem confirmação.
- [ ] Testes offline verdes; leitura da S9b intacta.

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `CURRENT.md`, esta spec, o adendo novo do ADR 0018,
`shared/drive.py`, `shared/drive_pick.py`, `ui/drive.py` e as assinaturas de
`core/io.py` e `ui/components/result_panel.py`. Não abrir as páginas das cinco
ferramentas.

## Arquivos prováveis

- `shared/drive.py`, `shared/drive_pick.py`, `shared/drive_store.py`
- `ui/drive.py`, `ui/components/result_panel.py`, `ui/components/tool_layout.py`
- `core/io.py`, `tests/test_drive_write.py`, `docs/adr/0018-*.md`

## Riscos

- Pasta concedida pode não dar escrita (`canAddChildren`); o teste real decide.
- Upload multipart grande precisa de `timeout` folgado e mensagem de progresso.
- Não sobrescrever arquivo do usuário por engano é requisito, não detalhe.

## Próximo depois desta

Fechar o ciclo 0006 e revisar o backlog (Drive concluído).
