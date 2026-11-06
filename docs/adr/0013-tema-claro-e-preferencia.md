# ADR 0013 — Tema claro e preferência salva

- **Status:** aceita
- **Data:** 2026-11-06

## Contexto

A paleta Dracula era um conjunto de constantes em `ui/theme.py`, lidas pelos
componentes no momento em que montavam cada controle. O dono pediu leitura
confortável em ambiente claro, sem mudar layout nem fluxo das ferramentas.
Reconstruir a árvore a cada troca descartaria arquivos, abas e resultado; o
desafio é recolorir o que já está montado.

## Decisão

- `ui/theme.py` guarda `DARK` e `LIGHT` com as mesmas chaves e expõe
  `apply(mode)`: ele troca os tokens do módulo. `build_theme(mode)` monta o
  `ColorScheme` direto da paleta pedida, sem depender do estado global.
- As paletas usam nomes semânticos (`TEXT`, `MUTED`, `SUBTLE_TEXT`,
  `CHIP_TEXT`, `SUCCESS_BG`, `SELECTED_BG`, `ICON_BG`, `SUCCESS_BORDER`) e os
  componentes leem `theme.X` ao montar o controle.
- `shared/settings.py` persiste a chave `theme` em
  `%LOCALAPPDATA%/xl_utils/settings.json`, com fallback para
  `~/.xl_utils/settings.json`. Gravação usa arquivo temporário e `os.replace`.
- `app.main` lê a preferência e chama `theme.apply` **antes** de montar a
  sidebar e o hub. `page.theme` recebe a paleta clara, `page.dark_theme` a
  escura, e `page.theme_mode` escolhe uma delas.
- `theme.color_mapping` monta o mapa token a token entre as paletas e
  `theme.restyle` percorre controles e estilos já montados, trocando apenas os
  campos de cor conhecidos. Textos, dados, layout e o `ToolState` ficam
  intactos — um log que contenha `#282A36` continua igual.
- Controles são mutados no lugar, mas os tipos de valor (`Border`,
  `BorderSide`, `TextStyle`, `ButtonStyle` e `Gradient`) são reconstruídos e
  trocados inteiros. Mutar `BorderSide` no lugar fazia o Flet enviar um patch
  parcial e o `Container` perdia o `border_radius` na troca ao vivo.
- A sidebar grava a escolha e aplica na hora: troca `page.theme_mode`, recolore
  a sidebar, o hub e todas as páginas em cache, e atualiza a tela.

## Consequências

- A preferência sobrevive ao fechamento; settings ausente, corrompido ou com
  valor desconhecido cai no escuro sem erro visível.
- A troca é imediata e não perde arquivos, abas, opções nem resultado. Nenhuma
  página é reconstruída.
- A paleta clara é a variante Alucard do Dracula: creme quente, sem branco
  puro, com os mesmos matizes escurecidos. Foi medida com contraste AA nos
  pares de texto, chips e status; o texto principal do tema escuro também passa.
  O `MUTED` escuro continua como estava para não alterar a identidade visual do
  Dracula.
- Nenhuma regra de ferramenta, recorte ou merge muda.
- `settings.json` guarda só preferências, nunca caminho de planilha ou
  conteúdo de célula.

## Alternativas

- **Reconstruir a UI a cada troca:** exigiria reidratar páginas e estado;
  perderia seleção e resultado no meio do trabalho.
- **Seguir o tema do Windows:** o resultado mudaria sem o usuário pedir;
  preferência explícita é mais previsível.
- **QSettings ou registry:** adiciona dependência/plataforma; JSON no
  `%LOCALAPPDATA%` é simples, portátil e testável.
