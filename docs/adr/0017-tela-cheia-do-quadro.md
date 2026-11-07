# ADR 0017 — Tela cheia do quadro de mesclagem

- **Status:** aceita
- **Data:** 2026-11-07

## Contexto

O quadro de alinhamento do merge vive dentro do cartão “2. Opções”, na coluna
esquerda. Com muitas colunas, os cards de 196 px ficam espremidos e o arraste
perde precisão. O dono pediu uma tela cheia que preserve grupos, seleção e
ordem, sem transformar a maximização em um novo modelo de layout.

## Decisão

- `ToolLayout` monta a página dentro de um `ft.Stack` com a página normal e um
  `OverlayHost` invisível por cima. O host cobre só o conteúdo da ferramenta;
  a sidebar continua visível e o “Executar” fica atrás da área maximizada.
- O host tem um único slot. O painel da tela cheia é montado uma vez no
  início e só a visibilidade do host alterna entre maximizado e normal. A
  árvore continua no `Stack`, então `theme.restyle` recolore o painel mesmo
  quando ele está escondido.
- Cada fábrica de opções recebe o host. Hoje só o merge o usa; as demais
  ferramentas recebem e ignoram, sem mudar a anatomia da página.
- O merge mantém dois quadros (cartão e tela cheia) alimentados pelo mesmo
  `self._groups`. Grupos, chips e ordem vivem fora dos controles visuais;
  renderizar de novo um quadro não muda a seleção nem o `ToolState.options`.
- A largura fixa de 196 px é mantida. Na tela cheia, `Row(wrap=True)` com
  `SPACE_BETWEEN` transforma a sobra em espaçamento; nunca estica o card.
- “CONFIRMAR” fica no canto inferior direito do painel e o ícone de restaurar
  fica no cabeçalho. Ambos chamam o mesmo `_restore`, que só esconde o host.

## Consequências

- Maximizar e restaurar não reconstroem grupos nem perdem o arraste em curso.
- O painel acompanha a troca de tema sem recriar controles.
- O restante da página não recebe cliques enquanto o host cobre o conteúdo.
- A tela cheia não esconde a sidebar; navegar para outra ferramenta mantém a
  página em cache e o quadro maximizado ao voltar.
- As outras ferramentas continuam sem tela cheia até uma sessão própria.

## Alternativas

- **`page.overlay`:** cobriria a janela inteira e exigiria calcular posição e
  tamanho; a sidebar também ficaria bloqueada, o que não foi pedido.
- **Esconder cabeçalho, resultado e barra:** perderia o “Executar” e o contexto
  da ferramenta; o pedido era ampliar o quadro, não trocar a página.
- **Reconstruir a página ao restaurar:** arriscava perder grupos e ordem, além
  de descartar o estado do arraste.
