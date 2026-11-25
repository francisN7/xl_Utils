# ADR 0026 — Drive sem consentimento repetido

- **Status:** aceita
- **Data:** 2026-11-24

## Contexto

O Picker de apps desktop (ADR 0018, adendo S9b) exige `prompt=consent` e só
aceita `drive.file`, sem combinar com outro escopo. Por isso cada escolha de
arquivo ou pasta abre de novo a tela de consentimento do Google. O ADR 0025
planejava um seletor do Drive em Flet, dentro do app, alimentado pela Drive API
com o token do login (S24). A S16 mediu se isso é viável sem trocar o escopo.

## Medições (S16, 2026-11-24)

Spike descartável em `artifacts/spike_drive/` (fora do Git), Linux, uma conta
de teste, projeto do Google Cloud já em **Em produção**, token só em memória.

| Medição | Resultado |
|---|---|
| Login (`openid`, `userinfo.email`, `drive.file`) | 9,9 s, com a única tela de consentimento |
| `files.list` na raiz com o token do login | **0 itens**, 433 ms |
| Picker JS em `http://127.0.0.1:<porta>` com `setOAuthToken` | abriu nas 2 rodadas; visível 105–120 ms após carregar a página |
| Consentimento nas rodadas do Picker JS | **nenhum** (só no login) |
| `metadata` do arquivo escolhido com o token do login | ok, 296–373 ms; planilha nativa reconhecida |
| Picker JS só de pastas (`ViewId.FOLDERS`, `setSelectFolderEnabled`) | devolveu o ID da pasta; visível em 121 ms |
| Token inválido | o Picker mostra 403 e **não chama o callback** |
| Listagem dentro da pasta concedida e memória | não medidas (o processo foi encerrado antes) |

A primeira versão abria em `ViewId.SPREADSHEETS`, que mostra toda planilha já
aberta pela conta; o dono pediu abrir na raiz. `DocsView(ViewId.DOCS)` com
`setParent('root')`, `setIncludeFolders(true)` e filtro por MIME resolve.

## Comparação

| Caminho | Consentimento | Escopo | Verificação Google | Listagem própria | Esforço | Risco |
|---|---|---|---|---|---|---|
| A — Picker desktop + `drive.file` (atual) | a cada escolha | não sensível | não | não | zero | UX ruim |
| B — Picker JS no navegador padrão, página em `127.0.0.1`, token do login | só no login | não sensível | não | não precisa | médio | API key pública; token na página local |
| C — Seletor em Flet com `drive.readonly`/`drive` | só no login | **restrito** | sim, com avaliação de segurança anual | sim | alto | custo recorrente; reconsentir contas |
| D — outro navegador ou OAuth próprio | igual ao A | igual | igual | não | médio | não muda a regra do Google |

Com `drive.file`, a Drive API só enxerga o que o app criou ou o que o usuário
escolheu no Picker; a listagem própria do C é inútil sem escopo restrito. A
webview embutida (B original) foi descartada: o Flet desktop não tem `WebView`,
e o Google diz que o Picker não pode mais ser exibido em webview embutida.

## Decisão

- **Caminho B.** A escolha de arquivos e pastas do Drive passa a usar o Picker
  JavaScript, servido por um servidor efêmero em `127.0.0.1` e aberto no
  navegador padrão, com `setOAuthToken` recebendo o token de acesso da conta do
  app. O escopo continua `drive.file`; não há verificação nem reconsentimento.
- O Picker JS precisa de **API key** (restrita à Google Picker API) e do
  **número do projeto** (`setAppId`) para a concessão valer para o cliente. Os
  dois são públicos por natureza; como o `client_secret` (ADR 0018), entram no
  build, não no Git.
- A visão de arquivos abre no Meu Drive (`setParent('root')`) com pastas
  navegáveis e filtro de planilhas; a de gravação usa `ViewId.FOLDERS`.
- A página tem caminho com nonce aleatório, `Cache-Control: no-store`, responde
  só em `127.0.0.1` e morre depois do retorno. O token é renovado antes de
  servir a página; como o Picker não avisa erro de token, o app tem tempo-limite
  e botão de cancelar.
- O Picker de desktop (A) fica como fallback enquanto o B não estiver no app.
- O seletor do Drive em Flet (ADR 0025, adendo) é **descartado**: exigiria
  escopo restrito.

## Consequências

- A S24 deixa de ser o seletor em Flet e passa a trocar `drive_pick.py` pelo
  Picker JS, mantendo `drive_cache`, `drive_store` e a gravação como estão.
- A escolha continua no navegador, fora do tema do app; é o preço de evitar o
  escopo restrito.
- Hoje o build não embute o cliente OAuth: quem recebe o instalador teria de
  importar o JSON. Embutir cliente, API key e número do projeto no build entra
  no backlog antes da distribuição.
- O projeto já está em produção; com só `drive.file`, o refresh token não vence
  em 7 dias e não há avaliação de segurança.

## Alternativas

Ver a tabela: A (como está), C (escopo restrito) e D (sem efeito) foram
preteridas pelos motivos acima.
