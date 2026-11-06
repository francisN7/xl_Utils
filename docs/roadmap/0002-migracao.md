# Migração e publicação — o que foi entregue (2026-11-04)

Ciclo 0002 fechado. O detalhe completo está no Git; as decisões ficam nos ADRs.
O fechamento administrativo previsto para a S4a foi absorvido pela S4b.

| Sessão | Entrega | Aceite |
|---|---|---|
| S1a | `all_str` como pipeline único de texto + emojis, sem `xlsx2csv` | leitura segura e `WorkbookReadError` |
| S1b | Extração de CNJ com regex, padronização e deduplicação | lista única e ordenada |
| S1c | Recorte por quantidade de linhas, com prévia | partes sequenciais e resto no último bloco |
| S1d | Seleção de abas por arquivo, com “Todas”/“Limpar” | abas escolhidas preservadas na saída |
| S1e | Merge em um modo, com `ORIGEM` e colunas arrastáveis | concatenação sem perder linhas |
| S2a | Integração nos quatro formatos, incluindo `.xls` | fixture fictícia e origens imutáveis |
| S2b | Log estruturado e diagnóstico copiável | erro tipado na UI e traceback no diagnóstico |
| S2c | Opções reais ou nada | card “2. Opções” só quando há o que editar |
| S2d | Tipo real × extensão | `FormatCheck` bloqueia o que não é planilha |
| S2e | Saída escolhida | nada gravado antes da escolha; lote em pasta |
| S3a | UI promovida a `main`; branch `legacy` criada | README e histórico publicados |
| S3b | `legacy` travada no GitHub | tag `legacy-v1` e rulesets ativos |

**Resultado do ciclo:** quatro ferramentas migradas para core + controller +
página, leitura segura em `.xlsx`/`.xls`/`.csv`/`.html`, seleção de abas, lote,
log/diagnóstico, saída escolhida e `main` publicada com a `legacy` preservada.

## Decisões do ciclo

- [ADR 0004](../adr/0004-leitura-segura-e-emojis.md) — leitura segura e emojis.
- [ADR 0005](../adr/0005-selecao-de-abas-e-merge.md) — seleção de abas e merge.
- [ADR 0006](../adr/0006-lote-de-arquivos.md) — lote de arquivos.
- [ADR 0007](../adr/0007-log-e-diagnostico.md) — log estruturado e diagnóstico.
- [ADR 0008](../adr/0008-saida-escolhida.md) — saída depois da prévia.
- [ADR 0009](../adr/0009-publicacao-main-legacy.md) — `main` com UI e `legacy`.

## Validação de fechamento

`uv run ruff check src tests`, `uv run pytest` e `node scripts/check-docs.mjs`
verdes antes do fechamento. O ciclo seguinte começa em
[`0003-qualidade.md`](0003-qualidade.md).
