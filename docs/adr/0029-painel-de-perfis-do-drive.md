# ADR 0029 — Painel de perfis do Drive com conta selecionada

- **Status:** aceita
- **Data:** 2026-11-25
- **Substitui em parte:** ADR 0018 (conta ativa e “Sair”)

## Contexto

Até a S20, o menu hambúrguer listava os e-mails com `checked` na conta ativa, e
“Sair desta conta” removia a ativa. Com duas ou mais contas, o “Abrir do Drive”
mostrava um diálogo perguntando qual usar; a conta ativa só servia para o
`checked` e para o fallback do `account_for`. A S21 previa tirar a conta ativa.
No questionário de abertura, o dono preferiu o caminho contrário: um painel de
perfil no estilo Google, com uma conta selecionada que o “Abrir do Drive” usa
direto.

## Decisão

- **Conta selecionada.** `drive/active.json`, `AccountStore.set_active` e
  `DriveSession.switch` continuam. O nome na UI e nos docs passa a ser “conta
  selecionada”. Se a marca aponta para uma conta que não existe mais, a sessão
  usa a primeira em ordem de e-mail, só em memória. `next_account` saiu.
- **Topo.** O hambúrguer dá lugar ao avatar (iniciais) e ao nome da conta
  selecionada (sem nome, o e-mail curto). Sem conta: “Entrar com Google”.
- **Painel.** Cabeçalho com avatar, nome e e-mail; “Outras contas” numa lista
  retrátil que começa fechada (clicar seleciona); “Adicionar conta” e “Sair”
  fixos embaixo. Nada de `checked`.
- **Sair.** Remove só a conta selecionada e seleciona a primeira que sobrar;
  sem contas, limpa a marca. Não roda com a sessão ocupada. As outras contas, as
  concessões de pasta e as cópias já abertas no cache ficam.
- **Abrir do Drive.** Usa a conta selecionada, sem diálogo; o tooltip do botão
  diz qual é.
- **Salvar no Drive.** Usa sempre a conta de origem do arquivo, mesmo com outra
  selecionada; o tooltip diz qual. `account_for` não cai mais na selecionada: a
  pasta de origem só é visível para a conta que a abriu (`drive.file`). Se essa
  conta saiu, o botão fica desabilitado e o clique explica: “Entre de novo com
  <e-mail> para salvar no Drive.” Cópia sem e-mail de origem: “Abra o arquivo
  de novo pelo Drive para salvar lá.”
- **Componente.** O `PopupMenuItem` do Flet 1.1.2 não tem submenu nem aceita uma
  lista retrátil. O painel é um `SubmenuButton` dentro de um `MenuBar`
  transparente, cujo menu aceita controles quaisquer (`ExpansionTile`,
  `CircleAvatar`, `MenuItemButton`). O spike da S21a conferiu no `--web`, nos
  dois temas, que ele abre, expande sem fechar e fecha ao escolher. O
  `MenuStyle` não passa pelo `theme.restyle`; por isso a troca de tema chama
  `TopMenu.refresh()`, que remonta o painel com os tokens novos.
- **Foto e apelido (S21b).** A engrenagem no cabeçalho abre a configuração da
  conta; sem foto, o avatar mostra as iniciais; o apelido substitui o nome.
  Ao sair, foto e apelido somem junto com a conta.

## Consequências

- Um clique a menos para abrir do Drive com várias contas; em troca, a conta
  em uso precisa estar sempre visível (topo e tooltip).
- Conta selecionada diferente da conta de origem é um caso normal, não um erro:
  o salvamento segue a origem e diz isso no tooltip.
- O teste do shell passa a esperar um `MenuBar` no canto superior direito.

## Alternativas

- **Sem conta ativa, diálogo no “Abrir do Drive”** (plano original da S21):
  descartada pelo dono; o diálogo a cada abertura é atrito.
- **Submenu por e-mail com “Sair desta conta”:** impossível com o
  `PopupMenuItem` do Flet 1.1.2 e substituído pelo painel.
- **`PopupMenuButton(content=…)` com lista fixa:** era o plano B do spike; não
  foi preciso.
- **Salvar na conta selecionada quando a origem saiu:** a outra conta não
  enxerga a pasta (`drive.file`); o arquivo cairia na raiz dela sem o usuário
  perceber.
