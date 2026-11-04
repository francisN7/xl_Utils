# S6a — Histórico de execuções

## Objetivo

Guardar localmente um resumo das últimas execuções e mostrá-lo no Início, sem
conteúdo de célula e sem alterar o fluxo de salvar arquivos.

## Fora de escopo

Sincronizar, exportar ou compartilhar o histórico; guardar prévias ou células;
histórico por arquivo dentro da planilha; nova página na sidebar; tema claro.

## Tarefas

1. Criar `shared/history.py` com `HistoryEntry` (ferramenta, data/hora ISO,
   nomes dos arquivos, contagens do `state.message`, estado final e duração) e
   `HistoryStore`, que anexa em JSON Lines e mantém no máximo 50 entradas.
2. Caminho padrão em `%LOCALAPPDATA%/xl_utils/history.jsonl` (fallback para
   `~/.xl_utils/history.jsonl`); aceitar caminho injetado nos testes. Arquivo
   corrompido ou ilegível não pode derrubar a execução.
3. Registrar no fim de cada execução, inclusive erro e cancelamento, com o
   estado do `ResultPanel`; nunca gravar o caminho completo na interface.
4. Mostrar as cinco últimas entradas num cartão do Início, com ferramenta,
   horário, arquivos e resultado; atualizar ao abrir a página.
5. Cobrir `HistoryStore` com `tmp_path`: anexar, ordenar, limite de 50, JSON
   inválido e conteúdo sem célula; testar o registro no `ToolLayout`.
6. Atualizar `architecture.md`, `ui.md`, `code-tour.md` e o `CHANGELOG.md`.

## Aceite

- [ ] cada execução concluída, com erro ou cancelada vira uma entrada
- [ ] o histórico sobrevive ao fechamento do app e fica limitado a 50 itens
- [ ] o cartão do Início mostra as cinco mais recentes
- [ ] nenhum conteúdo de célula nem caminho completo aparece na tela
- [ ] falha de histórico não muda o resultado da ferramenta
- [ ] `ruff`, `ruff format --check`, `pytest` e `docs:check` verdes

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec, `shared/log.py`,
`ui/components/tool_layout.py`, `ui/pages/home.py`, `app.py`, `reference/ui.md`
(seção “Layout”) e a seção “Logging e erros” de `reference/architecture.md`.

## Arquivos prováveis

- `src/xl_utils/shared/history.py` (novo)
- `src/xl_utils/ui/components/tool_layout.py`
- `src/xl_utils/ui/pages/home.py`
- `src/xl_utils/app.py` (se o Início precisar recarregar)
- `tests/test_history.py`, `tests/test_layout.py`
- `docs/reference/architecture.md`, `docs/reference/ui.md`,
  `docs/guide/code-tour.md`

## Riscos

- Escrever no disco no caminho de erro: envolver em `try/except` e só registrar
  um aviso no log, nunca trocar o resultado.
- Dados pessoais: guardar nomes de arquivo e contagens, não células; o caminho
  completo fica fora da interface.
- Concorrência: execuções são serializadas pela UI, mas a escrita deve ser
  atômica (gravar temporário e substituir) para não truncar o JSONL.
- O Início é montado uma vez; recarregar só quando a página é exibida, sem
  recriar o shell.

## Próximo depois desta

Fechar o ciclo 0004 ou seguir para o tema claro, conforme decisão do dono.
