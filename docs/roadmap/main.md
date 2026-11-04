# Roadmap atual

Ciclo ativo: **0004 — Execução e robustez**. O ciclo anterior está em
[`0003-qualidade.md`](0003-qualidade.md).

## Fase 1 — Feedback de execução

Objetivo: manter a janela responsiva e mostrar o andamento em execuções longas.

- [x] **S5a — Execução fora da UI thread e barra de progresso.** Handler em
  segundo plano, barra e contador por arquivo, entrada bloqueada. Ver ADR 0011.
- [x] **S5b — Log ao vivo e cancelamento.** Log por arquivo durante a execução,
  botão “Cancelar” e parada cooperativa entre arquivos, sem gravar o parcial.
  Ver adendo do ADR 0011.

## Fase 2 — Robustez das ferramentas

Objetivo: reduzir falhas em texto sujo e ampliar o recorte sem mudar o
comportamento atual.

- [x] **S5c — Extração de CNJ em texto sujo.** Normaliza espaços, quebras,
  travessões e invisíveis, aceita separadores flexíveis e mantém a rejeição a
  CPF e números maiores. Extrai mesmo com dígito verificador inválido. Ver
  ADR 0012.
- [x] **S5d — Recorte por quantidade de arquivos.** Alterna entre linhas por
  arquivo e quantidade de arquivos; a quantidade vale **por aba**, com blocos
  equilibrados e redução quando passa do total de linhas.

## Backlog

| Item | Valor | Custo | Pré-requisito |
|---|---|---|---|
| Tema claro opcional | Baixo | M | tokenizar as cores |
| Histórico de execuções | Médio | M | S5a e S5b |

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

- A S5a deixou a fila de progresso pronta; a S5b reusa o mesmo caminho para log
  ao vivo e cancelamento entre arquivos.
- A S5b manteve o cancelamento cooperativo: a chamada do controller em curso
  termina antes da parada, e o parcial não libera salvar.
- A S5c saneia só a cópia usada na busca; o texto da planilha continua intacto.
  Dígito verificador inválido não descarta o CNJ (ADR 0012).
- A S5d fechou a Fase 2: o recorte tem dois modos, e a quantidade de arquivos é
  aplicada separadamente a cada aba.
- A S4c fechou o ciclo 0003; o resumo está em
  [`0003-qualidade.md`](0003-qualidade.md).
- O template de spec foi versionado e o `docs:check` voltou a passar no CI.
- Tema claro teve o custo reavaliado para M: as cores são constantes importadas
  por todos os componentes.
- Histórico de execuções fica para depois da infraestrutura de execução (S5a e
  S5b).
