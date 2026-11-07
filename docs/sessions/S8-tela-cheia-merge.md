# S8 — Tela cheia no merge

## Objetivo

Maximizar o quadro de alinhamento de colunas do merge e restaurar a tela sem
perder a seleção de colunas nem os grupos.

## Fora de escopo

- Mudar o modelo de grupos, a ordem ou o arraste dos chips.
- Aplicar tela cheia às outras ferramentas.
- Google Drive e mudanças de tema.

## Tarefas

1. Criar um botão de maximizar ao lado de “Alinhamento de colunas”, visível só
   quando o quadro tem colunas.
2. Em tela cheia, ocupar a área inteira e distribuir os cards lado a lado com a
   largura atual de cada um; a sobra vira espaçamento, nunca estica o card.
3. Mostrar “CONFIRMAR” no canto inferior direito só durante a tela cheia.
4. Restaurar no mesmo botão ou em “CONFIRMAR”, preservando grupos, seleção e
   ordem.
5. Manter o botão “Executar” e o restante da página fora da área maximizada.
6. Testar janela larga e estreita, muitos cards e troca de tema durante a tela
   cheia.
7. Fechar com lint, testes, docs e commit.

## Aceite

- [ ] Maximizar ocupa a tela e restaura no mesmo botão.
- [ ] “CONFIRMAR” aparece só maximizado e também restaura.
- [ ] A largura de cada card não muda; a sobra vira espaçamento.
- [ ] Grupos, seleção e ordem sobrevivem à ida e volta.
- [ ] Lint, testes e docs verdes.

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `CURRENT.md`, esta spec e a seção **Mesclagem** de
`docs/reference/ui.md`. Consultar `ui/pages/merge.py`,
`ui/components/tool_layout.py` e `tests/test_merge.py` só nas partes do quadro.

## Arquivos prováveis

- `src/xl_utils/ui/pages/merge.py`
- `src/xl_utils/ui/components/tool_layout.py`
- `tests/test_merge.py`
- `docs/reference/ui.md`, `CHANGELOG.md`

## Riscos

- O painel de resultado e a barra de ação não podem ficar clicáveis por baixo
  da área maximizada.
- Reconstruir o quadro ao restaurar pode perder os grupos; guardar o estado em
  `ToolState.options` e só alternar a visibilidade.
- A largura fixa dos cards (`_CARD_WIDTH`) precisa ser respeitada para não
  espremer chips e quebrar o arraste.

## Próximo depois desta

S9a — Drive I: ADR de autenticação, OAuth, contas e shell.
