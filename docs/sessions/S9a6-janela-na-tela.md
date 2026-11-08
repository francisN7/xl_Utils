# S9a6 — Janela abre na tela primária

## Objetivo

Corrigir a janela que podia abrir fora da tela, em coordenadas negativas de um
monitor à esquerda, dando a impressão de que o `xl-utils` não iniciava.

## Causa

O Flet/Flutter escolhia a posição inicial sozinho. Em um arranjo de monitores
com a tela primária à esquerda (ou um monitor desconectado), a janela nascia em
`x = -1374`, visível apenas no desktop virtual.

## Decisão

Fixar `left = 80` e `top = 60` em `app.main`. A tela primária do Windows sempre
tem origem `(0,0)`, então a janela abre em uma área visível,
independentemente do arranjo de monitores.

## Tarefas

1. Definir `page.window.left` e `page.window.top`.
2. Testar que o shell recebe esses valores.
3. Reiniciar o app e conferir o retângulo da janela.
4. Registrar em UI, roadmap, CHANGELOG e estado.

## Aceite

- [x] Janela abre em `80,60`, visível.
- [x] Teste do shell confere `left` e `top`.
- [x] App inicia sem erro.
- [x] Docs, lint e testes verdes.

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `CURRENT.md`, esta spec e `app.py`.

## Arquivos prováveis

- `src/xl_utils/app.py`
- `tests/test_drive_session.py`
- `docs/reference/ui.md`, `docs/roadmap/main.md`,
  `docs/state/CURRENT.md`, `CHANGELOG.md`

## Riscos

- Em telas menores que 1280×860, a janela ainda pode passar do limite; o
  usuário pode redimensionar/mover, e o mínimo de 980×640 continua valendo.
- A posição fixa ignora onde o usuário deixou a janela na sessão anterior.

## Adendo — atalho global do `xl-utils`

O comando `xl-utils` no PATH vinha de um `uv tool install --editable .` antigo.
O ambiente isolado do tool não acompanha o `.venv`: depois do S9a, ele ficou sem
`google-auth-oauthlib` e o app morria com `ModuleNotFoundError: No module named
'google'` antes de abrir a janela. Reinstalar com `uv tool install --editable .
--force` resolve. Para o dia a dia, `uv run xl-utils` usa o `.venv` e é o
caminho recomendado.

O `uv tool install` também resolveu Flet 1.1.2, que ignorou a posição
`left/top` e abriu a janela fora da tela. O `pyproject.toml` passou a exigir
`flet[desktop]>=1.0.5,<1.1`, mantendo o atalho na mesma versão testada do
`.venv` (1.0.5).

## Próximo depois desta

S9b — Drive II: link/seletor e escrita do resultado.
