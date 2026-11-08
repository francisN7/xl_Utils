# Execução e robustez — o que foi entregue (2026-11-04)

Ciclo 0004 fechado. O detalhe completo está no Git; as decisões ficam nos ADRs.
O ciclo anterior está em [`0003-qualidade.md`](0003-qualidade.md); o tema claro
seguiu para o [ciclo 0005](0005-polimento.md).

| Sessão | Entrega | Aceite |
|---|---|---|
| S5a | Execução fora da UI thread: handler em segundo plano, barra e contador por arquivo, entrada bloqueada | janela responsiva durante o lote e progresso por arquivo |
| S5b | Log ao vivo e cancelamento cooperativo entre arquivos, sem gravar parcial | execução cancelável entre arquivos; parcial não libera salvar |
| S5c | Extração de CNJ em texto sujo, com separadores flexíveis; dígito verificador inválido não descarta | CNJ extraído de texto sujo; CPF e números maiores seguem rejeitados |
| S5d | Recorte por quantidade de arquivos, aplicado por aba, com blocos equilibrados | dois modos de recorte; quantidade limitada ao total de linhas |

**Resultado do ciclo:** execução responsiva e cancelável, log ao vivo, extração
de CNJ tolerante a texto sujo e recorte por quantidade de arquivos por aba.

## Decisões do ciclo

- [ADR 0011](../adr/0011-execucao-fora-da-ui.md) — execução fora da UI thread.
- [ADR 0012](../adr/0012-cnj-texto-sujo.md) — CNJ em texto sujo.

## Validação de fechamento

`uv run ruff check src tests`, `uv run pytest` e `node scripts/check-docs.mjs`
verdes antes do fechamento. O ciclo seguinte começa em
[`0005-polimento.md`](0005-polimento.md); o ativo, em
[`main.md`](../roadmap/main.md).
