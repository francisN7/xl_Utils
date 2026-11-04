# ADR 0004 — Leitura segura e limpeza de texto compartilhada

- **Status:** aceita
- **Data:** 2026-11-04

## Contexto

Cada script lia a planilha do seu jeito. Alguns usavam `dtype=str`, outros
deixavam o pandas inferir tipos; números viravam notação científica e zeros à
esquerda desapareciam. O `all_str` já fazia a conversão para texto, mas só
quando chamado sozinho. A remoção de emojis era uma ferramenta separada e o
`demoji` não funciona no Python 3.15.

## Decisão

- Todo arquivo é lido por **`all_str.prepare_workbook`**, sempre antes da regra
  da ferramenta.
- A leitura usa **`dtype=str`** e preserva o texto da célula, **inclusive
  quebras de linha**.
- A **remoção de emojis** (`emoji.replace_emoji`) entra nesse mesmo pipeline.
- O `all_str` continua existindo como ferramenta própria para conversão e
  reparo explícitos, agora também responsável pelos emojis.
- Nada de converter `_x000D_`/`_x000A_` automaticamente: o conteúdo é mantido
  como está.
- Reparo de arquivo corrompido é tentado só quando a leitura falha, sem
  `shell=True`.

## Consequências

- Dados sensíveis a formato (CNJ, CPF, códigos com zero) sobrevivem.
- Toda saída tende a ser texto; isso é intencional neste domínio.
- A ferramenta de texto deixa de ser opcional: é a porta de entrada de todas.
- O `remove_emoji` deixa de existir como página; emojis são removidos no
  pipeline e podem ser reconferidos no `all_str`.
- Sem normalização de quebra de linha, o conteúdo fica mais fiel ao original.

## Alternativas

- **Cada ferramenta lê como quiser:** mantém a duplicação e a perda de dados.
- **Normalizar quebras de linha:** rejeitado pelo dono; pode alterar conteúdo.
- **Manter `remove_emoji` separado:** duplica o pipeline e aumenta a superfície.
- **Continuar com `demoji`:** incompatível com 3.15 e com API removida.
- **Forçar tudo para numérico:** pior para CNJ/CPF e códigos com zero.

## Adendo — reparo tipado (S1a)

O reparo não converte mais para CSV via `xlsx2csv`. Quando a leitura normal
falha, `prepare_workbook` tenta **um** leitor tolerante conforme o formato real
(`openpyxl` somente leitura, codificações alternativas para CSV, outro parser
para HTML). Se o fallback também falhar, levanta `WorkbookReadError` com a causa
original; a página mostra a mensagem e o arquivo do usuário fica intacto.

## Adendo — `.xls` sem reparo (S4b)

O calamine é o único leitor de `.xls` do projeto. Repetir a mesma chamada não
configura reparo e escondia a causa original; o formato agora falha direto com
`WorkbookReadError` e uma mensagem que diz que não há leitor alternativo.

