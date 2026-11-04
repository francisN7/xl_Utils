# ADR 0012 — CNJ em texto sujo e dígito verificador

- **Status:** aceita
- **Data:** 2026-11-04

## Contexto

A extração reconhecia só o formato pontuado exato e a sequência de 20 dígitos.
Nas planilhas reais, o mesmo número aparece com espaços, quebras de linha,
travessões, barras e caracteres invisíveis colados durante a cópia; esses casos
eram descartados. Havia também uma decisão de produto: um CNJ com dígito
verificador inválido pode ser o único registro disponível, e descartá-lo perde
o processo.

## Decisão

- A busca usa uma cópia saneada do texto: remove invisíveis (zero-width, BOM),
  troca espaços não separáveis por espaço e uniformiza os travessões. O texto da
  planilha não é alterado.
- O padrão aceita separadores flexíveis entre os blocos (ponto, barra, hífen,
  espaço, travessão e quebra), desde que o total seja exatamente 20 dígitos.
- Os lookarounds continuam impedindo match dentro de número maior; CPF e
  sequência de 21 dígitos seguidos ficam de fora.
- O dígito verificador **não** é validado: o valor é extraído e padronizado
  mesmo se o cálculo falhar.
- `normalize_cnj` também aceita a forma suja e devolve o formato pontuado; o
  controller, a coluna `PROCESSOS` e o log não mudam.

## Consequências

- Células copiadas de PDF, e-mail ou sistema antigo passam a gerar resultados.
- Um número de 20 dígitos que não seja CNJ pode entrar como falso positivo; o
  usuário confere a lista antes de salvar.
- A contagem de achados, únicos e duplicados continua igual, agora incluindo os
  valores recuperados.
- A decisão de não validar o dígito é comportamental e não deve ser "corrigida"
  sem uma decisão nova do dono.

## Alternativas

- **Validar o dígito verificador:** reduziria falsos positivos, mas descartaria
  processos reais com erro de digitação; rejeitada.
- **Remover todo não dígito da célula e procurar 20 dígitos:** capturaria
  sequências formadas por números vizinhos e perderia os limites; rejeitada.
- **Exigir a pontuação exata:** era o comportamento anterior e perdia os casos
  de texto sujo; rejeitada.
