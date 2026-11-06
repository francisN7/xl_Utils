# Polimento — o que foi entregue (2026-11-06)

Ciclo 0005 fechado. O detalhe completo está no Git; as decisões ficam nos ADRs.
O ciclo anterior está em [`0004-execucao-e-robustez.md`](0004-execucao-e-robustez.md);
o próximo começa em [`main.md`](main.md).

| Sessão | Entrega | Aceite |
|---|---|---|
| S6a | `ORIGEM` = `<stem> - <aba>` e `LINHA_ORIGEM` numerando o resultado inteiro com zeros à esquerda | origem e posição legíveis após a mesclagem |
| S6b | leitura, planilha carregada e cálculo no log ao vivo; barra indeterminada por arquivo | quatro ferramentas mostram a etapa e avançam ao concluir cada arquivo |
| S6c | paletas escura/clara, preferência em `settings.json` e botão na sidebar com aviso de reabertura | tema salvo sobrevive ao fechamento; settings inválido cai no escuro |

**Resultado do ciclo:** execução visível nas quatro ferramentas e leitura
confortável em ambiente claro, sem mudar layout, fluxo ou regra de negócio.

## Decisões do ciclo

- [ADR 0005](../adr/0005-selecao-de-abas-e-merge.md) — adendo de `ORIGEM` e
  `LINHA_ORIGEM`.
- [ADR 0011](../adr/0011-execucao-fora-da-ui.md) — adendo de log por etapa.
- [ADR 0013](../adr/0013-tema-claro-e-preferencia.md) — tema claro e
  preferência salva.

## Backlog que seguiu para o ciclo 0006

- Vinculação entre AGENDA, CLIENTES, FINANCEIRO e PROCESSOS.
- Alinhamento de colunas em tela cheia na mesclagem.
- Envio direto do Google Drive, com OAuth e múltiplas contas.

Nenhum tinha sessão marcada ao fechar o ciclo; a prioridade fica com o dono.

## Validação de fechamento

`uv run ruff check src tests`, `uv run ruff format --check src tests`,
`uv run pytest` e `node scripts/check-docs.mjs` verdes antes do fechamento.
Smoke visual feito no app web: Início e Tratamento de Texto nos dois temas; o
botão da sidebar gravou `light` em `settings.json` e mostrou o aviso de
reabertura.
