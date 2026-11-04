# ADR 0011 — Execução fora da UI thread e progresso por arquivo

- **Status:** aceita
- **Data:** 2026-11-04

## Contexto

As quatro ferramentas chamavam o controller no callback do botão. Em uma
planilha grande, `prepare_workbook` e a regra da ferramenta bloqueavam o loop da
página: a janela parava de responder, sem barra nem contador. Flet não é
thread-safe; `Control.update()` precisa partir do loop da página, mas o trabalho
pesado deve sair dele.

## Decisão

- `shared/progress.py` define `ProgressEvent`, `ProgressReporter` e
  `NullReporter`. O reporter recebe `start(total)`, `file_started(name)`,
  `file_done(name)` e `finish()`; o evento carrega só nomes de arquivo e
  contagem, nunca conteúdo de célula.
- `ToolLayout._run` valida formato e estado no loop, e então:
  - sem página (testes headless), executa o handler no próprio loop com um
    reporter síncrono;
  - com página, agenda `_execute_async` por `page.run_task`.
- `_execute_async` roda `_execute` em `asyncio.to_thread` e consome os
  `ProgressEvent` de um `asyncio.Queue` alimentado por `call_soon_threadsafe`.
  O loop aplica cada evento na barra e no texto “Arquivo X de Y”.
- As páginas recebem o reporter e marcam início/fim de cada arquivo. Merge
  reporta uma única etapa, porque o controller mescla todas as fontes de uma vez.
- `ResultPanel` e `PreviewTable` aceitam um dispatcher. Durante a execução
  assíncrona, todo `update` é agendado no loop; a thread de trabalho só monta
  dados e agenda callbacks. O caminho síncrono continua atualizando direto.
- “Executar”, a entrada de arquivos e os chips de abas ficam desabilitados até o
  fim; falha do callback de progresso é isolada e vira aviso no log.

## Consequências

- A janela permanece responsiva e o contador reflete os arquivos concluídos.
- `RunHandler` passa a ter três parâmetros; páginas e testes foram ajustados.
- O estado da ferramenta ainda é preenchido pela thread de trabalho; a UI só o
  lê depois que a execução termina, com a entrada bloqueada.
- Log ao vivo e cancelamento ficam para a S5b: esta sessão só entrega o
  progresso agregado por arquivo.
- O merge precisa de uma execução por etapa para ter contagem por origem; isso
  exigiria mudar o controller, fora do escopo.

## Alternativas

- **`page.run_thread`:** não devolve um ponto de encontro para drenar a fila com
  o resultado; `run_task` + `to_thread` deixa o ciclo explícito.
- **Atualizar controles direto da thread:** arrisca mensagens fora de ordem e
  corrupção da árvore; rejeitado pela regra do Flet.
- **Rodar só o controller na thread e exibir no loop:** exigiria separar cálculo
  e apresentação nas quatro páginas; a fila de progresso resolve com menos
  mudança nesta fase.
- **Cancelar no meio do arquivo:** não dá para interromper pandas com segurança;
  o cancelamento cooperativo entre arquivos fica na S5b.
