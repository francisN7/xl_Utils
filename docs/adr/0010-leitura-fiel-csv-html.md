# ADR 0010 — Leitura fiel de CSV e HTML

- **Status:** aceita
- **Data:** 2026-11-04

## Contexto

A promessa do pipeline é preservar texto, zeros à esquerda, CNJ/CPF e `NA`. Três
falsos sucessos do pandas quebravam essa promessa sem levantar erro:

- CSV exportado pelo Excel em pt-BR usa `;`; com a vírgula padrão, a linha
  inteira virava uma coluna e os decimais (`1,50`) quebravam;
- `keep_default_na=True` transformava `NA`, `N/A`, `NULL` e `None` em vazio,
  inclusive no Excel lido com `dtype=str`;
- HTML com cabeçalho de dois níveis (`colspan`) não aplicava os converters,
  porque as chaves eram texto e as colunas eram tuplas: `000123` virava `123`.

Reparo só era tentado quando a leitura falhava. Nos três casos acima ela
“funcionava” e produzia dado errado.

## Decisão

- O CSV é lido com **encoding e separador detectados** antes da leitura
  principal: amostra de 64 KB, `utf-8-sig` → `cp1252` → `latin-1`, e
  `csv.Sniffer` restrito a `,`, `;`, tab e `|`. Se a leitura rápida falhar, o
  motor Python infere o separador linha a linha.
- Toda leitura usa `keep_default_na=False`: `NA`, `N/A`, `NULL` e `None` são
  texto; célula vazia vira `""`.
- O HTML é lido em duas passadas; os converters usam as **chaves reais** das
  colunas (tuplas quando há dois níveis) e o cabeçalho é achatado depois
  (`Grupo - cod`), com desempate `_2` para nomes repetidos.
- `.xlsx`/`.xlsm` e `.htm`/`.html` são famílias equivalentes e não contam como
  divergência de formato.
- O cabeçalho de CSV é lido por amostra, não pelo arquivo inteiro.

## Consequências

- CSV do Excel pt-BR, CSV com tab/pipe e HTML com `colspan` passam a produzir o
  resultado esperado, com teste em `tests/test_formats.py`.
- Células vazias deixam de ser `NaN` na leitura; quem precisar de ausência usa a
  regra da ferramenta (o merge continua preenchendo lacunas com `pd.NA`).
- A leitura de CSV fica um pouco mais cara por causa da amostra; em troca, não
  há mais corrupção silenciosa.
- O `.xls` continua sem leitor alternativo; ver o adendo do ADR 0004.

## Alternativas

- **Usar `sep=None, engine="python"` sempre:** funciona, mas é mais lento em
  arquivo grande; a amostra com o motor C cobre o caso comum.
- **Confiar na extensão `.csv` e na vírgula:** foi a causa do bug; rejeitado.
- **Deixar `NA` virar vazio:** perde texto e contradiz o `dtype=str`; rejeitado.
- **Converter o HTML inteiro com `astype(str)`:** perde o texto original de
  números (`1,50` vira `1.5`); rejeitado em favor de converters.
