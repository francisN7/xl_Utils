# S5a — Execução fora da UI thread e barra de progresso

## Objetivo

Executar qualquer ferramenta sem travar a janela, com barra de progresso e
contador de arquivos concluídos.

## Fora de escopo

Log ao vivo e cancelamento (S5b), mudança de regra das ferramentas, novo
layout, histórico e tema claro.

## Tarefas

1. Criar `shared/progress.py` com um `ProgressReporter` opcional (`start`,
   `file_started`, `file_done`, `finish`) e um `NullReporter`; as mensagens não
   carregam conteúdo de célula.
2. Adaptar `ToolLayout._run` para rodar o handler em `asyncio.to_thread` e
   consumir os eventos em uma fila thread-safe no loop da página.
3. Adicionar barra de progresso e texto “Arquivo X de Y” ao painel de
   resultado; desabilitar “Executar” e a entrada enquanto roda.
4. Ajustar `RunHandler` e as quatro páginas para receber o reporter e marcar o
   início/fim de cada arquivo; controllers ficam sem mudança nesta sessão.
5. Manter o caminho síncrono quando não houver `page` (testes headless).
6. Cobrir o reporter e a contagem com teste; garantir que a integração nos
   quatro formatos continua verde.
7. Escrever ADR sobre a fronteira thread → Flet e atualizar architecture e code
   tour onde o fluxo mudar.

## Aceite

- [ ] uma planilha grande roda sem congelar a janela
- [ ] barra e contador refletem os arquivos concluídos
- [ ] nenhum `update` de UI é chamado da thread de trabalho
- [ ] controllers sem reporter continuam com o comportamento atual
- [ ] `ruff`, `ruff format --check`, `pytest` e `docs:check` verdes

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec,
`ui/components/tool_layout.py`, `controllers/all_str.py` e a seção “Logging e
erros” de `reference/architecture.md`. Abrir os demais controllers só ao
ajustar as páginas.

## Arquivos prováveis

- `src/xl_utils/shared/progress.py` (novo)
- `src/xl_utils/ui/components/tool_layout.py`
- `src/xl_utils/ui/pages/*.py`
- `tests/test_layout.py`, `tests/test_integration.py`
- `docs/adr/0011-*.md`, `docs/reference/architecture.md`,
  `docs/guide/code-tour.md`

## Riscos

- Flet não é thread-safe: só atualizar a UI no loop da página, via fila e
  `page.run_task`; nunca chamar `update` da thread de trabalho.
- `page.run_task` não existe em teste headless: manter um caminho síncrono.
- Callback com exceção não pode derrubar a execução; isolar e registrar no log.
- Diff grande: não misturar log ao vivo nem cancelamento (S5b).

## Próximo depois desta

S5b — log ao vivo e cancelamento cooperativo.
