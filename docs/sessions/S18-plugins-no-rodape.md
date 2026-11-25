# S18 — Plugins no rodapé da sidebar, fora do Início

## Objetivo

**Plugins** sai do hub Início e da lista principal da sidebar e vira um item
fixo no rodapé, acima de `uv · Python 3.15`, abrindo a mesma página de hoje.

## Fora de escopo

- Mudar a página Plugins, o instalador ou o contrato dos plugins (S20).
- Remover Verificar Vínculos (S19) ou mexer no menu de perfis (S21).
- Novo ícone ou redesenho do logo (S17 já entregou o ícone real).

## Tarefas

1. Separar no registro (`ui/pages/registry.py`) as ferramentas do hub das
   páginas de rodapé, sem duplicar o `ToolPage` de Plugins.
2. `home.py`: o hub monta cartões só das ferramentas nativas.
3. `Sidebar`: item Plugins no `_footer`, com o mesmo realce de selecionado dos
   itens principais.
4. `app.py`: índice de navegação estável (`show`, abrir por `tool_id`), sem
   depender da posição de Plugins em `TOOLS`.
5. Testes headless: Início sem cartão Plugins; clicar no rodapé abre Plugins e
   marca só esse item; abrir por `tool_id` continua funcionando.
6. Atualizar `docs/reference/ui.md` → **Layout**/**Início** e o CHANGELOG.

## Aceite

- [ ] Início sem o cartão Plugins; sidebar com Plugins no rodapé.
- [ ] Navegar Início → ferramenta → Plugins → ferramenta preserva o estado.
- [ ] Tema escuro e claro conferidos com `uv run xl-utils`.
- [ ] `ruff`, `pytest` e `uv run python scripts/check_docs.py` verdes.

## Orçamento de contexto (≤90 linhas)

`ui/pages/registry.py` (definição de `TOOLS`), `ui/components/sidebar.py` →
`__init__`, `_item`, `select`, `_footer`; `app.py` → `show` e busca por
`tool_id`; `ui/pages/home.py` → montagem dos cartões; `docs/reference/ui.md` →
**Layout** e **Início**. Nada além disso.

## Arquivos prováveis

- `src/xl_utils/ui/pages/registry.py`, `src/xl_utils/ui/pages/home.py`
- `src/xl_utils/ui/components/sidebar.py`, `src/xl_utils/app.py`
- `tests/test_theme.py`, `tests/test_sidebar_icon.py`, `tests/test_plugins_ui.py`
- `docs/reference/ui.md`, `CHANGELOG.md`

## Riscos

- `app.py` usa `index - 1` sobre `TOOLS`: tirar Plugins da lista desloca
  índices; testar a navegação por `tool_id`.
- `select` hoje percorre `_items`; o item do rodapé precisa entrar no mesmo
  realce, senão dois itens ficam marcados.

## Próximo depois desta

S19 — Remover Verificar Vínculos e preparar o repo de plugins.
