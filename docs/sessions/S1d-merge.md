# S1d — Mesclagem de planilhas

## Objetivo

Unificar a primeira aba de vários arquivos ou todas as abas de uma planilha em
um único xlsx em `output/`, usando o pipeline do `all_str`.

## Fora de escopo

Cruzar linhas por chave; escolher colunas; preservar fórmulas ou formatação;
migrar `cut` (já feito); editar os arquivos de origem.

## Tarefas

1. Criar `core/tools/merge.py` com funções puras:
   - `merge_frames(frames)` descarta DataFrames vazios ou só com `NaN`,
     concatena com `ignore_index=True, sort=False` e preserva a ordem;
   - sem nenhum DataFrame válido, levanta `ValueError` com mensagem clara.
2. Criar `controllers/merge.py`:
   - modo `files`: lê a primeira aba de cada arquivo selecionado;
   - modo `sheets`: lê todas as abas do primeiro arquivo selecionado;
   - sempre por `prepare_workbook`;
   - salva em `output/<stem>_Mesclado.xlsx`, com a aba `MESCLADO`;
   - devolve caminho, linhas, colunas, abas usadas e log por origem.
3. Ativar o seletor “Modo de mesclagem” na página:
   - `files` = primeira aba de cada arquivo;
   - `sheets` = todas as abas de uma planilha;
   - o `Dropdown` fica em `ToolState.options` e o run handler lê o valor.
4. Conectar a página “Mesclar Planilhas” ao run handler, com caminho, log e
   prévia do resultado.
5. Criar `tests/test_merge.py`: mesmas colunas, colunas diferentes, ordem
   preservada, abas vazias ignoradas, modo `files`, modo `sheets`, sem dados,
   arquivos originais intactos e nome de saída.
6. Apagar `merge.py` da raiz.
7. Atualizar `CURRENT.md`, roadmap, `CHANGELOG.md` e
   `reference/architecture.md`.

## Aceite

- [ ] duas planilhas com o mesmo cabeçalho viram uma só, na ordem selecionada
- [ ] cabeçalhos diferentes geram união de colunas sem perder linhas
- [ ] modo `sheets` usa todas as abas do primeiro arquivo
- [ ] abas vazias ou só com `NaN` não entram no resultado
- [ ] nenhuma origem válida mostra erro claro, sem criar arquivo
- [ ] a página executa e mostra caminho, log e prévia
- [ ] `ruff`, `pytest` e `docs:check` verdes
- [ ] `merge.py` removido da raiz

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec,
`docs/reference/architecture.md`, `core/tools/all_str.py`,
`controllers/cut.py` e `ui/pages/cut.py`. Consultar `merge.py` só para copiar a
intenção dos dois modos.

## Arquivos prováveis

- `src/xl_utils/core/tools/merge.py`
- `src/xl_utils/controllers/merge.py`
- `src/xl_utils/ui/pages/merge.py`
- `src/xl_utils/ui/pages/registry.py`
- `tests/test_merge.py`

## Riscos

- `pd.concat` com colunas diferentes preenche ausente com `NaN`; o salvamento
  deve manter a célula vazia.
- Ordem dos arquivos no seletor precisa ser preservada.
- Modo `sheets` com vários arquivos selecionados usa só o primeiro; deixar isso
  explícito no log.
- Planilha sem nenhuma aba com dados não pode gerar arquivo vazio silencioso.
- Cabeçalhos com espaços/acentos são nomes de coluna; não normalizar.

## Próximo depois desta

S2a — integração do fluxo: planilhas reais fictícias, `.xls`, `.csv`, `.html` e
reparo de arquivo corrompido.
