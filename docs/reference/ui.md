# Interface

**O que responde:** layout, navegação, componentes e tema. **O que não
responde:** regras de negócio (ver `architecture.md`) nem o porquê (ver
`../adr/0003-ui-sidebar-e-inicio.md`).

## Layout

Sidebar fixa de 240 px + área de conteúdo. A sidebar é um `Column` próprio, não
um `NavigationRail`: assim ícones, rótulos e o item ativo ficam alinhados de
forma consistente. Ela tem o logo, o item **Início** e as quatro ferramentas.
O conteúdo abre em uma das duas formas:

- **Início:** hub com cartões das ferramentas.
- **Ferramenta:** cabeçalho + duas colunas (entrada/opções e resultado) + barra
  de ação fixa.

```text
┌──────────┬────────────────────────────────────────────┐
│ Início   │  Título da ferramenta          [status]   │
│ Texto    ├───────────────────┬────────────────────────┤
│ CNJ      │ 1. Entrada        │ 3. Resultado           │
│ Recortar │    dropzone       │    status + caminho    │
│ Mesclar  │ 2. Opções         │    log + prévia        │
│          ├───────────────────┴────────────────────────┤
│          │ [resumo]                    [Executar]     │
└──────────┴────────────────────────────────────────────┘
```

## Capturas

![Tela inicial](../assets/ui-base.png)

![Página de ferramenta](../assets/ui-tool.png)

## Navegação e estado

- Trocar de ferramenta **mantém** o estado dela (arquivo, opções e resultado).
- Trocar o arquivo **reseta** opções e resultado daquela ferramenta.
- A página inicial é o hub; o item “Início” volta para ele.

## Componentes

| Componente | Responsabilidade |
|---|---|
| `sidebar` | Logo, Início e as quatro ferramentas, com item ativo destacado. |
| `file_input` | Dropzone clicável + seletor nativo, lista de arquivos, remover e resetar. |
| `options_panel` | Controles específicos da ferramenta. |
| `result_panel` | Status, caminho de saída, abrir pasta, log e prévia. |
| `preview_table` | Primeiras linhas do resultado, somente leitura. |
| `tool_layout` | Cabeçalho, cartões, barra de ação e estados. |

### Entrada de arquivos

O Flet 1.0 não expõe arrastar e soltar arquivos do sistema operacional. O
dropzone é uma área clicável que abre o `FilePicker` nativo; o texto "clique
para selecionar" substitui a promessa de drop.

## Início

O hub mostra quatro cartões em uma linha no desktop, dois no médio e um no
mobile, com 200 px de altura. Cada cartão tem ícone, nome, descrição e o atalho
“Abrir ferramenta”. Novas ferramentas entram da esquerda para a direita; a
próxima linha também começa à esquerda.

## Resultado e prévia

A prévia fica **sempre visível** no painel de resultado:

- primeiras 100 linhas e todas as colunas;
- rolagem horizontal e vertical;
- cabeçalho fixo;
- valores vazios aparecem como célula vazia, não como `nan`;
- a planilha original nunca é alterada.

## Tema Dracula (dark)

| Token | Hex | Uso |
|---|---|---|
| Fundo | `#282A36` | fundo do app |
| Fundo profundo | `#21222C` | sidebar, barras |
| Superfície | `#343746` | cartões |
| Borda | `#44475A` | divisores e contornos |
| Texto | `#F8F8F2` | texto principal |
| Muted | `#6272A4` | texto secundário |
| Primária | `#BD93F9` | botão e seleção |
| Destaque | `#FF79C6` | realces |
| Sucesso | `#50FA7B` | conclusão |
| Aviso | `#FFB86C` | atenção |
| Erro | `#FF5555` | falha |
| Info | `#8BE9FD` | links e caminhos |

No Flet: `page.theme_mode = ft.ThemeMode.DARK` e
`page.theme = ft.Theme(color_scheme=ft.ColorScheme(...))`. O tema claro fica
fora do escopo inicial.

## Estados

| Estado | O que mostra |
|---|---|
| Vazio | Dropzone e botão desabilitado. |
| Selecionado | Arquivos, opções e botão habilitado. |
| Executando | Progresso, botão “Cancelar” e log ao vivo. |
| Sucesso | Status verde, caminho, “Abrir pasta” e prévia. |
| Erro | Status vermelho, mensagem tipada e log copiável. |

## Acessibilidade

- Contraste mínimo AA sobre o fundo Dracula.
- Navegação por teclado no seletor e na barra de ação.
- Nunca usar cor como único sinal de status: sempre ícone + texto.
