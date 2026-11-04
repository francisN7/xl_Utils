# S4c — Traduzir `ui/` e `shared/` e revisar o diagnóstico

## Objetivo

Completar a tradução de comentários e docstrings para PT-BR e revisar a cópia do
diagnóstico, sem mudar o comportamento das ferramentas.

## Fora de escopo

Novos recursos, mudança de layout, empacotamento, release, edição da `legacy` e
reescrita do core.

## Tarefas

1. Traduzir docstrings e comentários de `src/xl_utils/ui/` e
   `src/xl_utils/shared/`, mantendo identificadores em inglês.
2. Revisar `build_diagnostics` e as mensagens de erro da UI: campos, limites e
   garantia de que nenhum conteúdo de célula entra no texto.
3. Conferir se `docs/guide/code-tour.md` e `docs/reference/architecture.md`
   continuam verdadeiros depois da tradução; corrigir o que estiver defasado.
4. Atualizar a convenção do `AGENTS.md` (remover o backlog de tradução) e
   registrar a sessão em `CURRENT.md`, `main.md` e `CHANGELOG.md`.
5. Rodar a validação completa e commitar com `S4c: ...`.

## Aceite

- [ ] `ui/` e `shared/` sem docstring/comentário em inglês
- [ ] diagnóstico revisado e sem conteúdo de célula
- [ ] code tour e arquitetura conferidos
- [ ] `ruff`, `ruff format --check`, `pytest` e `docs:check` verdes
- [ ] `CURRENT.md`, roadmap e `CHANGELOG.md` atualizados

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec e `docs/guide/code-tour.md`.
Abrir só os arquivos de `ui/`/`shared/` que estiverem sendo traduzidos e a seção
“Logging e erros” de `reference/architecture.md`.

## Arquivos prováveis

- `src/xl_utils/ui/**/*.py` e `src/xl_utils/shared/*.py`
- `docs/guide/code-tour.md`, `docs/reference/architecture.md`
- `docs/state/CURRENT.md`, `docs/roadmap/main.md`, `CHANGELOG.md`

## Riscos

- Traduzir docstring não pode alterar texto de UI nem mensagem de erro; testes de
  `test_layout.py`, `test_ui_state.py` e `test_log.py` seguram o comportamento.
- O diagnóstico é copiado pelo usuário; revisar o texto exige cuidado para não
  incluir conteúdo de célula nem caminho sensível além do necessário.
- Tradução ampla gera diff grande; separar por camada e não misturar com regra.

## Próximo depois desta

Escolher com o dono o próximo item do backlog (histórico de execuções, cancelar
execução em andamento ou tema claro).
