# Interface

**O que responde:** layout, navegação, componentes e tema. **O que não
responde:** regras de negócio (ver `architecture.md`) nem o porquê (ver
`../adr/0003-ui-sidebar-e-inicio.md`).

## Layout

Sidebar fixa de 260 px + área de conteúdo. A sidebar é um `Column` próprio, não
um `NavigationRail`: assim ícones, rótulos e o item ativo ficam alinhados de
forma consistente. Ela tem o logo, o item **Início** e as quatro ferramentas
nativas; **Plugins** fica fixo no rodapé, acima de `uv · Python 3.15` e do
botão de tema, com o mesmo realce de selecionado. Os itens são identificados
pelo `id` da página (`registry.TOOLS` e `registry.FOOTER_PAGES`), não pela
posição. No
canto superior direito da área de conteúdo fica o painel de perfil do Google
Drive (avatar + nome) — fora da sidebar, para não competir com a navegação.

O logo da sidebar é `assets/icon.png` (36 px, cantos de 9 px), lido em bytes
para não depender do `assets_dir` do Flet; sem o arquivo, volta o quadrado roxo
com “x”. O ícone da janela (`page.window.icon`) é `assets/icon.ico` no Windows e
`assets/icon.png` nos demais. `ui/assets.py` resolve a pasta: raiz do repo no
dev e `sys._MEIPASS/assets` no exe (o build leva `assets/` com `--add-data`).
O conteúdo abre em uma das duas formas:

- **Início:** hub com cartões das ferramentas nativas.
- **Ferramenta:** cabeçalho + duas colunas (entrada/opções e resultado) + barra
  de ação fixa, separada do corpo por 16 px. As duas colunas rolam na vertical
  sem barra visível; os cartões recortam o conteúdo e nunca invadem a barra de
  ação.

```text
┌──────────┬────────────────────────────────────────────┐
│ Início   │  Título da ferramenta          [status]   │
│ Texto    ├───────────────────┬────────────────────────┤
│ CNJ      │ 1. Entrada        │ 3. Resultado           │
│ Recortar │    dropzone       │    status + caminho    │
│ Mesclar  │ 2. Opções         │    log + prévia        │
│          │                   │                        │
│          │                   │                        │
│          ├───────────────────┴────────────────────────┤
│ Plugins  │ [resumo]                    [Executar]     │
└──────────┴────────────────────────────────────────────┘
```

## Navegação e estado

- Trocar de ferramenta **mantém** o estado dela (arquivo, opções e resultado).
- Trocar o arquivo **reseta o resultado**; o valor das opções permanece.
- A página inicial é o hub; o item “Início” volta para ele.
- O avatar com o nome no canto superior direito abre o painel de perfis do
  Google Drive: entrar, selecionar outra conta, adicionar conta e sair. Ele não
  interfere na navegação das ferramentas.

## Plugins

A área **Plugins** lista os manifestos válidos e as pastas inválidas, instala um
`.tar.xz` pelo seletor nativo (com o sidecar ao lado) e remove com confirmação,
avisando que `data/` também é apagado. “Abrir” monta uma página com o mesmo
`ToolLayout` das ferramentas nativas, a partir de `[ui]` e `[[options]]`.

O `lib/` do plugin **não** é importado ao abrir o app, listar, navegar ou montar
a página: o import acontece no primeiro Executar e fica em cache até instalar ou
remover. Abrir a ferramenta também não lê planilha; a leitura começa no clique.

## Componentes

| Componente | Responsabilidade |
|---|---|
| `sidebar` | Logo, Início e as seis ferramentas, com item ativo destacado. |
| `top_menu` | Painel de perfil no canto superior direito: conta selecionada, outras contas, adicionar e sair. |
| `file_input` | Dropzone clicável + seletor nativo, lista de arquivos, remover e resetar. |
| `sheet_selector` | Chips por aba, “Todas”/“Limpar” e contador “N de M”. |
| `options_panel` | Controles específicos; aparece só quando há opção editável e guarda o valor no `ToolState`. |
| `result_panel` | Status, caminho de saída, abrir pasta, log e prévia. |
| `preview_table` | Primeiras linhas do resultado, somente leitura. |
| `tool_layout` | Cabeçalho, cartões, barra de ação, estados e a área de tela cheia; aceita entradas rotuladas no lugar da lista única. |

### Entrada de arquivos

O Flet 1.0 não expõe arrastar e soltar arquivos do sistema operacional. O
dropzone é uma área clicável que abre o `FilePicker` nativo; o texto "clique
para selecionar" substitui a promessa de drop. As ferramentas em lote aceitam
vários arquivos: depois do primeiro, o dropzone vira “Adicionar outro arquivo” e
a lista permite remover cada um. Um plugin pode declarar entradas rotuladas
(`[ui].inputs` no manifesto): uma planilha em cada rótulo, sem lista acumulada.

Com uma conta do Drive conectada, um botão quadrado com o ícone do Drive aparece
à direita da dropzone, na mesma linha e sem texto. Uma conta abre o Picker
direto; duas ou mais abrem um diálogo para escolher qual. O arquivo escolhido é
baixado para o cache local com o nome real e entra na lista como qualquer
arquivo do computador.

Arquivo local continua sempre no seletor nativo do sistema operacional. No
Drive, o ADR 0026 troca o Picker de desktop, que pede consentimento a cada
escolha, pelo Picker JavaScript aberto no navegador com o token do login:
consentimento só no login, abrindo no Meu Drive com pastas e filtro de
planilhas. A troca é a S24; até lá o app usa o Picker de desktop.

Cada arquivo da lista mostra o tamanho e, quando o conteúdo diverge da
extensão, uma linha discreta com o tipo real (ex.: `conteúdo: .xlsx · nome:
.xls`). Se nem o conteúdo nem a extensão apontarem para um formato suportado, a
linha fica vermelha com “Não foi possível identificar o formato”; a execução é
bloqueada antes da leitura e o motivo vai para o log e o diagnóstico. No caso
comum, nada além do nome e do tamanho aparece.

Texto e CNJ não têm opções editáveis: o card “2. Opções” não aparece e o
comportamento fixo fica em uma frase no card “1. Entrada” (remoção de emojis e
quebras preservadas; padronização e deduplicação de CNJ). Recorte e merge
mantêm o card, respectivamente com o campo de linhas e o quadro de colunas; sem
opções, o resultado passa a ser o cartão “2. Resultado”.

### Seleção de abas

Abaixo da lista de arquivos, o card “1. Entrada” mostra chips com o nome de cada
aba. No lote, o padrão marca todas as abas de todos os arquivos; no merge, a
primeira de cada um. “Todas” e “Limpar” mudam tudo de uma vez e o contador
mostra “N de M”. Os chips quebram linha (`Row(wrap=True)`) e a seleção é
guardada por arquivo no `ToolState`. Se a listagem falhar, o seletor mostra o
erro do arquivo e a execução reporta a falha de leitura; sem nenhuma aba
marcada, a ferramenta não executa e pede uma seleção. Enquanto as abas são
lidas, aparece um spinner e o botão Executar fica desabilitado.

### Mesclagem

O merge usa a mesma seleção de abas, com a primeira aba de cada arquivo marcada
por padrão quando há vários. Em “2. Opções”, a seção **“Alinhamento de colunas”**
mostra um quadro de colunas de saída. Cada chip representa uma coluna de uma
aba e exibe `arquivo · aba`; arrastar um chip para outra coluna junta as duas
no mesmo destino, e arrastar para antes de outro chip muda a ordem. O **primeiro
chip de cada coluna define o cabeçalho** e recebe o ícone de alfinete.

Os botões “+ esq.” e “+ dir.” criam uma coluna vazia ao lado; “Nova coluna”
acrescenta uma no fim. Uma coluna vazia só aparece como área de destino e é
ignorada na execução. Colunas com o mesmo nome já nascem juntas; para separar
uma correspondência automática, crie uma coluna vazia e arraste um dos chips
para ela. Cada aba pode contribuir com no máximo uma coluna por saída. O quadro
é refeito quando os arquivos ou as abas mudam e o estado vive em
`ToolState.options`.

O ícone de tela cheia ao lado do título abre o quadro sobre o conteúdo inteiro
da página. Os cards mantêm a largura fixa e a sobra vira espaçamento entre eles;
nada é esticado. “CONFIRMAR” aparece no canto inferior direito e, como o mesmo
ícone, restaura o cartão sem refazer os grupos: seleção e ordem continuam
válidas. O restante da página fica atrás da área maximizada e não recebe cliques.

A saída `Merge.xlsx` mostra `ORIGEM` (arquivo sem extensão e aba) e
`LINHA_ORIGEM` (posição da linha no resultado, com zeros à esquerda) como
primeiras colunas.

## Início

O hub mostra um cartão por ferramenta nativa (Plugins fica só no rodapé da
sidebar), com 200 px de altura: até quatro por
linha no desktop, dois no médio e um no mobile. Cada cartão tem ícone, nome,
descrição e o atalho “Abrir ferramenta”. O nome ocupa uma única linha e ganha
reticências quando falta espaço — nunca quebra no meio da palavra; a descrição
fica em até duas linhas, também com `…`, e mostra o texto completo no tooltip.
O cartão recorta o conteúdo, então o atalho permanece dentro da área mesmo em
largura estreita. Novas ferramentas entram da esquerda para a direita; a próxima
linha também começa à esquerda. As quatro nativas cabem numa linha no desktop.

## Drive

O canto superior direito mostra a conta selecionada: avatar com as iniciais e
o nome (sem nome, o e-mail curto). O clique abre o painel de perfis
(`ui/components/top_menu.py`, estado em `ui/drive.py`). Não existe cartão do
Drive no hub: entrar é uma ação do painel, como em qualquer app com “Entrar com
Google”.

- **Sem conta:** o topo e o painel mostram **Entrar com Google**. Se o cliente
  OAuth ainda não estiver configurado, o primeiro clique pede o JSON baixado do
  Google Cloud Console, uma única vez; feito isso, o navegador abre.
- **Com uma ou mais contas:** o painel abre com a conta selecionada (avatar,
  nome e e-mail). As demais ficam em **Outras contas**, uma lista retrátil que
  começa fechada; clicar numa delas a seleciona. **Adicionar conta** e **Sair**
  ficam fixos embaixo. Sair remove só a selecionada e seleciona a primeira que
  sobrar (ordem de e-mail); as outras contas e os arquivos já abertos ficam.
  E-mails longos aparecem truncados com `…`; o valor completo fica no tooltip,
  que surge depois de 3 s de hover.
- **Abrir do Drive:** o botão ao lado da dropzone abre direto na conta
  selecionada, sem perguntar; o tooltip diz qual é.
- **Durante o login:** o topo e o painel mostram “Conectando ao Google…”. Se o
  usuário negar o acesso ou o navegador não responder em três minutos, a
  mensagem aparece no topo do painel e nada fica travado.

O token nunca aparece na tela, no log ou no diagnóstico; os detalhes ficam no
ADR 0018.

Com uma planilha aberta do Drive, o painel de resultado troca **Salvar em
output/** por **Salvar no Drive**. A gravação usa sempre a conta que abriu o
arquivo, mesmo com outra selecionada; o tooltip do botão diz qual. Se essa conta
saiu do app, o botão fica desabilitado e pede para entrar de novo com ela. A
primeira gravação pede a pasta no Picker e lembra a concessão por conta; as
seguintes gravam direto. Recusar a pasta manda
o resultado para a raiz do Meu Drive, com aviso. O sucesso mostra o nome, a
pasta e o botão **Abrir no Drive**.

## Resultado e prévia

A prévia fica **sempre visível** no painel de resultado. Depois de executar, o
painel entra em **“Pronto para salvar”**: a prévia aparece, mas nenhum arquivo
é criado.

- **Salvar** abre o seletor nativo: `save_file` para uma saída, com o nome
  sugerido editável, ou `get_directory_path` para várias saídas.
- **Salvar em output/** grava no `output/` de cada origem, sem diálogo; o merge
  usa a pasta da primeira origem.
- Quando a entrada veio do Drive, **Salvar em output/** dá lugar a **Salvar no
  Drive**: a primeira gravação pede a pasta no Picker, a concessão fica
  lembrada por conta e recusar cai na raiz do Meu Drive. Nome ocupado ganha
  `_001`, `_002`... e o sucesso mostra “Abrir no Drive”.
- Cancelar o seletor mantém a prévia e os botões; nada é gravado.
- Nomes existentes ganham sufixo; o log registra o caminho real como
  `Salvo: <caminho>`.
- Após salvar, o caminho real aparece, “Abrir pasta” é liberado e os botões de
  salvar somem. Falha de escrita mostra o erro e mantém a prévia.
- primeiras 100 linhas e todas as colunas;
- rolagem vertical com barra oculta e horizontal com barra só quando precisa;
- vista fixa de 240 px, com o log limitado a 160 px para não espremer a prévia;
- “Copiar log” copia os eventos; “Copiar diagnóstico” copia versões, arquivos,
  abas, opções, resultado e, quando houver, tipo, mensagem, causa e traceback;
- cabeçalho da tabela com fundo próprio, acompanhando a rolagem;
- valores vazios aparecem como célula vazia, não como `nan`;
- a planilha original nunca é alterada.

## Temas (escuro e claro)

O app abre no tema salvo em `%LOCALAPPDATA%/xl_utils/settings.json` (fallback
`~/.xl_utils/settings.json`), chave `theme` com `dark` ou `light`. Arquivo
ausente, inválido ou com valor desconhecido abre no escuro. A preferência é
gravada na sidebar e aplicada na hora, sem perder o estado da ferramenta.

O tema claro é a variante Alucard do Dracula: fundo creme quente, sem branco
puro, com os mesmos matizes de roxo, rosa, verde, amarelo, ciano e laranja
escurecidos para manter o contraste AA.

| Token | Escuro | Claro | Uso |
|---|---|---|---|
| Fundo | `#282A36` | `#F2EEE1` | fundo do app |
| Fundo profundo | `#21222C` | `#E9E4D4` | sidebar, barras |
| Superfície | `#343746` | `#FBF7E9` | cartões |
| Borda | `#44475A` | `#D7D0BC` | divisores e contornos |
| Texto | `#F8F8F2` | `#1F1F1F` | texto principal |
| Muted | `#6272A4` | `#6C664B` | texto secundário |
| Texto sutil | `#C9CBDC` | `#4B4636` | itens inativos e log |
| Texto de chip | `#B8BCD0` | `#4B4636` | chips e títulos de cartão |
| Primária | `#BD93F9` | `#644AC9` | botão e seleção |
| Destaque | `#FF79C6` | `#A3144D` | realces |
| Sucesso | `#50FA7B` | `#14710A` | conclusão |
| Aviso | `#FFB86C` | `#A34D14` | atenção na entrada |
| Andamento | `#F1FA8C` | `#75600F` | execução e aviso de reabertura |
| Erro | `#FF5555` | `#B02A1C` | falha |
| Info | `#8BE9FD` | `#036A96` | links e caminhos |
| Fundo de sucesso | `#22342A` | `#E6F2DB` | selo “Pronto” |
| Borda de sucesso | `#2C4A38` | `#A9C79A` | contorno do selo |
| Fundo de erro | `#3A2428` | `#F8E3DD` | bloco de erro |
| Fundo de info | `#1F3438` | `#E1EEF2` | bloco informativo |
| Seleção | `#2D2A47` | `#E7E1F5` | chip de aba selecionado |
| Fundo do ícone | `#332B45` | `#ECE6F8` | ícone do cartão do hub |

No Flet: `page.theme_mode` recebe `DARK` ou `LIGHT`; `page.theme` usa a paleta
clara e `page.dark_theme` a escura. Os componentes leem `theme.X` no momento em
que montam o controle, nunca a constante importada direto. Ao alternar,
`theme.apply(mode)` troca os tokens e `theme.restyle` recolore a árvore já
montada, sem reconstruir páginas nem perder `ToolState`. Controles são mutados
no lugar; bordas e estilos (`Border`, `BorderSide`, `TextStyle`, `ButtonStyle`,
`Gradient`) são recriados inteiros. Mutar um `BorderSide` ao vivo fazia o Flet
mandar um patch parcial e o `border_radius` do `Container` sumia.

A tipografia usa a escala de `ui/theme.py`: mínimo de **12 px** (`FONT_XS`) para
dicas, contadores, log e células; 13 px (`FONT_SM`) para corpo e rótulos; 15 px
(`FONT_MD`) para nomes de ferramenta; 24/26 px para títulos. Texto nunca fica
abaixo de `FONT_XS`.

## Estados

| Estado | O que mostra |
|---|---|
| Vazio | Dropzone e botão desabilitado. |
| Selecionado | Arquivos, opções (quando existirem) e botão habilitado. |
| Lendo abas | Spinner “Lendo as abas...” e Executar desabilitado. |
| Formato desconhecido | Linha vermelha na entrada; Executar mostra “Não foi possível identificar o formato”. |
| Sem abas | Aviso “Selecione ao menos uma aba” e nenhuma execução. |
| Executando | Status amarelo, barra indeterminada e log de etapas crescendo. |
| Já processada | `AlertDialog` de reexecução; “Continuar” recalcula sem repetir o protocolo. |
| Sucesso | Status verde, caminho, “Abrir pasta” e prévia. |
| Erro | Status vermelho, título tipado, mensagem original e diagnóstico copiável. |

## Acessibilidade

- Contraste mínimo AA para o texto principal nos dois temas; a paleta clara
  também passa AA nos textos secundários, chips e cores de status.
- Navegação por teclado no seletor e na barra de ação.
- Nunca usar cor como único sinal de status: sempre ícone + texto.
