# Roadmap

Status: `[ ]` pendente · `[~]` em andamento · `[x]` concluída.

## Como funciona

- **Ciclo** agrupa sessões com o mesmo tema e termina numa página numerada.
- **Sessão** é uma entrega vertical + testes + docs + commit. Só nasce quando o
  ciclo é escolhido; a spec é escrita no fim da anterior.
- **Ordem** é definida pelo dono. Sem prioridade declarada, o agente pergunta.
- **Passado** mora aqui mesmo: ciclo fechado vira `NNNN-titulo.md`, ao lado do
  `main.md`.

## Artefatos

| Arquivo | Estado | O que é |
|---|---|---|
| [`main.md`](main.md) | **ativo** | ciclo atual e backlog |
| [`0001-fundacao.md`](0001-fundacao.md) | fechado | fundação do app |
| [`0002-migracao.md`](0002-migracao.md) | fechado | migração e publicação |
| [`0003-qualidade.md`](0003-qualidade.md) | fechado | qualidade e clareza |
| [`0004-execucao-e-robustez.md`](0004-execucao-e-robustez.md) | fechado | execução e robustez |
| [`0005-polimento.md`](0005-polimento.md) | fechado | polimento |
| [`0006-backlog.md`](0006-backlog.md) | fechado | vinculação, tela cheia e Drive |
| [`0007-versoes-e-distribuicao.md`](0007-versoes-e-distribuicao.md) | fechado | versão e distribuição |
| [`0008-plugins.md`](0008-plugins.md) | fechado | plugins |

## Ciclos fechados

| Arquivo | Ciclo | Fechado em |
|---|---|---|
| [`0001-fundacao.md`](0001-fundacao.md) | Fundação | 2026-11-04 |
| [`0002-migracao.md`](0002-migracao.md) | Migração e publicação | 2026-11-04 |
| [`0003-qualidade.md`](0003-qualidade.md) | Qualidade e clareza | 2026-11-04 |
| [`0004-execucao-e-robustez.md`](0004-execucao-e-robustez.md) | Execução e robustez | 2026-11-04 |
| [`0005-polimento.md`](0005-polimento.md) | Polimento | 2026-11-06 |
| [`0006-backlog.md`](0006-backlog.md) | Backlog | 2026-11-08 |
| [`0007-versoes-e-distribuicao.md`](0007-versoes-e-distribuicao.md) | Versão e distribuição | 2026-11-09 |
| [`0008-plugins.md`](0008-plugins.md) | Plugins | 2026-11-11 |

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
- spec da sessão fora do working tree no fim do ciclo;
- commit `SXX: resumo curto`.

## Numeração

- Sessão dentro da mesma fase usa letra: `S0a`, `S0b`, `S1a`.
- Ciclos fechados ganham quatro dígitos no arquivo: `0007-versoes-e-distribuicao.md`.
