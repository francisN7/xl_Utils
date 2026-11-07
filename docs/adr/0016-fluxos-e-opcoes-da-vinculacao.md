# ADR 0016 — Fluxos independentes e opções da vinculação

- **Status:** aceita
- **Data:** 2026-11-07

## Contexto

A vinculação nasceu com AGENDA × PROCESSOS (ADR 0014). A S7c acrescenta
FINANCEIRO e CLIENTES e o dono definiu que uma execução pode ser só da AGENDA,
só do FINANCEIRO ou das duas. O arquivo anexado é a intenção: não faz sentido
pedir um checkbox extra para “verificar” o que já foi anexado. O FINANCEIRO
também pode ser conferido só por nome, quando não há PROCESSOS.

Duas opções pedidas pelo dono:

1. **Nome sem vínculo na descrição** (só FINANCEIRO): prefixar a descrição com
   o nome do cliente quando a coluna de nome não vincula.
2. **Manter apenas um campo vinculante** (AGENDA, FINANCEIRO ou ambos): manter
   só o campo numérico que venceu a prioridade e levar os demais para a
   descrição.

## Decisão

- **Fluxos pelo anexo.** AGENDA anexada exige PROCESSOS; FINANCEIRO anexado
  exige PROCESSOS ou CLIENTES. AGENDA sem PROCESSOS bloqueia a execução
  inteira; pelo menos um dos dois fluxos precisa estar presente. Cada fluxo
  gera uma saída.
- **Só CLIENTES no FINANCEIRO.** Só `VINCULA (POR NOME)?` é criada ou
  sobrescrita; `VINCULA?` não é criada nem alterada. A validação de CNJ só
  roda quando PROCESSOS está presente.
- **`MIGRAÇÃO` é sentinela.** Nunca entra na comparação de protocolo, nem na
  AGENDA nem no PROCESSOS. Em linha vinculada, a coluna de protocolo é
  esvaziada; em linha sem vínculo, a sentinela permanece e a descrição não é
  tocada na reexecução.
- **Cabeçalho sem espaços.** `header_key` remove todos os espaços depois de
  dobrar caixa e acento. `VINCULA(POR NOME)?` e `VINCULA (POR NOME)?` são a
  mesma coluna; a existente é sobrescrita no lugar e mantém o rótulo original.
- **Ordem das colunas.** `VINCULA?` e depois `VINCULA (POR NOME)?`, depois do
  bloco padrão e antes das extras. Com só CLIENTES, a coluna de nome entra
  depois de um `VINCULA?` que já exista.
- **Nome sem vínculo.** Prefixo literal `NOME DO CLIENTE: <valor>` mais o
  separador `" | "` da planilha; descrição vazia recebe só o prefixo; nome
  vazio não gera prefixo. Opção desligada por padrão.
- **Campo único.** Só em linha vinculada: o vencedor fica na coluna e os outros
  dois campos vão para o fim da descrição como `<CABEÇALHO>: <valor>`; as
  colunas são esvaziadas. `MIGRAÇÃO` não é movida. No FINANCEIRO, o prefixo do
  nome vem primeiro, depois a descrição, depois os campos movidos. Opção
  desligada por padrão, com uma caixa por planilha.

## Consequências

- O usuário precisa anexar as planilhas certas; o botão e o aviso dizem o que
  falta. Não há seleção de fluxo separada.
- O FINANCEIRO sem PROCESSOS não valida CNJ e não gera `VINCULA?`; a conferência
  fica restrita ao nome.
- A descrição do FINANCEIRO pode crescer com o prefixo do nome e com os campos
  movidos; a ordem é estável.
- A sentinela deixa de gerar falso positivo quando um PROCESSOS traz
  literalmente `MIGRAÇÃO` no protocolo.
- A coluna de nome existente com grafia sem espaço continua com a grafia do
  usuário; só o conteúdo é revisado.

## Alternativas

- **Checkbox “Verificar AGENDA/FINANCEIRO”.** Rejeitada: o arquivo anexado já
  expressa a intenção e o checkbox só duplicaria a decisão.
- **Exigir PROCESSOS para o FINANCEIRO.** Rejeitada: o dono quer conferir só
  nomes quando a fonte numérica não está disponível.
- **Normalizar nome/CNJ para aumentar matches.** Rejeitada: a ferramenta é um
  teste de vinculação; o falso negativo por formato é o resultado esperado.
- **Tratar `MIGRAÇÃO` como protocolo comum.** Rejeitada: gera vínculo falso na
  reexecução e mistura estado com dado.
- **Remover as colunas dos campos movidos.** Rejeitada: a saída preserva as
  colunas de entrada; o conteúdo migra para a descrição.
