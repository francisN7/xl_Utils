# S7b — Vinculação II: FINANCEIRO e CLIENTES

## Objetivo

Acrescentar FINANCEIRO e CLIENTES à vinculação, gerando `VINCULA?` e
`VINCULA (POR NOME)?` no FINANCEIRO sem alterar a AGENDA já entregue.

## Fora de escopo

- Opção “manter apenas um campo vinculante” — fica para a S7c.
- Normalizar nome, CNJ, PASTA ou PROTOCOLO; continua tudo bruto.
- Popular CLIENTES ou PROCESSOS; eles são só fontes de consulta.
- Google Drive e tela cheia.

## Tarefas

1. A página de vinculação passa a ter quatro entradas rotuladas: AGENDA,
   PROCESSOS, FINANCEIRO e CLIENTES. A AGENDA continua obrigatória; as demais
   entram quando o fluxo do FINANCEIRO estiver selecionado.
2. Reaproveitar `find_target_sheet`, `fold_header` e `link_agenda`; criar a
   regra do FINANCEIRO em `core/tools/link.py` com a mesma prioridade
   CNJ → PASTA → PROTOCOLO e comparação bruta.
3. `VINCULA?` no FINANCEIRO: `VINCULA POR CNJ`, `VINCULA POR PASTA`,
   `VINCULA POR PROTOCOLO` ou `NÃO vincula, apenas processo consultivo`.
   Sem mover protocolo e sem `MIGRAÇÃO`.
4. `VINCULA (POR NOME)?` só SIM/NÃO. Montar a lista única com os nomes de
   PROCESSOS (split por `;`) e de CLIENTES; comparar o nome do FINANCEIRO como
   está, sem normalizar. Duplicatas não mudam o resultado.
5. Opção “nome sem vínculo na descrição”: quando o nome não vincula, prefixar
   `NOME DO CLIENTE: <valor> | <descrição>`; descrição vazia vira só
   `NOME DO CLIENTE: <valor>`.
6. Inserir `VINCULA?` e `VINCULA (POR NOME)?` depois do bloco padrão do
   FINANCEIRO e antes das extras, nesta ordem; sobrescrever no lugar se já
   existirem. Preservar todas as colunas e as outras abas.
7. Saída única com o FINANCEIRO transformado (e a AGENDA, se as duas saídas
   forem pedidas na mesma execução) em `output/` ou pasta escolhida.
8. Testes de prioridade, nome, descrição vazia, colunas e reexecução; atualizar
   docs, roadmap, `CURRENT.md` e `CHANGELOG.md`.

## Aceite

- [ ] FINANCEIRO vincula por CNJ, PASTA e PROTOCOLO na ordem, com valor bruto.
- [ ] `VINCULA (POR NOME)?` responde SIM para nome presente em PROCESSOS ou
  CLIENTES e NÃO caso contrário.
- [ ] Nome de PROCESSOS com `;` é dividido em vários nomes; o trecho é comparado
  como está, sem trim.
- [ ] Opção de nome prefixa a descrição com `" | "` e não deixa separador
  sobrando quando a descrição é vazia.
- [ ] Colunas novas ficam depois de `NOME DO CLIENTE` e antes das extras.
- [ ] Saída preserva as colunas de entrada e as outras abas; original intocado.
- [ ] Lint, testes e docs verdes.

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `CURRENT.md`, esta spec, `docs/adr/0014-*.md` e
`docs/adr/0015-*.md`. Consultar `core/tools/link.py`, `controllers/link.py`,
`ui/pages/link.py` e `ui/components/tool_layout.py`. Não reler os controllers
das outras ferramentas.

## Arquivos prováveis

- `src/xl_utils/core/tools/link.py`, `controllers/link.py`, `ui/pages/link.py`
- `src/xl_utils/configs/headers.json` (já tem FINANCEIRO e CLIENTES)
- `tests/test_link.py`, `tests/test_configs.py`
- `docs/reference/architecture.md`, `docs/reference/ui.md`, `CHANGELOG.md`

## Riscos

- Nome com `;` e espaço depois do separador: `"A; B"` produz `" B"`, que não
  casa com `"B"`. É consequência da comparação bruta; confirmar com o dono se
  o split deve aparar o espaço — a decisão vale para toda a ferramenta.
- FINANCEIRO pode não ter a coluna de nome; o erro de coluna ausente já lista
  o que faltou e precisa citar a planilha certa.
- Reexecução do FINANCEIRO não tem `MIGRAÇÃO`: as duas colunas são
  sobrescritas no lugar, sem pop-up.
- O layout atual suporta N entradas rotuladas; quatro entradas aumentam a
  altura do cartão de entrada — validar a rolagem.

## Próximo depois desta

S7c — opção de manter um único campo vinculante, log por etapa e acabamento da
ferramenta.
