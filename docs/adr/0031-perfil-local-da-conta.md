# ADR 0031 — Perfil local da conta: foto e apelido

- **Status:** aceita
- **Data:** 2026-11-25
- **Complementa:** ADR 0029 (item “Foto e apelido (S21b)”)

## Contexto

O ADR 0029 previu uma engrenagem no painel de perfis para o usuário trocar a
foto e o nome que aparecem no topo. O login só pede `drive.file`, `openid` e
`email`. Por isso o app não tem a foto do Google, e o avatar mostrava só as
iniciais. A S21b abriu com um questionário de três pontos: tela, tratamento da
foto e recorte.

## Decisão

- **Tela:** diálogo modal `AlertDialog` (“Configurar conta”), aberto pela
  engrenagem do cabeçalho do painel. Nada de página nova nem de entrada na
  navegação. A largura sai de `page.width`, com teto de 360 px.
- **Engrenagem:** é um `MenuItemButton` só com ícone. O `SubmenuButton` do
  Flet 1.1.2 não tem `close()`, e é o `MenuItemButton` que fecha o painel
  antes de o diálogo abrir. Conferido no `--web`: o diálogo chega com cerca de
  1 s de atraso, por causa da animação.
- **Rascunho:** a foto e o apelido ficam em memória até **Salvar**; Cancelar
  não grava nada. O diálogo guarda o e-mail da conta aberta e grava nela.
- **Foto:** Pillow (≥13, wheel cp315/cp315t para Windows e Linux). Aceita
  PNG, JPEG e WebP de até 10 MB e respeita a orientação do EXIF. O recorte é
  **automático no centro** (quadrado), a foto é reduzida a 256×256 e gravada
  como PNG. Imagem com pixels demais (aviso de bomba de descompressão do
  Pillow) é recusada. A decodificação roda fora da UI thread.
- **Armazenamento:** `drive/profiles/<hash>.json` (`{"nickname": ...}`) e
  `drive/profiles/<hash>.png`, com o mesmo hash de 16 caracteres das contas
  (`accounts.account_key`). Nem o nome nem o conteúdo guardam o e-mail. As
  gravações são atômicas (`.tmp` + `os.replace`). Apelido vazio e sem foto não
  deixam arquivo.
- **Exibição:** o apelido (até 16 caracteres, o mesmo limite do topo)
  substitui o nome no topo, no cabeçalho e no tooltip de “Abrir do Drive”;
  vazio volta ao nome do Google. A foto vai em `CircleAvatar.foreground_image_src`
  (bytes) e as iniciais ficam em `content`, por baixo, se a imagem falhar. As
  iniciais continuam vindo do nome do Google.
- **Sair** apaga a foto e o apelido só da conta que saiu.

## Consequências

- Uma dependência nova em todas as plataformas (Pillow). O build do Windows
  precisa levá-la; a S23 confere no release.
- A foto pesa cerca de 30 KB e é reenviada ao cliente Flet a cada redesenho do
  painel, o que não é problema nesse tamanho.
- Perfil não sincroniza entre máquinas nem com o Google: é local, como a conta.

## Alternativas

- **Página própria:** exigiria registrar em `PAGES` e tiraria o usuário da
  ferramenta aberta.
- **Sem Pillow, foto como veio até 1 MB:** recusaria a maioria das fotos de
  celular e mandaria o arquivo inteiro a cada redesenho.
- **Ajuste manual do recorte:** o Flet não tem um recortador pronto; o custo
  não cabe na sessão.
- **Foto do perfil do Google:** pediria o escopo `profile` ou uma chamada ao
  `userinfo`, contra o escopo mínimo do ADR 0018.
