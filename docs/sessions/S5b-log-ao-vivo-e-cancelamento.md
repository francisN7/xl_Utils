# S5b — Log ao vivo e cancelamento cooperativo

## Objetivo

Mostrar os eventos do log conforme são produzidos e permitir cancelar uma
execução em andamento, sem gravar nenhum arquivo.

## Fora de escopo

Mudar regras das ferramentas, novo layout, histórico de execuções, tema claro e
cancelar no meio de uma chamada do pandas.

## Tarefas

1. Estender a fila da S5a para transportar linhas de log junto com os
   `ProgressEvent`, sem conteúdo de célula; o painel passa a exibir os eventos
   conforme chegam.
2. Criar um token de cancelamento compartilhado (`shared/progress.py` ou módulo
   vizinho) com `cancel()` e `cancelled`; o layout o entrega ao handler.
3. As páginas consultam o token entre arquivos; nos lotes, também entre abas
   quando o controller expuser um ponto de parada. Sem interromper uma chamada
   em curso.
4. Ao cancelar: parar antes do próximo item, manter o que já foi calculado em
   memória, marcar o resultado como “Cancelado” e não habilitar ações de salvar
   para itens incompletos.
5. Trocar o botão “Executar” por “Cancelar” durante a execução, mantendo a
   entrada bloqueada; ao terminar, restaurar o estado normal.
6. Cobrir token, cancelamento entre arquivos e preservação do log no teste;
   garantir a integração dos quatro formatos verde.
7. Atualizar ADR 0011 (adendo sobre log/cancelamento), architecture e code tour.

## Aceite

- [ ] o log cresce durante a execução, sem esperar o fim
- [ ] cancelar entre arquivos interrompe o lote e não grava nada
- [ ] a UI continua sendo atualizada só no loop da página
- [ ] execução concluída mantém o comportamento atual da S5a
- [ ] `ruff`, `ruff format --check`, `pytest` e `docs:check` verdes

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec,
`shared/progress.py`, `ui/components/tool_layout.py`,
`ui/components/result_panel.py` e a seção “Execução e progresso” de
`reference/architecture.md`. Abrir as páginas só ao inserir as checagens do
token.

## Arquivos prováveis

- `src/xl_utils/shared/progress.py`
- `src/xl_utils/ui/components/tool_layout.py`
- `src/xl_utils/ui/components/result_panel.py`
- `src/xl_utils/ui/pages/*.py`
- `tests/test_progress.py`, `tests/test_layout.py`, `tests/test_integration.py`
- `docs/adr/0011-execucao-fora-da-ui.md`, `docs/reference/architecture.md`,
  `docs/guide/code-tour.md`

## Riscos

- Não dá para interromper pandas com segurança; o cancelamento é cooperativo e
  só vale no próximo ponto de checagem.
- O log ao vivo não pode reordenar eventos nem duplicar a linha final.
- `state.running` e o botão “Cancelar” precisam voltar ao normal em qualquer
  caminho de erro.
- Só atualizar a UI via fila/dispatcher; nunca da thread de trabalho.

## Próximo depois desta

Fase 2 — S5c, extração de CNJ em texto sujo.
