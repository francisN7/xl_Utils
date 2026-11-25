# S22 — Auditoria dos docs e documentação para quem chega

## Objetivo

Quem nunca viu o projeto consegue entender, rodar e fazer a primeira
contribuição só pelos docs, e todo `.md` bate com o código atual. O README e o
site ficam com banner, badges e screenshots.

## Fora de escopo

- Mudança de código ou de comportamento do app (achado de bug vira backlog).
- Release, build e notas da 0.4.0 (S23).
- Picker JS (S24) e versão Linux empacotada (backlog).

## Tarefas

1. Auditar todos os `.md` contra o código com a skill `docs-review` (o pedido
   desta sessão é o pedido explícito): relatório com evidências antes de
   editar.
2. Trilha de onboarding: o que é → rodar → arquitetura → tour do código →
   primeira contribuição, ligada a partir do `README.md` e do `docs/README.md`.
3. Glossário dos termos do domínio (CNJ, AGENDA, FINANCEIRO, `all_str`,
   conta selecionada, perfil local…).
4. Diagramas do fluxo de dados e das camadas (`core` → `controllers` → `ui`,
   `shared`, plugins, Drive) em `architecture.md`.
5. Guia de contribuição e tabela “onde mexer para…”; conferir que todo módulo
   atual aparece em `architecture.md` e `code-tour.md`.
6. README e site: banner, badges, tagline animada e screenshots dos dois
   temas, com dados fictícios.

## Aceite

- [ ] Relatório do `docs-review` aplicado ou com cada item justificado.
- [ ] Trilha de onboarding e glossário publicados e ligados no mapa.
- [ ] Todo módulo de `src/xl_utils/` citado em `architecture.md` ou
      `code-tour.md`.
- [ ] README com badges e screenshots; o site publica só se o HTML mudar
      (ADR 0019).
- [ ] `ruff`, `pytest` e `uv run python scripts/check_docs.py` verdes.

## Orçamento de contexto (≤90 linhas)

`docs/README.md` (mapa), depois só a seção de cada doc auditado; o código por
`grep`/`glob`, nunca arquivo inteiro sem necessidade.

## Arquivos prováveis

- `README.md`, `docs/README.md`, `docs/reference/architecture.md`
- `docs/guide/code-tour.md`, `docs/guide/` (novos: onboarding, glossário,
  contribuição)
- `docs/index.html` (site), `assets/` (screenshots)

## Riscos

- Escopo grande: priorizar a trilha de onboarding e o que está errado.
- Screenshots não podem ter e-mail, nome ou planilha real.
- Doc 👤 (README, CHANGELOG) tem tom humano; histórico (ADRs, ciclos) não se
  reescreve.

## Próximo depois desta

S23 — Release 0.4.0 e fechamento do ciclo 0009.
