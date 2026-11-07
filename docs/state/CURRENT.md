# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S8 — tela cheia no merge
- **Próxima:** S9a — Drive I (ADR, OAuth, contas e shell)
- **Ciclo:** 0006 — Backlog
- **Decisões:** comparação bruta; CNJ máscara ou 20 dígitos; `MIGRAÇÃO` é
  sentinela; config empacotada em `src/xl_utils/configs/headers.json`;
  ADRs 0014 (regra), 0015 (config), 0016 (fluxos) e 0017 (tela cheia por
  overlay no conteúdo). O `id`, os módulos `link` e “vinculação” continuam.

## Pronto

- S8: maximizar ao lado de “Alinhamento de colunas” cobre o conteúdo, mantém
  os cards em 196 px com a sobra como espaçamento e volta pelo mesmo ícone ou
  por “CONFIRMAR” no canto inferior direito. Grupos, seleção e ordem
  sobrevivem; o tema recolore o painel escondido. Confirmado no app.
- S7d/S7c/S7a/S7b: vinculação completa — quatro entradas, fluxos pelo anexo,
  opções, log por etapa, `MIGRAÇÃO` como sentinela e o nome “Verificar
  Vínculos”. S6: tema ao vivo e `ORIGEM` no merge.

## Próximo passo

Ler `docs/sessions/S9a-drive-autenticacao.md` e escrever o ADR 0018 antes de
qualquer código de Drive.

## Arquivos-chave

- `ui/components/tool_layout.py` (`OverlayHost`), `ui/pages/merge.py`
- `ui/state.py`, `ui/pages/registry.py`, `ui/theme.py`
- `core/tools/link.py`, `controllers/link.py`, `ui/pages/link.py`
- `shared/configs.py`, `src/xl_utils/configs/headers.json`
- `tests/test_merge_page.py`, `tests/test_layout.py`, `tests/test_link.py`
- `docs/adr/0017-tela-cheia-do-quadro.md`,
  `docs/adr/0016-fluxos-e-opcoes-da-vinculacao.md`

## Armadilhas

- A tela cheia cobre só o conteúdo; a sidebar continua clicável.
- O painel é montado uma vez: não recriar grupos ao maximizar/restaurar.
- Comparação bruta: CNJ mascarado × 20 dígitos crus não vincula.
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
