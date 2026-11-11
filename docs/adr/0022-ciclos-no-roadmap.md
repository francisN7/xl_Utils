# ADR 0022 — Ciclos fechados voltam ao roadmap

- **Status:** aceita
- **Data:** 2026-11-11

## Contexto

O ADR 0020 criou `docs/history/` para separar os ciclos fechados do roadmap
ativo. Na prática, a pasta virou um destino único para assuntos diferentes: o
índice de ciclos, o processo do roadmap e o `main.md` ficaram em pastas
distintas, e quem procurava o passado precisava saber que ele mudou de lugar.
O ganho de contexto curto já era garantido pelo `CURRENT.md` e pela spec da
sessão; o custo de navegação não se pagou.

## Decisão

- **Ciclo fechado fica em `docs/roadmap/NNNN-titulo.md`**, ao lado do
  `main.md`. O `roadmap/README.md` é o índice dos ciclos e do processo.
- **A pasta `docs/history/` deixa de existir.** O conteúdo volta para
  `roadmap/` sem reescrever o texto das páginas.
- **Spec continua temporária:** vive em `docs/sessions/` enquanto a sessão está
  aberta e sai do working tree no fechamento do ciclo. O Git guarda o texto.
- **Nada comprimido no repositório**, como no ADR 0020.
- **O check de docs volta a conferir os links das páginas de ciclo**, agora que
  elas estão em `roadmap/`; só CHANGELOG, specs e corpo de ADR ficam fora.

## Consequências

- Um único lugar responde "qual é o ciclo atual" e "o que já fechou":
  `docs/roadmap/`.
- Os links relativos das páginas de ciclo continuam válidos em `roadmap/`
  (`../adr/`, `../guide/`, `main.md` e as páginas irmãs).
- O working tree não cresce no fechamento: a página do ciclo substitui o
  `main.md`, e as specs saem.
- Custos: `roadmap/` volta a misturar futuro e passado; o `README.md` precisa
  deixar claro o que é ativo e o que é histórico.

## Alternativas

- **Manter `docs/history/`:** preservava a separação física, mas repetia o custo
  de navegação que motivou esta reversão. Descartada.
- **Arquivar por sessão:** multiplicaria arquivos e contrariaria o orçamento de
  contexto. Descartada.
- **Só o Git, sem página de ciclo:** o resumo passaria a depender de ler diffs;
  a página numerada continua sendo o índice barato do passado. Descartada.
