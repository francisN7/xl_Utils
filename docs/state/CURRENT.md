# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S7a — vinculação AGENDA × PROCESSOS
- **Próxima:** S7b — FINANCEIRO + CLIENTES
- **Ciclo:** 0006 — Backlog
- **Decisões:** comparação bruta; CNJ máscara ou 20 dígitos; `MIGRAÇÃO`
  sempre; config empacotada em `src/xl_utils/configs/headers.json`; ADR 0014
  (regra) e ADR 0015 (config × estado)

## Pronto

- S7a: motor puro em `core/tools/link.py`; página com duas entradas rotuladas
  (AGENDA e PROCESSOS); `VINCULA?` na prioridade CNJ → PASTA → PROTOCOLO;
  protocolo preservado na descrição e campo vira `MIGRAÇÃO`; pop-up de
  reexecução; saída preserva colunas e abas.
- S6c: tema claro/escuro ao vivo via `theme.restyle`, sem perder estado.
- S6b/S6a: log por etapa e `ORIGEM`/`LINHA_ORIGEM` no merge.

## Próximo passo

Ler `docs/sessions/S7b-vinculacao-financeiro.md` e implementar FINANCEIRO +
CLIENTES, `VINCULA (POR NOME)?` e a opção de nome na descrição.

## Arquivos-chave

- `core/tools/link.py`, `controllers/link.py`, `ui/pages/link.py`
- `shared/configs.py`, `src/xl_utils/configs/headers.json`
- `ui/components/tool_layout.py`, `ui/state.py`, `ui/pages/registry.py`
- `tests/test_link.py`, `tests/test_configs.py`
- `docs/adr/0014-regra-de-vinculacao.md`,
  `docs/adr/0015-config-empacotada.md`

## Armadilhas

- Comparação bruta: CNJ mascarado × 20 dígitos crus não vincula; é esperado.
- CNJ numérico no Excel perde precisão antes da leitura; a coluna deve ser texto.
- `PROCESSO ORIGINÁRIO` contém “PROCESSO”; o match é exato, nunca substring.
- Cabeçalho dobra caixa/acento/espaço; valor de célula não é tocado.
- `MIGRAÇÃO` na AGENDA dispara o pop-up; confirmar não reescreve o protocolo.
- Config empacotada via `importlib.resources`; override em `%LOCALAPPDATA%`.
- Flet não é thread-safe: `pre_run` roda em thread e só devolve texto.
- Cancelar não interrompe pandas: só vale entre arquivos.
- `.xls` não tem leitor alternativo; falha do calamine é final.
- Nunca `push --force` na `main`; `legacy` é somente leitura.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check
src tests` · `uv run pytest` · `node scripts/check-docs.mjs`
