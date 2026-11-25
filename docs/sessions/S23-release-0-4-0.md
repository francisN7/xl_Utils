# S23 — Release 0.4.0 e fechamento do ciclo 0009

## Objetivo

Publicar a 0.4.0 (instalador Windows com Pillow) e fechar o ciclo 0009; o 0010
nasce limpo, com o Picker JS (S24) como próxima sessão.

## Fora de escopo

- Picker JS do Drive (S24) e versão Linux (backlog).
- Mudança de UI ou de comportamento; só correção que bloqueie a release.
- README e site (S22b); o badge de release se atualiza sozinho.

## Tarefas

1. Versão 0.4.0 em `pyproject.toml`, `src/xl_utils/__init__.py` e
   `installer/xl_utils.iss` (comentário e `#define`); `uv lock` regenera o
   `uv.lock` (nunca à mão). Os `0.3.0` dos testes de plugin são dado de teste:
   conferir antes de trocar.
2. `CHANGELOG.md`: “Não lançado” vira `## [0.4.0] — <data>`, só com o que é
   visível desde a 0.3.0 (plugins, API 2, painel de contas, foto e apelido,
   chaveiro no Linux, divisão acima de 1.000.000 linhas).
3. Build no Windows pelo dono: `scripts/build_windows.ps1`, conferindo que o
   Pillow entra no pacote (foto da conta abre no executável).
4. Validação no Windows Sandbox (`docs/guide/release-windows.md` → Validação):
   instala, abre, quatro ferramentas, Plugins, foto e apelido da conta.
5. Notas (`artifacts/installer/notes.md`) e `gh release create v0.4.0` pelo
   dono, depois do push.
6. Fechar o ciclo: `git mv docs/roadmap/main.md
   docs/roadmap/0009-investigacoes-de-ui.md` com cabeçalho de histórico; novo
   `main.md` (ciclo 0010) com o backlog vivo (S24, versão Linux, Picker só com
   planilhas); linha no `docs/roadmap/README.md`.

## Aceite

- [ ] 0.4.0 nos três lugares; `uv lock` sem diff inesperado.
- [ ] CHANGELOG com a seção 0.4.0 e “Não lançado” vazio.
- [ ] Instalador e `SHA256SUMS.txt` gerados; Sandbox conferido pelo dono.
- [ ] Release `v0.4.0` publicada (dono).
- [ ] Ciclo 0009 arquivado; `main.md` novo com a S24 como próxima.
- [ ] `ruff`, `pytest` e `uv run python scripts/check_docs.py` verdes.

## Orçamento de contexto (≤90 linhas)

`docs/guide/release-windows.md` (Build, Validação, Publicação), `CHANGELOG.md`
(só “Não lançado”), `pyproject.toml`, o topo de `installer/xl_utils.iss`,
`docs/roadmap/main.md` e `docs/roadmap/README.md`. Do build, só o trecho de
dependências de `scripts/build_windows.ps1`.

## Arquivos prováveis

- `pyproject.toml`, `uv.lock`, `src/xl_utils/__init__.py`,
  `installer/xl_utils.iss`
- `CHANGELOG.md`, `docs/roadmap/{main,README,0009-investigacoes-de-ui}.md`
- `artifacts/installer/` (fora do Git)

## Riscos

- Build e Sandbox só rodam no Windows: dependem do dono.
- Pillow no `flet pack`: falta de `PIL._imaging` só aparece no executável.
- `flet pack` apaga `build/`; exige `_lzma.pyd` e `python3t.dll`; `.iss` é
  UTF-8 com BOM.
- Publicar exige push: nunca empurrar sem o OK do dono.

## Próximo depois desta

Ciclo 0010 — S24, Picker JS do Drive (`docs/sessions/S24-seletor-do-drive.md`).
