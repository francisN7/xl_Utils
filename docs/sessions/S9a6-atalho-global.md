# S9a6 — Atalho global do `xl-utils`

## Objetivo

Fazer o comando `xl-utils` (atalho global) abrir o app, manter o Flet na versão
mais nova e deixar a janela na posição/monitor que o usuário escolher.

## Causa

- O atalho global criado com `uv tool install --editable .` tem um ambiente
  isolado próprio. Ele não recebeu as dependências do Google adicionadas na S9a
  e o comando morria com `ModuleNotFoundError: No module named 'google'` antes
  de abrir a janela.
- A janela em coordenadas negativas era o **monitor secundário**, para onde o
  usuário a move de propósito. Não era bug; forçar `left`/`top` foi um
  diagnóstico errado e foi removido.
- O teto `<1.1` no Flet também foi removido: o projeto usa a versão mais nova e
  o lock/tool acompanham (1.1.2).

## Decisões

- **Reinstalar o tool após mudar dependências:** `uv tool install --editable .
  --force`. Para o dia a dia, `uv run xl-utils` usa o `.venv`.
- **Não fixar a posição da janela:** o app não define `left`/`top`; o usuário
  escolhe o monitor e o gerenciador de janelas cuida do resto.
- **Flet sem teto:** `flet[desktop]>=1.0.5`, com o lock atualizado para a versão
  mais nova; a suíte roda nela.

## Tarefas

1. Reinstalar o atalho global com as dependências atuais.
2. Remover `left`/`top` e o teste que os exigia.
3. Remover o teto `<1.1` e atualizar o lock para Flet 1.1.2.
4. Testar o comando global e a suíte com 1.1.2.
5. Atualizar setup, UI, roadmap, CHANGELOG e estado.

## Aceite

- [x] `xl-utils` global abre o app.
- [x] A janela pode ficar no monitor secundário; o app não a reposiciona.
- [x] Flet 1.1.2 no `.venv`, no lock e no tool; testes verdes.
- [x] Docs, lint e testes verdes.

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `CURRENT.md`, esta spec, `app.py` e `pyproject.toml`.

## Arquivos prováveis

- `pyproject.toml`, `uv.lock`
- `src/xl_utils/app.py`, `tests/test_drive_session.py`
- `docs/guide/setup.md`, `docs/reference/ui.md`, `docs/roadmap/main.md`,
  `docs/state/CURRENT.md`, `CHANGELOG.md`

## Riscos

- O tool global precisa ser reinstalado sempre que uma dependência nova entrar.
- Atualizações futuras do Flet podem exigir ajustes; o lock registra a versão
  testada.

## Próximo depois desta

S9b — Drive II: link/seletor e escrita do resultado.
