# Roadmap

Status: `[ ]` pendente · `[~]` em andamento · `[x]` concluída.

## Como funciona

- **Ciclo** agrupa sessões com o mesmo tema e termina numa página de histórico.
- **Sessão** é uma entrega vertical + testes + docs + commit. Só nasce quando o
  ciclo é escolhido; a spec é escrita no fim da anterior.
- **Ordem** é definida pelo dono. Sem prioridade declarada, o agente pergunta.
- **Passado** não mora aqui: ciclo fechado vira página em
  [`../history/`](../history/README.md).

## Artefatos

| Arquivo | Estado | O que é |
|---|---|---|
| [`main.md`](main.md) | **ativo** | ciclo atual e backlog |
| [`../history/README.md`](../history/README.md) | índice | ciclos fechados, um `NNNN-titulo.md` cada |

## Convenção de nomes

- `main.md` é sempre o roadmap ativo; é o único que muda no dia a dia.
- Quando um ciclo fecha, `main.md` vira `../history/NNNN-titulo.md` (quatro
  dígitos, ordem de fechamento) e um novo `main.md` começa.
- Este `README.md` explica o processo; não guarda fases nem ciclos.

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
- spec da sessão fora do working tree no fim do ciclo;
- commit `SXX: resumo curto`.

## Numeração

- Sessão dentro da mesma fase usa letra: `S0a`, `S0b`, `S1a`.
- Ciclos fechados ganham quatro dígitos no arquivo: `0006-backlog.md`.
