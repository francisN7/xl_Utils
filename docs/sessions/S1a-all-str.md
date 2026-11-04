# S1a — Pipeline do all_str

## Objetivo

Toda ferramenta ler por um único pipeline que preserva texto e remove emojis,
com a página de Tratamento de Texto funcionando e testada.

## Fora de escopo

Migrar `cnj`, `cut` ou `merge`; empacotamento; editar o arquivo original.

## Tarefas

1. Criar `core/tools/all_str.py` com `prepare_workbook(path)`:
   - ler com `read_workbook(path, dtype=str)`;
   - remover emojis célula a célula com `remove_emojis`;
   - não converter nem remover quebras de linha.
2. Implementar o reparo de leitura quando o arquivo falhar, sem `shell=True`
   e sem `xlsx2csv`; se não for possível, levantar erro tipado.
3. Expor `prepare_workbook` para as demais ferramentas (o local exato fica a
   critério da implementação; documentar no ADR se mudar).
4. Conectar a página de Tratamento de Texto ao run handler: selecionar arquivo,
   executar, salvar em `output/` com `save_workbook` e mostrar resultado.
5. Criar `tests/test_all_str.py` com zeros à esquerda, CNJ, emojis e quebras de
   linha preservadas.
6. Apagar `all_str.py` da raiz.
7. Atualizar `CURRENT.md`, roadmap, `CHANGELOG.md` e `reference/architecture.md`.

## Aceite

- [ ] uma planilha com `000123`, CNJ e emoji sai com o texto intacto e sem emoji
- [ ] quebras de linha originais continuam iguais
- [ ] a página executa e mostra caminho, log e prévia
- [ ] nenhum `shell=True` ou `xlsx2csv` no caminho novo
- [ ] `ruff`, `pytest` e `docs:check` verdes
- [ ] `all_str.py` removido da raiz

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec,
`docs/reference/architecture.md` e `docs/reference/ui.md`. Consultar
`core/io.py`, `core/text.py` e `tool_layout.py` só quando necessário. Não ler
os scripts legados além do `all_str.py` que será apagado.

## Arquivos prováveis

- `src/xl_utils/core/tools/all_str.py`
- `src/xl_utils/core/io.py`
- `src/xl_utils/core/text.py`
- `src/xl_utils/ui/pages/registry.py`
- `tests/test_all_str.py`

## Riscos

- pandas 3 pode mudar a leitura de `.xls`/`.html`; testar com um arquivo real.
- Reparo de xlsx corrompido é o ponto mais frágil; começar com erro tipado em
  vez de gambiarra.
- Emoji em célula com quebra de linha: validar que o `\n` sobrevive.

## Próximo depois desta

S1b — migrar `cnj` usando o pipeline do `all_str`.
