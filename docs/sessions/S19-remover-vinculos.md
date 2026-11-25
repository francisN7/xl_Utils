# S19 — Remover Verificar Vínculos e preparar o repo de plugins

## Objetivo

O app deixa de ter **Verificar Vínculos** (quatro ferramentas nativas + Plugins
no rodapé) e existe o esqueleto do repo privado `xl_U-Plugins`, com o código
atual da vinculação como referência e o guia reutilizável de criação.

## Fora de escopo

- Reescrever a vinculação como plugin funcional (depende da API 2, S20).
- Mudar o contrato dos plugins ou a página Plugins.
- Menu de perfis do Drive (S21) e auditoria geral dos docs (S22).

## Tarefas

1. Remover `core/tools/link.py`, `controllers/link.py`, `ui/pages/link.py` e a
   entrada `link` de `ui/pages/registry.py`.
2. Limpar referências em `shared/configs.py` e `ui/components/tool_layout.py`
   (e a parte da vinculação em `configs/headers.json`, se só ela usa).
3. Remover `tests/test_link.py`, `tests/test_link_page.py` e os casos de
   vinculação em `tests/test_configs.py`.
4. Docs: `docs/reference/ui.md` (Layout, Início, **Vinculação**),
   `docs/reference/architecture.md`, `docs/index.html`, AGENTS.md (“cinco
   utilitários”); ADRs 0014/0016 ganham nota “superado — removido na S19”.
5. Esqueleto em `/home/francis/Apps/Codes/xl_U-Plugins` (repo próprio, remoto
   `francisN7/xl_U-Plugins`; commit lá, push só com OK): README, `link/` com o
   código atual como referência e guia de criação reaproveitando
   `docs/plugins/`.
6. CHANGELOG (Removed).

## Aceite

- [ ] Nenhuma referência a `link`/Vínculos em `src/` e `tests/` (`grep`).
- [ ] Início com quatro cartões; sidebar sem Vínculos; Plugins no rodapé.
- [ ] Esqueleto `xl_U-Plugins` criado com o código de referência.
- [ ] `ruff`, `pytest` e `uv run python scripts/check_docs.py` verdes.

## Orçamento de contexto (≤90 linhas)

`grep -rn link` em `src/` e `tests/`; `shared/configs.py` e `tool_layout.py`
só nos trechos achados; `docs/reference/ui.md` → **Layout**, **Início**,
**Vinculação**; `architecture.md` só a linha das ferramentas.

## Arquivos prováveis

- `src/xl_utils/core/tools/link.py`, `controllers/link.py`, `ui/pages/link.py`
- `src/xl_utils/ui/pages/registry.py`, `shared/configs.py`,
  `ui/components/tool_layout.py`, `configs/headers.json`
- `tests/test_link.py`, `tests/test_link_page.py`, `tests/test_configs.py`

## Riscos

- `headers.json` e `shared/configs.py` podem servir a outras ferramentas:
  remover só as chaves da vinculação.
- O repo de plugins tem só `README.md` (1 commit) e esse README estava com
  mudança não commitada em 2026-11-25: conferir com o dono antes de mexer.

## Próximo depois desta

S20 — Leitura de planilhas pelo host e API 2 dos plugins.
