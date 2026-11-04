# S4a — Fechar o ciclo 0002 e abrir a Fase 4

## Objetivo

Encerrar o ciclo 0002 (Migração + Publicação) com um roadmap numerado e abrir
a Fase 4 com a primeira sessão escolhida pelo dono.

## Fora de escopo

Executar a primeira sessão da Fase 4; empacotamento, instalador ou release;
mexer no código da `main` ou na `legacy`.

## Tarefas

1. Conferir o aceite da S3b: tag `legacy-v1`, rulesets ativos e README da
   `main` apontando para a branch e a tag.
2. Revisar o backlog vigente (`histórico de execuções`, `cancelar execução em
   andamento`, `tema claro opcional`) e perguntar ao dono qual item abre a
   Fase 4. Sem resposta, parar e registrar a pendência em `CURRENT.md`.
3. Renomear `docs/roadmap/main.md` para `docs/roadmap/0002-migracao.md` e
   resumir o ciclo: tabela S1a–S3b, resultado, decisões (ADRs 0004–0009) e
   validação final. Não copiar diffs nem medições antigas.
4. Criar um novo `docs/roadmap/main.md` para a Fase 4 com o objetivo escolhido,
   as sessões previstas, o backlog restante, a manutenção e os gatilhos.
5. Atualizar `docs/roadmap/README.md`: `0002-migracao.md` entra em “Ciclos
   fechados” e o novo `main.md` fica ativo.
6. Escrever a spec da primeira sessão da Fase 4 a partir de
   `docs/sessions/_TEMPLATE.md` (≤90 linhas, com orçamento de contexto).
7. Remover do working tree as specs do ciclo fechado (`S2b` a `S3b`); o Git
   guarda o histórico e o resumo fica no roadmap numerado.
8. Rodar `ruff`, `pytest` e `docs:check`, atualizar `CURRENT.md` e o
   `CHANGELOG.md`, e commitar com `S4a: ...`.

## Aceite

- [ ] `docs/roadmap/0002-migracao.md` resume o ciclo e cita os ADRs
- [ ] novo `main.md` ativo com Fase 4 definida pelo dono
- [ ] índice do roadmap com o ciclo 0002 em “fechados”
- [ ] spec da primeira sessão da Fase 4 pronta e dentro de 90 linhas
- [ ] specs do ciclo 0002 fora do working tree
- [ ] `ruff`, `pytest` e `docs:check` verdes

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec, `docs/roadmap/main.md`,
`docs/roadmap/README.md` e as primeiras linhas de `CHANGELOG.md`. Não abrir
código-fonte.

## Arquivos prováveis

- `docs/roadmap/main.md`, `docs/roadmap/0002-migracao.md`,
  `docs/roadmap/README.md`
- `docs/sessions/` (remover specs do ciclo 0002 e criar a próxima)
- `docs/state/CURRENT.md`, `CHANGELOG.md`

## Riscos

- Perder o backlog ao reescrever o roadmap; copiar a tabela e os gatilhos para o
  novo `main.md` antes de renomear.
- Ciclo fechado sem decisão do dono vira fase inventada; nesse caso registrar a
  pergunta em `CURRENT.md` e não avançar.
- Remover specs sem o resumo no roadmap apaga contexto útil; escrever o resumo
  primeiro.
- Renomear o roadmap quebra links relativos; rodar `docs:check` depois e corrigir
  as referências em `docs/README.md`.

## Próximo depois desta

Primeira sessão da Fase 4, definida na etapa 2.
