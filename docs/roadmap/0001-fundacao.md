# Fundação — o que foi entregue (2026-11-04)

Ciclo 0001 fechado. O detalhe completo está no Git; as decisões ficam nos ADRs.

| Sessão | Entrega | Aceite |
|---|---|---|
| S0a | Branch `feat/ui`, uv no Python 3.15, estrutura MVC, shell Flet, docs e check | app importa; `ruff`, `pytest` e `docs:check` verdes |
| S0b | Tema Dracula, sidebar + Início, quatro cartões, entrada/resultado/prévia, estado por ferramenta | app abre e navega; UI aprovada; validação verde |

**Resultado do ciclo:** app desktop navegável com quatro ferramentas, base de UI
e documentação entre sessões prontas para a migração.

## Decisões do ciclo

- [ADR 0001](../adr/0001-stack-ui-e-ambiente.md) — stack, uv, Flet e fim do CLI.
- [ADR 0002](../adr/0002-arquitetura-core-ui.md) — arquitetura core/controllers/ui.
- [ADR 0003](../adr/0003-ui-sidebar-e-inicio.md) — sidebar + Início e anatomia de ferramenta.
- [ADR 0004](../adr/0004-leitura-segura-e-emojis.md) — leitura segura e emojis.

## Validação de fechamento

`uv run ruff check src tests`, `uv run pytest` e `node scripts/check-docs.mjs`
verdes antes do fechamento. O ciclo seguinte começa em
[`0002-migracao.md`](0002-migracao.md).
