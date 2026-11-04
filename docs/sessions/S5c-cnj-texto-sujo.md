# S5c — Extração de CNJ em texto sujo

## Objetivo

Extrair CNJs de células com espaços, quebras, travessões e caracteres
invisíveis, aceitando separadores flexíveis sem confundir CPF nem número maior.

## Fora de escopo

Validar dígito verificador (decisão: extrair mesmo inválido), mudar o formato
pontuado da saída, normalizar o texto da planilha, alterar a página ou o log.

## Tarefas

1. Criar no core uma normalização específica da extração: remover caracteres
   invisíveis (zero-width, BOM), trocar NBSP por espaço e colapsar espaços e
   quebras entre os blocos do número.
2. Ajustar a regex para aceitar separadores flexíveis entre os blocos (ponto,
   barra, hífen, espaço e travessão), mantendo os lookarounds que impedem match
   dentro de número maior.
3. Manter os limites: exatamente 20 dígitos no total, CPF de 11 dígitos fora e
   nenhuma sequência de 21 ou mais dígitos aceita.
4. Preservar `normalize_cnj`, `summarize_cnjs` em uma passada, o controller e a
   saída `PROCESSOS`; o log continua contando achados, únicos e duplicados.
5. Cobrir os casos sujos em `tests/test_cnj.py` e confirmar a integração nos
   quatro formatos.

## Aceite

- [ ] CNJ separado por espaço, travessão ou quebra de linha é extraído e
      padronizado
- [ ] caracteres invisíveis não impedem o match
- [ ] CPF, sequência de 21 dígitos e trecho dentro de número maior continuam
      rejeitados
- [ ] dígito verificador inválido é extraído, não descartado
- [ ] `ruff`, `ruff format --check`, `pytest` e `docs:check` verdes

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec, `core/tools/cnj.py`,
`tests/test_cnj.py`, `controllers/cnj.py` e a seção “Extração de CNJ” de
`reference/architecture.md`. Abrir a página só se a mensagem exibida mudar.

## Arquivos prováveis

- `src/xl_utils/core/tools/cnj.py`
- `tests/test_cnj.py`, `tests/test_integration.py`
- `docs/reference/architecture.md` (seção “Extração de CNJ”)
- `docs/adr/0004-leitura-segura-e-emojis.md` (só consulta)

## Riscos

- Separador flexível demais pode capturar CPF formatado com espaços; testar os
  limites antes de afrouxar a regex.
- Colapsar espaços não pode alterar a posição dos demais caracteres usados nos
  lookarounds; normalizar só a cópia usada na busca.
- `normalize_cnj` deve continuar rejeitando valor inválido fora da extração.
- Texto com dois CNJs colados precisa continuar devolvendo dois achados.

## Próximo depois desta

Fase 2 — S5d, recorte por quantidade de arquivos.
