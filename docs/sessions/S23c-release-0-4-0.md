# S23c — Release 0.4.0 para Windows e Linux e fechamento do ciclo 0009

## Objetivo

Publicar a 0.4.0 com instalador Windows e AppImage Linux, gerados pelo
workflow da S23b, e fechar o ciclo 0009; o 0010 nasce limpo, com a S24.

## Fora de escopo

- Picker JS do Drive (S24).
- Mudança de UI ou de comportamento; só correção que bloqueie a release.
- README e site (S22b); o badge de release se atualiza sozinho.

## Tarefas

1. Versão 0.4.0 em `pyproject.toml`, `src/xl_utils/__init__.py` e
   `installer/xl_utils.iss` (comentário e `#define`); `uv lock` regenera o
   `uv.lock` (nunca à mão). Os `0.3.0` dos testes de plugin são dado de teste:
   conferir antes de trocar.
2. `CHANGELOG.md`: “Não lançado” vira `## [0.4.0] — <data>`, só com o que é
   visível desde a 0.3.0 (plugins, API 2, painel de contas, foto e apelido,
   versão Linux com chaveiro, divisão acima de 1.000.000 linhas).
3. Push e disparo do `release.yml` (`confirmar: build`), os dois com o OK do
   dono; baixar os artefatos para `artifacts/release/` (fora do Git).
4. Conferir os SHA-256 e abrir o AppImage no Linux do dono; Windows fica só com
   o smoke test do CI.
5. Notas (`artifacts/release/notes.md`): requisitos (Windows 10/11 x64; Linux
   x86_64 com GTK 3), tamanhos, checksums, aviso de SmartScreen e aviso de que
   o Windows foi validado só pelo CI. `gh release create v0.4.0` com os dois
   arquivos e `SHA256SUMS.txt`, pelo dono.
6. Fechar o ciclo: `git mv docs/roadmap/main.md
   docs/roadmap/0009-investigacoes-de-ui.md` com cabeçalho de histórico; novo
   `main.md` (ciclo 0010) com o backlog vivo (S24, Picker só com planilhas,
   Ajuda ( i ), Sobre); linha no `docs/roadmap/README.md`.

## Aceite

- [ ] 0.4.0 nos três lugares; `uv lock` sem diff inesperado.
- [ ] CHANGELOG com a seção 0.4.0 e “Não lançado” vazio.
- [ ] Artefatos do workflow com smoke test verde e checksums conferidos.
- [ ] AppImage 0.4.0 aberto no Linux do dono.
- [ ] Release `v0.4.0` publicada com Windows e Linux (dono).
- [ ] Ciclo 0009 arquivado; `main.md` novo com a S24 como próxima.
- [ ] `ruff`, `pytest` e `uv run python scripts/check_docs.py` verdes.

## Orçamento de contexto (≤90 linhas)

`docs/guide/release-{windows,linux}.md` (Publicação), `CHANGELOG.md` (só “Não
lançado”), `pyproject.toml`, topo de `installer/xl_utils.iss`,
`docs/roadmap/main.md` e `docs/roadmap/README.md`.

## Arquivos prováveis

- `pyproject.toml`, `uv.lock`, `src/xl_utils/__init__.py`,
  `installer/xl_utils.iss`
- `CHANGELOG.md`, `docs/roadmap/{main,README,0009-investigacoes-de-ui}.md`
- `artifacts/release/` (fora do Git)

## Riscos

- Sem conferência humana no Windows: login do Drive e foto podem falhar só lá.
  As notas avisam; o primeiro problema real vira 0.4.1.
- Artefato do Actions expira em 7 dias: baixar logo depois do disparo.
- O build instala as versões do `uv.lock` (S23b): o `uv lock` da tarefa 1 não
  pode subir o Flet sem conferir o patch do `flet-cli` no `build_windows.ps1`.
- Publicar exige push: nunca empurrar sem o OK do dono.

## Próximo depois desta

Ciclo 0010 — S24, Picker JS do Drive (`docs/sessions/S24-seletor-do-drive.md`).
