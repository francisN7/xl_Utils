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

## Próximo depois desta

S9b — Drive II: link/seletor e escrita do resultado.
