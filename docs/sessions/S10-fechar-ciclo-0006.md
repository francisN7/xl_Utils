# S10 — Fechar o ciclo 0006 e revisar o backlog

## Objetivo

Encerrar o ciclo **0006 — Backlog** com o Drive concluído, arquivar a página do
ciclo, tirar as specs fechadas do working tree e escolher o próximo ciclo com o
backlog revisado.

## Fora de escopo

- Implementar qualquer item do backlog (responsividade, e-mail longo, plugins).
- Reabrir decisões do Drive; a S9c já validou gravação, pasta e nomes livres.

## Tarefas

1. Rodar a validação completa e confirmar o app abrindo com uma gravação real no
   Drive (abrir, processar, salvar na pasta, repetir e ver `_001`).
2. Revisar o backlog em `docs/roadmap/main.md`: responsividade do Início e das
   ferramentas, e-mail longo no menu de perfis, seletor de arquivos integrado à
   UI, Drive sem consentimento repetido e sistema de plugins.
3. Fechar o ciclo: renomear `docs/roadmap/main.md` para `0006-backlog.md`,
   criar um `main.md` novo para o ciclo 0007 e atualizar
   `docs/roadmap/README.md`.
4. Remover do working tree as specs dos ciclos fechados (`docs/sessions/S7*`,
   `S8*`, `S9*`); o histórico fica no Git e o resumo na página numerada.
5. Atualizar `docs/README.md` (mapa e link da próxima spec), `CURRENT.md` e
   `CHANGELOG.md`.
6. Commitar com `S10: fecha o ciclo 0006`.

## Aceite

- [ ] Ciclo 0006 arquivado em página numerada; `main.md` novo aponta o 0007.
- [ ] Backlog revisado e priorizado, com a próxima sessão escrita.
- [ ] Specs fechadas fora de `docs/sessions/` e links vivos sem quebra.
- [ ] `ruff`, `pytest` e `node scripts/check-docs.mjs` verdes.
- [ ] Gravação real no Drive validada no app.

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec, `docs/roadmap/main.md`,
`docs/roadmap/README.md` e a seção do backlog. Não abrir código nem as cinco
páginas de ferramenta.

## Arquivos prováveis

- `docs/roadmap/main.md`, `docs/roadmap/0006-backlog.md`,
  `docs/roadmap/README.md`
- `docs/sessions/` (limpeza), `docs/README.md`, `docs/state/CURRENT.md`
- `CHANGELOG.md`

## Riscos

- Remover specs ainda referenciadas no `docs/README.md` ou no roadmap; rodar o
  `check-docs` depois.
- Fechar o ciclo sem validar a gravação real; a S9c tem o roteiro no teste
  `scripts/check-drive-picker.py --write`.
- Renomear a página do ciclo e esquecer o índice em `roadmap/README.md`.

## Próximo depois desta

Abrir o ciclo 0007 com a primeira sessão escolhida no backlog revisado.
