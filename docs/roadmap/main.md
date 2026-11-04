# Roadmap atual

Nenhum ciclo ativo. O ciclo 0003 está fechado em
[`0003-qualidade.md`](0003-qualidade.md).

O backlog abaixo aguarda mais feedback do dono; um item só vira sessão quando um
novo ciclo e uma fase forem escolhidos.

## Backlog

| Item | Valor | Custo | Pré-requisito |
|---|---|---|---|
| Tema claro opcional | Baixo | S | — |
| Histórico de execuções | Médio | M | S2b |
| Cancelar execução em andamento | Médio | M | S1a |

## Manutenção

- Rodar `uv lock --upgrade` a cada ciclo e validar pandas/Flet — critério:
  testes verdes e app abrindo.
- Revisar `docs:check` no CI a cada mudança de documentação.
- Atualizar o code tour quando um módulo do core mudar de papel.

## Gatilhos (não são backlog)

- Suporte a macOS/Linux — só entra quando houver máquina para testar.
- Empacotamento, instalador e release — só entram quando o dono decidir
  distribuir.
- Internacionalização — só entra se aparecer usuário fora do PT-BR.
- Drag & drop real de arquivos — só entra se migrar para PySide6 ou houver hook
  Windows-only.

## Descartados (não voltam sem decisão nova)

- CLI com `click` — a branch `cli-app` foi apagada; ver ADR 0001.
- `demoji` — incompatível com Python 3.15 e API removida; ver ADR 0001.
- Ferramentas `convert` (JSON → planilha) e `quick_replace` (substituir
  nomes) — saem sem substituto, conforme decisão do dono.
- Página própria de `remove_emoji` — a remoção de emojis entra no pipeline do
  `all_str`; ver ADR 0004.
- Renomear o arquivo original do usuário para “corrigir” extensão — proibido
  por design; a leitura usa o tipo real sem tocar no arquivo.
- Normalizar quebras de linha automaticamente — rejeitado; preservar o texto.

## Notas do ciclo

- A S4a (fechamento do ciclo 0002) foi absorvida pela S4b; o resumo do ciclo
  está em [`0002-migracao.md`](0002-migracao.md).
- O ciclo 0003 fechou com a S4c; o resumo está em
  [`0003-qualidade.md`](0003-qualidade.md).
