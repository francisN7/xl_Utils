# ADR 0018 — Autenticação no Google Drive

- **Status:** aceita
- **Data:** 2026-11-08

## Contexto

O app vai ler e gravar planilhas no Google Drive (S9). Antes de qualquer
código, é preciso decidir como o usuário entra, como as contas são guardadas e
o que a S9a entrega sem tocar em planilhas. O app é desktop, distribuído como
código aberto e roda só no Windows; o `client secret` de um app desktop é
público por definição.

## Decisão

- **Escopos:** `openid`, `https://www.googleapis.com/auth/userinfo.email` e
  `https://www.googleapis.com/auth/drive.file`. `drive.file` só enxerga o que
  o próprio app criou ou o usuário escolheu no seletor do Drive, e não exige
  verificação do Google. O e-mail vai na forma canônica porque o Google devolve
  `userinfo.email` mesmo quando o pedido usa o atalho `email`.
- **Biblioteca:** `google-auth-oauthlib` (1.5.x) com `requests`, o caminho que
  o Google recomenda para apps instalados. Na 1.5 o PKCE S256
  (`autogenerate_code_verifier=True`) e o `state` já vêm ligados por padrão, e
  `run_local_server` reserva a porta de forma exclusiva no Windows.
- **Fluxo:** redirecionamento em `http://127.0.0.1:porta` com porta efêmera
  (`port=0`), navegador padrão e `timeout_seconds` explícito. `localhost` não é
  usado porque alguns firewalls o bloqueiam. Cancelar ou fechar o navegador
  vira erro tratado, nunca UI travada.
- **Credenciais do cliente:** `src/xl_utils/configs/drive_client.json`
  empacotado, no formato `{"installed": {...}}`, com override em
  `%LOCALAPPDATA%/xl_utils/drive_client.json`. O `client_id` é público e pode
  viajar no pacote; o `client_secret` não é segredo em app desktop e nunca é
  impresso. O arquivo empacotado nasce com campos vazios: sem configuração, o
  app explica como criar o cliente em vez de falhar no meio do fluxo.
- **Identidade:** o e-mail e o nome vêm do `id_token` devolvido pelo endpoint
  de token por TLS. Não há chamada extra ao `userinfo`; o token não é
  verificado de novo porque veio direto do Google na mesma conexão.
- **Tokens:** uma conta por arquivo em
  `%LOCALAPPDATA%/xl_utils/drive/accounts/`, com o `refresh_token` protegido
  por DPAPI (`CryptProtectData`) e gravação atômica (`.tmp` + `os.replace`).
  O e-mail ativo fica em `drive/active.json`. Token nunca entra em log,
  diagnóstico, mensagem de erro ou `repr` de objeto.
- **Sair:** remove só a conta ativa e o token dela; as demais contas e o
  arquivo `active.json` continuam. Trocar de conta só é permitido com a
  ferramenta ociosa.
- **Destino da saída:** adiado para a S9c. Nada na S9a depende de escolher
  entre aba extra e `output/`; decidir agora criaria compromisso sem caso de
  uso.

## Consequências

- Entram cerca de nove pacotes (`google-auth`, `pyasn1`, `cryptography`,
  `requests-oauthlib`, `oauthlib`, `requests`, `urllib3`, `certifi`, `idna`,
  `charset_normalizer`); `requests` passa a servir também a Drive API REST na
  S9b, sem `google-api-python-client`.
- DPAPI é Windows-only. Fora do Windows o store recusa gravar com mensagem
  clara; os testes injetam um protetor falso.
- A página do navegador sempre diz “concluído”, inclusive quando o usuário
  nega o acesso; o erro real aparece no app.
- Não há DPoP, reautenticação silenciosa nem revogação remota no “Sair”.
- Se o cliente OAuth mudar, os `refresh_token` antigos param de funcionar e a
  conta precisa ser refeita.

## Alternativas

- **Fluxo PKCE próprio com `urllib`:** zero dependência, mas reimplementaria
  token, refresh e validação de `state`, justamente onde errar é caro.
- **`google-api-python-client`:** o SDK completo da Drive arrasta `protobuf` e
  `httplib2` para três chamadas REST; peso sem retorno.
- **Copiar/colar (OOB) ou esquema próprio de URI:** descontinuados pelo Google.
- **Token em texto puro:** mais simples, mas qualquer backup ou leitura do
  perfil expõe a conta inteira; DPAPI custa poucas linhas via `ctypes`.

## Adendo — importação do cliente e teste do login (S9a1)

O dono não deve editar JSON à mão. No primeiro clique em **Entrar com Google**,
quando ainda não há cliente, o app abre o seletor nativo e importa o arquivo
baixado do Google Cloud Console; depois disso o login é só clicar → navegador.
A validação ocorre antes de gravar: no máximo 64 KB, UTF-8, objeto JSON,
`client_id` no alfabeto do Google, `auth_uri`/`token_uri` em HTTPS e em
`google.com`/`googleapis.com`. Só os campos usados são copiados para
`%LOCALAPPDATA%/xl_utils/drive_client.json`, de forma atômica; campos
desconhecidos do arquivo original são descartados. O JSON empacotado continua
vazio e um teste garante que ninguém commite credencial real.

No Windows, o `client_secret` é gravado cifrado por DPAPI no campo
`client_secret_dpapi`; em texto ele só existe em memória durante o login. Em
outros sistemas, ou no JSON empacotado no build, ele fica em texto, porque o
segredo de app desktop não é confidencial. O `refresh_token` continua cifrado
por DPAPI. A única
entrada não confiável é o JSON importado; `authorize` só recebe um
`ClientConfig` já validado pelo app.

O fluxo de navegador passa a ter teste ponta a ponta offline: um servidor falso
em `127.0.0.1` faz o papel do Google, confere o PKCE (S256) e o `state`, e o
navegador é substituído por uma função que busca a URL. Cobrem sucesso, acesso
negado, `state` de outra requisição, timeout e ausência de token na mensagem de
erro. O consentimento real do Google é o único passo manual e é exercitado por
`scripts/check-drive-login.py`, que imprime só e-mail, nome, escopos e a
presença do refresh token.

## Adendo — Picker do Drive sem webview (S9b)

O Picker da S9b não usa a API JavaScript, API key nem webview. O Google oferece
o **Picker para apps desktop**, que é uma autorização OAuth comum: a URL de
consentimento leva `trigger_onepick=true`, `prompt=consent` e
`access_type=online`, e o retorno chega no mesmo loopback `127.0.0.1:porta` com
`picked_file_ids` e `code`.

Essa requisição aceita **só** `https://www.googleapis.com/auth/drive.file` — a
documentação do Picker não permite combiná-lo com `openid` ou `userinfo.email`.
Por isso o login da S9a continua como está e a escolha do arquivo faz uma
segunda autorização curta, que:

- **não** pede `access_type=offline`: cada escolha geraria um refresh token
  novo, e o Google invalida os mais antigos quando o cliente acumula tokens;
- serve apenas para baixar o arquivo recém-escolhido, com o token de acesso
  devolvido na hora;
- confere `state` e PKCE como o login.

A concessão é por arquivo e por cliente: o token da conta passa a enxergar o
arquivo escolhido sem mudar escopo nenhum, e as contas salvas continuam
válidas. No Cloud Console isso exige a **Google Picker API** ativa no mesmo
projeto; a Drive API já era necessária. Nada de cliente novo, API key ou
reconsentimento.

`picked_file_ids` pode trazer vários IDs (`allow_multiple=true`), o que a
mesclagem usa. Planilha nativa do Google é exportada por `files.export` com o
MIME de `.xlsx`; os demais formatos vêm por `alt=media`. O download vira um
arquivo temporário em `%LOCALAPPDATA%/xl_utils/drive/cache/<sessão>/` com o nome
real, e entra no pipeline normal — nada é gravado ao lado da origem do usuário.

Gravar de volta na pasta de origem fica para a S9c: `drive.file` concede arquivo
por arquivo, e a pasta do arquivo escolhido não vem junto. Será preciso o
usuário conceder a pasta uma vez (`allow_folder_selection=true`) e guardar essa
concessão por conta, ou aceitar a raiz do Meu Drive.
