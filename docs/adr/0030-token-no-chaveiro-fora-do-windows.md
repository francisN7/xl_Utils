# ADR 0030 — Token do Drive no chaveiro do sistema fora do Windows

- **Status:** aceita
- **Data:** 2026-11-25
- **Substitui em parte:** ADR 0018 (“DPAPI é Windows-only; fora do Windows o
  store recusa gravar”)

## Contexto

O ADR 0018 protegeu o `refresh_token` com DPAPI e tratou o app como só para
Windows: em outro sistema, `AccountStore.save` recusava gravar. O dono passou a
usar só Linux. O login no navegador funcionava, mas a conta nunca era guardada
e o painel voltava para “Entrar com Google” com a mensagem “A proteção de
tokens do Drive só existe no Windows.” A versão Linux saiu dos gatilhos e foi
para o backlog.

## Decisão

- **Windows continua com DPAPI**, sem mudança de formato: o arquivo da conta
  guarda o blob em base64 no campo `token`.
- **Fora do Windows, o token vai para o chaveiro do usuário** pelo pacote
  `keyring` (Secret Service do GNOME Keyring ou do KDE/KWallet; Keychain no
  macOS). Serviço `xl_utils/drive`; a chave é o mesmo hash de 16 caracteres do
  nome do arquivo, nunca o e-mail. O arquivo da conta não tem `token` e marca
  `"vault": "keyring"`.
- `keyring` entra só com o marcador `sys_platform != 'win32'`: o build Windows
  não carrega nada novo. O import é preguiçoso.
- **Sair** apaga primeiro o arquivo e depois o segredo. Se o chaveiro falhar,
  a conta já sumiu do app e o erro aparece no painel.
- **Erros do chaveiro** viram `AccountsError` só com o tipo do erro
  (`KeyringLocked`, `NoKeyringError`…), nunca com a mensagem do backend.
  Conta cujo segredo sumiu do chaveiro é ignorada na lista, como arquivo
  corrompido.
- **Testes** nunca tocam o chaveiro real: o `conftest.py` troca
  `KeyringVault` por um cofre em memória.

## Consequências

- Login e “Sair” funcionam no Linux. Conferido no KDE (Secret Service do
  `ksecretd`): gravar, ler e apagar um token falso.
- Chaveiro trancado pode pedir a senha ao abrir o app, porque a lista de contas
  lê os tokens.
- Contas não migram entre sistemas: cada máquina entra de novo.
- O `client_secret` do cliente OAuth continua sem DPAPI fora do Windows; ele é
  público por natureza (ADR 0018).

## Alternativas

- **Cifrar o token com chave própria em arquivo:** a chave ficaria ao lado do
  segredo, sem proteção real.
- **`keyring` também no Windows:** mudaria o formato de quem já tem conta
  guardada e não ganha nada sobre o DPAPI.
- **Token em texto com permissão 0600:** qualquer processo do usuário leria.
