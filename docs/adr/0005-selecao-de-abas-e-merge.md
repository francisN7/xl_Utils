# ADR 0005 — Seleção de abas e mesclagem com origem

- **Status:** aceita
- **Data:** 2026-11-04

## Contexto

Os scripts originais liam só a primeira aba. Com a UI, o usuário precisa
escolher quais abas entram em cada ferramenta. O `merge` antigo tinha dois modos
(“primeira aba de cada arquivo” e “todas as abas de uma planilha”), o que fica
ambíguo quando há vários arquivos e seleção de abas. Também é preciso
diferenciar linhas duplicadas vindas de origens diferentes e permitir alinhar
colunas de mesmo significado que chegam com nomes diferentes.

## Decisão

- Um componente único de **seleção de abas** entra no card de entrada de todas
  as ferramentas: chips pequenos, agrupados por arquivo quando houver vários,
  com “Todas” e “Limpar” e contador de selecionadas.
- Padrão: um arquivo seleciona todas as abas; vários arquivos selecionam a
  primeira aba de cada um. O usuário pode mudar antes de executar.
- A seleção vive em `ToolState`, por arquivo.
- `all_str` lê e salva somente as abas selecionadas, **preservando os nomes**.
- `cnj` procura somente nas abas selecionadas; a saída continua uma lista
  `PROCESSOS`.
- `cut` recorta somente as abas selecionadas; o nome do arquivo de saída segue
  a quantidade de abas processadas.
- `merge` passa a ter **um único modo**: concatena as abas selecionadas de todos
  os arquivos selecionados, na ordem de arquivos e abas. O dropdown de modo
  deixa de existir.
- A mesclagem acrescenta uma coluna `ORIGEM` no formato
  `arquivo - aba - linha`, para distinguir duplicidades.
- O alinhamento manual de colunas é desejável: o usuário indica quais colunas
  de origens diferentes ocupam a mesma coluna no resultado. A S1e decide se
  isso será por arrastar ou por seleção/dropdown, conforme o suporte do Flet.

## Consequências

- A mesma seleção serve para todas as ferramentas e evita regras divergentes.
- O merge fica mais simples de explicar: o que está marcado é o que entra.
- `all_str` e `cut` precisam carregar a seleção no controller e filtrar depois
  do `prepare_workbook`.
- `cnj` e `cut` mudam de comportamento em relação ao script antigo, que só lia
  a primeira aba.
- A coluna `ORIGEM` aumenta a largura da saída; fica documentada na prévia.
- O alinhamento manual pode exigir uma etapa própria na UI antes de executar.

## Alternativas

- **Manter os dois modos de merge:** mantém a ambiguidade com vários arquivos e
  seleção de abas; rejeitado.
- **Ler sempre só a primeira aba:** simples, mas ignora o pedido de seleção;
  rejeitado.
- **Só concatenar com os mesmos nomes de coluna:** perde dados quando os
  cabeçalhos variam; o alinhamento manual cobre esse caso.
- **Sem coluna de origem:** duplicidades de arquivos diferentes ficam
  indistinguíveis; rejeitado.

## Adendo — S1e (2026-11-04)

- O alinhamento é por **um dropdown por coluna distinta**, não por arrastar: o
  Flet 1.0 não oferece drag de colunas.
- Colunas com o mesmo nome já nascem alinhadas; para unir nomes diferentes, o
  usuário escolhe a mesma coluna canônica nos dois dropdowns.
- O mapa vive em `ToolState.options` e é recalculado quando os arquivos ou as
  abas mudam; a lista de colunas vem de `core/io.read_headers`, que não carrega
  as linhas para Excel e CSV.
- `ORIGEM` é a primeira coluna, no formato `<arquivo> - <aba> - <linha>`. Uma
  coluna de origem que já se chame `ORIGEM` é renomeada para `ORIGEM_original`.
- Execução com uma única aba útil é recusada com mensagem clara, antes de
  gravar qualquer arquivo.
