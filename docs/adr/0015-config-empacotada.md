# ADR 0015 — Config empacotada e estado por máquina

- **Status:** aceita
- **Data:** 2026-11-06

## Contexto

O aplicativo precisa dos cabeçalhos padrão da vinculação para casar colunas e
saber onde inserir `VINCULA?`. Se esse arquivo morar na raiz do repositório, a
instalação em outra máquina — sem o checkout — não o encontra. O mesmo problema
vai aparecer no login do Google: uma parte da configuração é pública e pode
viajar no pacote; outra é segredo ou estado da máquina e nunca pode ir para o
Git nem para o instalador.

## Decisão

- **Config empacotada:** `src/xl_utils/configs/headers.json` fica dentro do
  pacote e viaja no wheel. É lido por `importlib.resources`, então funciona
  igual no checkout e na instalação. O `uv_build` inclui os arquivos do módulo;
  o wheel foi conferido.
- **Override opcional por máquina:** se existir
  `%LOCALAPPDATA%/xl_utils/headers.json` (ou `~/.xl_utils/headers.json` quando
  não houver `LOCALAPPDATA`), ele vence o padrão. Serve para ajustar rótulos
  sem rebuild; se estiver malformado, a ferramenta falha com `ConfigError` em
  vez de trabalhar com um mapa incompleto.
- **Segredos e estado:** credenciais, client secret, token e conta escolhida do
  Google vão para `%LOCALAPPDATA%/xl_utils/google/`. Nunca entram no repositório
  nem no wheel. O que for público (client ID e escopos) pode ficar em
  `src/xl_utils/configs/`.
- **Rede de segurança no Git:** `.gitignore` cobre `client_secret*.json`,
  `token*.json`, `credentials*.json` e `*.pem`. A proteção principal é o
  caminho por máquina; o ignore evita um commit acidental.
- **Nada de config na raiz do repositório.** A pasta `configs/` da raiz não é
  usada: ela não existiria na máquina de quem instala.

## Consequências

- A instalação funciona sem o repositório e sem passar caminho de configuração.
- O dono pode trocar um rótulo numa máquina sem gerar um novo wheel; o padrão
  continua no pacote.
- Um override inválido bloqueia a vinculação com mensagem clara, em vez de
  produzir saída incompleta.
- O instalador carrega só dados públicos; segredos nascem no login e ficam
  fora do Git.
- Testes carregam o JSON empacotado por `importlib.resources` e usam um
  `%LOCALAPPDATA%` temporário para o override, sem tocar na máquina real.

## Alternativas

- **`configs/` na raiz:** simples no desenvolvimento, quebrada na instalação.
- **Constantes no código:** evitaria o JSON, mas qualquer ajuste de rótulo
  exigiria rebuild e misturaria dado com regra.
- **Variável de ambiente por máquina:** mais uma coisa para configurar e
  documentar; o override em `%LOCALAPPDATA%` já resolve.
- **Guardar token no repositório:** proibido por segurança; o repo é público.
