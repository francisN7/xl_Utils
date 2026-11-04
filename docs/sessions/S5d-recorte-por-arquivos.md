# S5d — Recorte por quantidade de arquivos

## Objetivo

Permitir recortar cada aba em uma quantidade escolhida de arquivos, além do
modo atual de linhas por arquivo, sem mudar o formato de saída.

## Fora de escopo

Cortar por coluna, por tamanho em bytes, juntar abas em um único arquivo,
alterar o merge, mudar o padrão de nome `_Recorte_NNN` ou o salvamento.

## Tarefas

1. No core, expor um segundo modo de divisão: `split_frame_by_parts(frame, n)`
   e `split_workbook_by_parts(sheets, n)`, devolvendo `n` blocos sequenciais
   quando houver linhas suficientes.
2. Regra de distribuição: blocos de `ceil(linhas / n)`; o último recebe o resto.
   Se `n` for maior que as linhas, reduzir ao número de linhas, sem gerar
   arquivos vazios; aba vazia continua gerando um arquivo.
3. Na página de recorte, alternar entre “Linhas por arquivo” e “Arquivos por
   aba” com um seletor; guardar modo e valor em `ToolState.options` e validar
   inteiro positivo com mensagem clara.
4. No controller, escolher o modo recebido e registrar no log qual regra foi
   usada; manter `SaveItem`, nomes e prévia iguais.
5. Cobrir os dois modos no core, o limite `n > linhas`, aba vazia e a integração
   nos quatro formatos.
6. Atualizar `architecture.md`, `code-tour.md` e o texto de ajuda da página.

## Aceite

- [ ] o usuário escolhe entre linhas por arquivo e arquivos por aba
- [ ] a quantidade de arquivos vale **por aba**, não pelo lote inteiro
- [ ] nenhum modo gera arquivo vazio além do caso de aba vazia
- [ ] nomes `_Recorte_NNN`, ordem das linhas e conteúdo permanecem iguais
- [ ] `ruff`, `ruff format --check`, `pytest` e `docs:check` verdes

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec, `core/tools/cut.py`,
`controllers/cut.py`, `ui/pages/cut.py`, `tests/test_cut.py` e a seção
“Recorte” de `reference/architecture.md`.

## Arquivos prováveis

- `src/xl_utils/core/tools/cut.py`
- `src/xl_utils/controllers/cut.py`
- `src/xl_utils/ui/pages/cut.py`
- `tests/test_cut.py`, `tests/test_integration.py`
- `docs/reference/architecture.md`, `docs/guide/code-tour.md`

## Riscos

- `ceil` com `n` grande pode gerar blocos de uma linha; validar o limite e
  testar com 1, 2, linhas exatas e resto.
- O modo antigo precisa continuar idêntico para não quebrar os testes de
  integração e os nomes já usados.
- A prévia atual mostra só a primeira parte; não prometer prévia de todas as
  partes nesta sessão.
- O seletor não pode perder o valor ao trocar de modo sem o usuário perceber;
  manter um valor de cada modo no estado.

## Próximo depois desta

Fase 2 concluída; próximo é o backlog do ciclo (tema claro ou histórico de
execuções) ou o fechamento do ciclo 0004.
