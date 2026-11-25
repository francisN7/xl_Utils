# S22a — Auditoria dos docs e documentação para quem chega

## Objetivo

Quem nunca viu o projeto consegue entender, rodar e fazer a primeira
contribuição só pelos docs, e todo `.md` bate com o código atual.

## Fora de escopo

- Mudança de código ou de comportamento do app (achado de bug vira backlog).
- Banner, badges, tagline animada, screenshots e site (S22b).
- Release, build e notas da 0.4.0 (S23).
- Licença: segue “todos os direitos reservados”.

## Tarefas

1. Auditar todos os `.md` contra o código com a skill `docs-review` (o pedido
   desta sessão é o pedido explícito): relatório com evidências antes de
   editar.
2. Trilha de onboarding (`docs/guide/onboarding.md`): o que é → rodar →
   arquitetura → tour do código → glossário → primeira contribuição, ligada a
   partir do `README.md` e do `docs/README.md`.
3. Glossário (`docs/reference/glossary.md`) dos termos do domínio e do
   processo (CNJ, `all_str`, conta selecionada, perfil local, slot nomeado…).
4. Diagramas Mermaid das camadas e do fluxo de dados em `architecture.md`.
5. `CONTRIBUTING.md` para dev convidado e tabela “Onde mexer para…” revisada;
   todo módulo atual citado em `architecture.md` ou `code-tour.md`.
6. `scripts/check_docs.py` cobra a cobertura de módulos (regra 5).

## Aceite

- [ ] Relatório do `docs-review` aplicado ou com cada item justificado.
- [ ] Trilha de onboarding, glossário e `CONTRIBUTING.md` ligados no mapa.
- [ ] Todo módulo de `src/xl_utils/` citado em `architecture.md` ou
      `code-tour.md`; o check falha se faltar um.
- [ ] `ruff`, `pytest` e `uv run python scripts/check_docs.py` verdes.

## Orçamento de contexto (≤90 linhas)

`docs/README.md` (mapa), depois só a seção de cada doc auditado; o código por
`grep`/`glob`, nunca arquivo inteiro sem necessidade.

## Arquivos prováveis

- `README.md`, `CONTRIBUTING.md`, `docs/README.md`
- `docs/reference/{architecture,glossary}.md`
- `docs/guide/{code-tour,onboarding}.md`
- `scripts/check_docs.py`

## Riscos

- Escopo grande: priorizar a trilha de onboarding e o que está errado.
- Doc 👤 (README, CHANGELOG) tem tom humano; histórico (ADRs, ciclos) não se
  reescreve.
- Documento novo só entra se responder uma pergunta que nenhum outro responde:
  a trilha liga, não copia.

## Próximo depois desta

S22b — README e site com banner, badges e screenshots.
