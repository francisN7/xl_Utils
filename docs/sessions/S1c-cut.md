# S1c — Recorte de planilha

## Objetivo

Dividir todas as abas de uma planilha em arquivos de N linhas, salvos em
`output/`, usando o pipeline do `all_str` e um campo de linhas editável.

## Fora de escopo

Migrar `merge`; recortar por coluna; juntar abas; editar a planilha original;
preservar fórmulas ou formatação (a saída é texto/tabela).

## Tarefas

1. Criar `core/tools/cut.py` com funções puras:
   - `split_frame(frame, rows_per_file)` devolve os pedaços na ordem, aceitando
     o resto final menor que N e rejeitando N <= 0 com `ValueError`;
   - `split_workbook(sheets, rows_per_file)` devolve
     `{aba: [pedaço, ...]}`, sem perder abas vazias.
2. Criar `controllers/cut.py`:
   - ler por `prepare_workbook`;
   - salvar cada pedaço com `save_workbook` em `output/`;
   - nome de uma aba: `<stem>_Recorte_001.xlsx`;
   - nome de várias abas: `<stem>_<aba>_Recorte_001.xlsx`, com caracteres
     inválidos de nome de arquivo trocados por `_`;
   - devolver caminhos, contagem de arquivos/linhas e log.
3. Ativar o campo “Linhas por arquivo” na página (padrão 1000):
   - `ToolLayout` passa o `ToolState` para a fábrica de opções;
   - o controle fica no estado da página e o run handler lê o valor;
   - valor vazio, zero, negativo ou não numérico vira erro claro na UI.
4. Conectar a página “Recortar Planilha” ao run handler, mostrando caminho(s),
   log e prévia do primeiro recorte.
5. Criar `tests/test_cut.py`: múltiplo exato, resto, N maior que o total,
   N inválido, planilha vazia, duas abas, arquivo original intacto e nomes de
   saída esperados.
6. Apagar `cut.py` da raiz.
7. Atualizar `CURRENT.md`, roadmap, `CHANGELOG.md` e
   `reference/architecture.md`.

## Aceite

- [ ] 2.500 linhas com N=1000 geram 3 arquivos (1000, 1000, 500)
- [ ] todas as abas são recortadas e nomes de saída não colidem
- [ ] N inválido mostra erro na UI e não cria arquivo
- [ ] planilha vazia ou N maior que o total gera um arquivo com todas as linhas
- [ ] a página executa e mostra caminho(s), log e prévia
- [ ] `ruff`, `pytest` e `docs:check` verdes
- [ ] `cut.py` removido da raiz

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec,
`docs/reference/architecture.md`, `core/tools/all_str.py`,
`controllers/all_str.py` e `ui/pages/all_str.py`. Consultar `cut.py` só para
copiar a intenção do recorte; não abrir os outros scripts legados.

## Arquivos prováveis

- `src/xl_utils/core/tools/cut.py`
- `src/xl_utils/controllers/cut.py`
- `src/xl_utils/ui/pages/cut.py`
- `src/xl_utils/ui/components/tool_layout.py`
- `src/xl_utils/ui/pages/registry.py`
- `src/xl_utils/ui/state.py`
- `tests/test_cut.py`

## Riscos

- `range` com passo errado perde a última linha; testar o resto.
- Nomes de aba com `/`, `\`, `:` ou tamanho longo quebram o salvamento.
- `_Recorte_001` pode já existir; `save_workbook` resolve com sufixo, mas o
  teste deve cobrir a colisão.
- O campo de opções muda a assinatura do `ToolLayout`; validar a página do
  `all_str` e do `cnj` depois do refactor.
- Não converter `_x000D_`/`_x000A_`: o pipeline mantém o texto como está.

## Próximo depois desta

S1d — migrar `merge` (unificar arquivos ou abas).
