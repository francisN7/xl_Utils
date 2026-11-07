# S7c — Vinculação II: FINANCEIRO, CLIENTES e opções

## Objetivo

Acrescentar FINANCEIRO e CLIENTES à vinculação, com dois fluxos independentes
(AGENDA e/ou FINANCEIRO) e as duas opções: nome sem vínculo na descrição e
manter apenas um campo vinculante.

## Fora de escopo

- Popular CLIENTES ou PROCESSOS; eles são só fontes de consulta.
- Normalizar nome, CNJ, PASTA ou PROTOCOLO; continua tudo bruto.
- Google Drive e tela cheia.

## Fluxos

- A página tem quatro entradas rotuladas: AGENDA, PROCESSOS, FINANCEIRO e
  CLIENTES. Não há checkbox de fluxo: a presença do arquivo define o fluxo.
- AGENDA anexada exige PROCESSOS. FINANCEIRO anexado exige PROCESSOS ou
  CLIENTES. Pelo menos um dos dois (AGENDA/FINANCEIRO) precisa estar anexado.
- Com AGENDA sem PROCESSOS, nada roda, mesmo que o FINANCEIRO tenha CLIENTES.
- Um fluxo gera uma saída; dois fluxos geram duas saídas.

## Regras

1. AGENDA: mantém a regra da S7a (CNJ → PASTA → PROTOCOLO, `VINCULA?`,
   `MIGRAÇÃO`, protocolo na descrição quando não vincula). `MIGRAÇÃO` nunca é
   comparada; em linha vinculada, a sentinela é limpa.
2. FINANCEIRO com PROCESSOS: `VINCULA?` na mesma prioridade e
   `VINCULA (POR NOME)?` SIM/NÃO. Os nomes vêm de PROCESSOS (split cru por `;`)
   e de CLIENTES; o nome do FINANCEIRO é comparado como está.
3. FINANCEIRO só com CLIENTES: só `VINCULA (POR NOME)?`; não cria nem altera
   `VINCULA?`. Uma coluna existente é revisada e sobrescrita no lugar.
4. Só PROCESSOS: testa nomes e números. Ambos: testa nomes e números.
5. Cabeçalho casa sem espaços: `VINCULA(POR NOME)?` e `VINCULA (POR NOME)?` são
   a mesma coluna e são sobrescritas no lugar.
6. As colunas novas entram depois do bloco padrão e antes das extras, na ordem
   `VINCULA?` e `VINCULA (POR NOME)?`; se já existirem, ficam no lugar.
7. Nome sem vínculo na descrição (opção do FINANCEIRO, desligada): prefixa
   `NOME DO CLIENTE: <valor> | <descrição>`; descrição vazia fica só o prefixo;
   nome vazio não gera prefixo.
8. Manter apenas um campo vinculante (opção com uma caixa para AGENDA e uma
   para FINANCEIRO, desligadas): em linha vinculada, mantém o campo vencedor e
   move os outros dois para o fim da descrição como `<CABEÇALHO>: <valor>`, no
   separador da planilha; esvazia essas colunas. Não move `MIGRAÇÃO`; linha sem
   vínculo fica como a regra base. Com as duas opções no FINANCEIRO, o prefixo
   do nome vem primeiro, depois a descrição, depois os campos movidos.
9. Saída preserva todas as colunas e as outras abas; original intocado.

## Aceite

- [x] FINANCEIRO vincula por CNJ, PASTA e PROTOCOLO na ordem, com valor bruto.
- [x] `VINCULA (POR NOME)?` responde SIM para nome em PROCESSOS ou CLIENTES e
  NÃO caso contrário, sem normalizar.
- [x] Nome de PROCESSOS com `;` é dividido cru; o trecho é comparado como está.
- [x] Só CLIENTES gera apenas a coluna de nome, sem tocar em `VINCULA?`.
- [x] Opção de nome prefixa a descrição e não deixa separador sobrando.
- [x] Opção de campo único move e esvazia os outros números, sem mover
  `MIGRAÇÃO`.
- [x] Colunas novas ficam depois do bloco padrão e antes das extras; cabeçalho
  sem espaço é reconhecido.
- [x] Saída preserva colunas e abas; original intocado.
- [x] Lint, testes e docs verdes.

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `CURRENT.md`, esta spec, o ADR 0014 e o ADR 0016. Consultar
`core/tools/link.py`, `controllers/link.py`, `ui/pages/link.py` e
`ui/components/tool_layout.py`.

## Arquivos prováveis

- `src/xl_utils/core/tools/link.py`, `controllers/link.py`, `ui/pages/link.py`
- `src/xl_utils/ui/components/tool_layout.py`, `ui/pages/registry.py`
- `tests/test_link.py`, `tests/test_link_page.py`, `tests/test_layout.py`
- `docs/reference/architecture.md`, `docs/reference/ui.md`, `CHANGELOG.md`

## Riscos

- Nome com `;` e espaço depois do separador: `"A; B"` produz `" B"`, que não
  casa com `"B"`. É a comparação bruta; o grupo 2 tem esse caso.
- CNJ numérico no Excel perde precisão antes da leitura; a coluna deve ser texto.
- Reexecução do FINANCEIRO não tem `MIGRAÇÃO`: as colunas são sobrescritas no
  lugar, sem pop-up.
- Quatro entradas aumentam a altura do cartão de entrada; validar a rolagem.

## Próximo depois desta

S7d — log por etapa e acabamento da vinculação.
