# S2a — Integração do fluxo

## Objetivo

Cobrir as quatro ferramentas ponta a ponta com planilhas fictícias nos formatos
`.xlsx`, `.xls`, `.csv` e `.html`, incluindo o reparo de leitura.

## Fora de escopo

Testes de widget/Flet; logging estruturado (S2b); remoção das opções fixas
(S2c); conferência entre tipo real e extensão (S2d); formatos novos.

## Tarefas

1. Criar fixtures sintéticas em `tmp_path` para `.xlsx`, `.csv` e `.html`; para
   `.xls`, versionar **um** binário mínimo e fictício em `tests/fixtures/`,
   gerado uma vez com `uv run --with xlwt` (não adicionar `xlwt` ao projeto).
2. Cobrir `read_workbook`, `list_sheets` e `read_headers` nos quatro formatos,
   com zeros à esquerda, CNJ-like e acentos preservados.
3. Testar o reparo:
   - CSV em `cp1252` que falha na leitura normal e passa pelo fallback;
   - arquivo inválido que sobe `WorkbookReadError` com o nome da origem.
4. Rodar `run_all_str`, `run_cnj`, `run_cut` e `run_merge` sobre as fixtures e
   conferir: saída em `output/`, abas/linhas esperadas e origem intacta
   (comparar bytes antes e depois).
5. Testar o merge com origens de formatos diferentes na mesma execução,
   conferindo `ORIGEM` e alinhamento de colunas.
6. Atualizar `reference/architecture.md` (seção Testes), `guide/testing.md`,
   `CURRENT.md`, roadmap e `CHANGELOG.md`.

## Aceite

- [ ] `.xlsx`, `.xls`, `.csv` e `.html` são lidos como texto sem perder zeros
- [ ] CSV cp1252 é reparado; arquivo inválido vira `WorkbookReadError`
- [ ] cada controller grava em `output/` e não altera os arquivos de origem
- [ ] merge aceita origens mistas e mantém `ORIGEM` por arquivo, aba e linha
- [ ] `ruff`, `pytest` e `docs:check` verdes

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec, `core/io.py`,
`core/mime.py`, `core/tools/all_str.py`, os controllers só pelas assinaturas,
`tests/test_all_str.py`, `docs/guide/testing.md` e o ADR 0004.

## Arquivos prováveis

- `tests/test_formats.py`
- `tests/test_integration.py`
- `tests/fixtures/minimo.xls`
- `docs/reference/architecture.md` (Testes)
- `docs/guide/testing.md`

## Riscos

- O pandas 3 não escreve `.xls`; a fixture binária precisa ser pequena,
  fictícia e documentada no teste.
- HTML usa `PáginaN` e pode gerar colunas `Unnamed`; fixar o esperado.
- O caminho normal do CSV usa vírgula; o `sep=None` só entra no reparo.
- Reparo não pode esconder corrupção real: o arquivo inválido precisa falhar.
- O merge relê cada origem para listar colunas e para mesclar; medir se pesa.

## Próximo depois desta

S2b — logging e erros: log estruturado por execução, erros tipados na UI e botão
de copiar diagnóstico.
