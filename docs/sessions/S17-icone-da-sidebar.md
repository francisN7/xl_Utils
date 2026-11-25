# S17 — Ícone da sidebar e da janela

## Objetivo

A sidebar mostra o ícone real do app no lugar do quadrado “x”, e a janela usa
`assets/icon.ico` no cabeçalho, no dev e no build Windows.

## Fora de escopo

- Redesenhar o ícone ou gerar variantes (`scripts/make_icons.py` fica igual).
- Mover Plugins para o rodapé (S18) ou mexer no menu de perfis.
- Ícone do instalador além do que o `build_windows.ps1` já usa.

## Tarefas

1. Trocar o placeholder “x” de `Sidebar._logo`
   (`src/xl_utils/ui/components/sidebar.py`) por `assets/icon.png`, no tamanho
   atual, com fallback para o “x” se o arquivo faltar.
2. Definir o ícone da janela em `app.py` (`page.window.icon`) com `assets/icon.ico`
   e caminho resolvido para dev e para o exe empacotado.
3. Garantir que o build leve `assets/` para o lado do exe
   (`scripts/build_windows.ps1`, `--add-data`) e que o caminho funcione no
   bundle.
4. Teste headless: a sidebar monta com e sem o PNG, sem exceção.
5. Atualizar `docs/reference/ui.md` → **Layout** e o CHANGELOG.

## Aceite

- [ ] Sidebar com o ícone real em tema escuro e claro.
- [ ] Ícone da janela no dev (`uv run xl-utils`).
- [ ] Build Windows com o ícone na janela e na sidebar (ou registrado como
  pendente de validação no Windows).
- [ ] `ruff`, `pytest` e `uv run python scripts/check_docs.py` verdes.

## Orçamento de contexto (≤90 linhas)

`ui/components/sidebar.py` → `_logo`, `app.py` → montagem da página,
`scripts/build_windows.ps1` (trecho do PyInstaller), `docs/reference/ui.md` →
**Layout** e a armadilha do `flet pack` em CURRENT. Nada além disso.

## Arquivos prováveis

- `src/xl_utils/ui/components/sidebar.py`, `src/xl_utils/app.py`
- `scripts/build_windows.ps1`, `tests/test_sidebar.py` (ou equivalente)
- `docs/reference/ui.md`, `CHANGELOG.md`

## Riscos

- Caminho relativo quebra no exe: resolver por `sys._MEIPASS`/pasta do exe.
- Linux não valida o `.ico` no título da janela; a checagem final é no Windows.
- `flet pack` apaga `build/`; artefatos em `artifacts/`.

## Próximo depois desta

S18 — Plugins no rodapé da sidebar, fora do Início.
