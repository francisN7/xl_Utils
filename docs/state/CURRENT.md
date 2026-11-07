# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S7d — acabamento da vinculação
- **Próxima:** S8 — tela cheia no merge
- **Ciclo:** 0006 — Backlog
- **Decisões:** comparação bruta; CNJ máscara ou 20 dígitos; `MIGRAÇÃO` é
  sentinela e nunca é comparada; config empacotada em
  `src/xl_utils/configs/headers.json`; ADR 0014 (regra), 0015 (config) e 0016
  (fluxos e opções). O `id`, os módulos `link` e a palavra “vinculação”
  continuam.

## Pronto

- S7d: log por etapa nos dois fluxos, com totais de CNJ/PASTA/PROTOCOLO e
  nome; cartão do Início e cabeçalho com as quatro planilhas e o fluxo pelo
  anexo; textos e docs revisados; grupo 1 confere com o gabarito.
- S7c: quatro entradas, fluxos pelo anexo, opções de nome e campo único;
  `MIGRAÇÃO` limpa em linha vinculada e o cabeçalho casa sem espaços.
- S7a/S7b: motor puro AGENDA × PROCESSOS, `VINCULA?`, pop-up de reexecução e
  o nome “Verificar Vínculos”.
- S6c: tema claro/escuro ao vivo. S6b/S6a: log por etapa e `ORIGEM` no merge.

## Próximo passo

Ler `docs/sessions/S8-tela-cheia-merge.md` e preparar a maximização do quadro
de alinhamento de colunas.

## Arquivos-chave

- `core/tools/link.py`, `controllers/link.py`, `ui/pages/link.py`
- `ui/components/tool_layout.py`, `ui/state.py`, `ui/pages/registry.py`
- `shared/configs.py`, `src/xl_utils/configs/headers.json`
- `tests/test_link.py`, `tests/test_link_page.py`, `tests/test_layout.py`
- `docs/adr/0014-regra-de-vinculacao.md`,
  `docs/adr/0016-fluxos-e-opcoes-da-vinculacao.md`

## Armadilhas

- Comparação bruta: CNJ mascarado × 20 dígitos crus não vincula; é esperado.
- CNJ numérico no Excel perde precisão antes da leitura; a coluna deve ser texto.
- `PROCESSO ORIGINÁRIO` contém “PROCESSO”; o match é exato, nunca substring.
- Cabeçalho dobra caixa/acento e remove espaços; valor de célula não é tocado.
- Nome de PROCESSOS com `;` é dividido cru: `"A; B"` produz `" B"`.
- `MIGRAÇÃO` na AGENDA dispara o pop-up; confirmar não reescreve o protocolo.
- AGENDA sem PROCESSOS bloqueia tudo, mesmo com FINANCEIRO e CLIENTES.
- Só CLIENTES: não valida CNJ e não cria nem altera `VINCULA?`.
- Config empacotada via `importlib.resources`; override em `%LOCALAPPDATA%`.
- Flet não é thread-safe: `pre_run` roda em thread e só devolve texto.
- Cancelar não interrompe pandas: só vale entre arquivos.
- `.xls` não tem leitor alternativo; falha do calamine é final.
- Nunca `push --force` na `main`; `legacy` é somente leitura.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check src tests` · `uv run pytest` · `node scripts/check-docs.mjs`
