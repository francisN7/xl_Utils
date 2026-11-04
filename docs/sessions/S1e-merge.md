# S1e — Mesclagem de planilhas

## Objetivo

Substituir `merge.py` por uma ferramenta única: concatenar as abas selecionadas
de todos os arquivos na ordem, com coluna `ORIGEM` e alinhamento de colunas.

## Fora de escopo

Alinhar colunas automaticamente; converter tipos; arrastar colunas (o Flet 1.0
não oferece drag); juntar linhas por chave (join).

## Tarefas

1. Criar `core/tools/merge.py`:
   - `merge_sheets(entries, column_map)` recebe uma sequência de
     `(arquivo, aba, DataFrame)` já limpa e filtrada;
   - descarta abas sem linhas, mas nunca descarta linhas com dados;
   - aplica `column_map` (`{coluna_de_origem: coluna_canônica}`) antes de
     concatenar;
   - concatena com `ignore_index=True`, na ordem de arquivos e abas;
   - adiciona `ORIGEM` como primeira coluna, no formato
     `<arquivo> - <aba> - <linha>`, com a linha contada a partir de 1 na origem.
2. Criar `controllers/merge.py` com `run_merge(sources)`:
   - cada fonte é `(Path, set[str] | None)`;
   - lê com `prepare_workbook`, filtra com `filter_sheets` e chama
     `merge_sheets`;
   - exige ao menos uma aba no total e ao menos duas fontes ou duas abas;
   - salva `output/Merge.xlsx` (`Mesclado`) e log por arquivo (abas, linhas, colunas).
3. Criar `ui/pages/merge.py`:
   - reaproveita o seletor, com `multiple_files=True` e o padrão de primeira aba
     por arquivo (o lote das outras ferramentas segue o ADR 0006);
   - opções mostram, para cada coluna distinta, um dropdown para escolher a
     coluna canônica; colunas iguais já ficam alinhadas;
   - o mapeamento vive em `ToolState.options` e é recalculado quando os
     arquivos ou as abas mudam;
   - seleção vazia mostra erro claro antes de executar.
4. Trocar `_merge_options` e o registro em `ui/pages/registry.py` pela nova
   página com run handler; apagar `merge.py` da raiz.
5. Criar `tests/test_merge.py`:
   - ordem de arquivos e abas preservada;
   - `ORIGEM` correto, incluindo nome de arquivo, aba e linha;
   - colunas ausentes viram `NaN` e colunas extras aparecem no fim;
   - `column_map` funde colunas de nomes diferentes;
   - abas vazias ignoradas; seleção vazia e fonte única rejeitadas;
   - saída em `output/Merge.xlsx` sem alterar as origens.
6. Atualizar `CURRENT.md`, roadmap, `CHANGELOG.md`,
   `reference/architecture.md` e `reference/ui.md`.

## Aceite

- [ ] mesclar dois arquivos com as abas marcadas gera `output/Merge.xlsx`
- [ ] `ORIGEM` identifica arquivo, aba e linha de cada registro
- [ ] mapear colunas com nomes diferentes não perde dados
- [ ] abas não selecionadas e abas vazias não entram
- [ ] execução com uma única aba avisa que não há o que mesclar
- [ ] `merge.py` removido da raiz e a página funciona no lugar do placeholder
- [ ] `ruff`, `pytest` e `docs:check` verdes

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec,
`docs/reference/architecture.md`, `docs/adr/0005-selecao-de-abas-e-merge.md`,
`docs/adr/0006-lote-de-arquivos.md`, `core/tools/sheets.py`,
`core/tools/all_str.py`, `ui/pages/registry.py`,
`ui/components/sheet_selector.py` e `merge.py`; controllers existentes só para
repetir o padrão de log e saída.

## Arquivos prováveis

- `src/xl_utils/core/tools/merge.py`
- `src/xl_utils/controllers/merge.py`
- `src/xl_utils/ui/pages/merge.py`
- `src/xl_utils/ui/pages/registry.py`
- `src/xl_utils/ui/state.py`
- `tests/test_merge.py`
- `merge.py` (remover)

## Riscos

- Cabeçalhos duplicados na mesma aba; o alinhamento por nome precisa de índice.
- `pd.concat` com colunas diferentes gera `NaN`; conferir na prévia e no log.
- Caminho `output/Merge.xlsx` já existente: `save_workbook` cria nome livre.
- Dropdowns demais estouram a largura do card; agrupar por coluna canônica.
- Ordem de arquivos/abas precisa ser a da UI, não a do dicionário.

## Próximo depois desta

S2a — integração do fluxo: testes com planilhas reais fictícias, leitura de
`.xls`, `.csv` e `.html` e reparo de arquivo corrompido.
