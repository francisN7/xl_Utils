# Roadmap

Status: `[ ]` pendente · `[~]` em andamento · `[x]` concluída.

## Como funciona

- **Fase** agrupa sessões com o mesmo tema.
- **Sessão** é uma entrega vertical + testes + docs + commit. Só nasce quando a
  fase é escolhida; a spec é escrita no fim da anterior.
- **Ordem** é definida pelo dono. Sem prioridade declarada, o agente pergunta.

## Artefatos

| Arquivo | Estado | O que é |
|---|---|---|
| [`main.md`](main.md) | **ativo** | backlog à espera de um novo ciclo |
| [`0003-qualidade.md`](0003-qualidade.md) | fechado | histórico do ciclo de qualidade e clareza |
| [`0002-migracao.md`](0002-migracao.md) | fechado | histórico do ciclo de migração e publicação |
| [`0001-fundacao.md`](0001-fundacao.md) | fechado | histórico do ciclo da fundação |

## Ciclos fechados

| Arquivo | Ciclo | Fechado em |
|---|---|---|
| [`0001-fundacao.md`](0001-fundacao.md) | Fundação | 2026-11-04 |
| [`0002-migracao.md`](0002-migracao.md) | Migração e publicação | 2026-11-04 |
| [`0003-qualidade.md`](0003-qualidade.md) | Qualidade e clareza | 2026-11-04 |

## Convenção de nomes

- `main.md` é sempre o roadmap ativo; é o único que muda no dia a dia.
- Quando um ciclo fecha, `main.md` vira `NNNN-titulo.md` (quatro dígitos, ordem
  cronológica) e um novo `main.md` começa.
- Este `README.md` é o índice; não guarda fases.

## Definition of Ready (de uma spec)

1. Objetivo em uma frase observável.
2. Fora de escopo explícito.
3. Tarefas numeradas.
4. Critérios de aceite verificáveis.
5. Orçamento de contexto (arquivos e limite de linhas).
6. Riscos e como detectar cedo.

## Definition of Done

- lint, testes e docs verdes;
- funciona no ambiente alvo;
- docs, `CURRENT.md`, roadmap e `CHANGELOG.md` atualizados;
- commit `SXX: resumo curto`.

## Numeração

- Sessão dentro da mesma fase usa letra: `S0a`, `S0b`, `S1a`.
- Fases/ciclos fechados ganham quatro dígitos no arquivo: `0001-fundacao.md`.
