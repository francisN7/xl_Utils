# S3a — Promover a UI a `main`

## Objetivo

Tornar a versão com UI a `main` e preservar a `main` antiga em `legacy`, com um
README de descontinuação no lugar do README atual.

## Fora de escopo

Empacotamento, instalador e release; reescrever a história; remover os scripts
antigos da branch legada; marcar a branch no GitHub (fica na S3b).

## Tarefas

1. Confirmar que `main` é ancestral de `feat/ui` com
   `git merge-base --is-ancestor main feat/ui`. Se não for, integrar `main` em
   `feat/ui` e resolver os conflitos antes de publicar.
2. Criar `legacy` no commit atual de `main` e publicar a branch.
3. Na `legacy`, substituir todo o `README.md` por um aviso curto de
   descontinuação: versão sem UI, sem manutenção, apenas histórica, com link
   para a `main`. Commitar só o README.
4. Avançar `main` até `feat/ui` com `git merge --ff-only` (sem merge commit se
   o histórico permitir) e publicar.
5. Confirmar que `main` é a branch padrão; remover `feat/ui` local e remota
   depois de validar que o conteúdo está na `main`.
6. Na `main`, mencionar a `legacy` no README ou na documentação de
   desenvolvimento, para quem chegar por link antigo.
7. Rodar `ruff`, `pytest` e `docs:check` na `main`, atualizar `CURRENT.md`,
   marcar S3a no roadmap e registrar no `CHANGELOG.md`.

## Aceite

- [ ] `main` aponta para a versão com UI e é a branch padrão
- [ ] `legacy` parte do commit antigo e só acrescenta o aviso de descontinuação
- [ ] o README da `legacy` não descreve mais o projeto ativo
- [ ] `feat/ui` removida após o merge
- [ ] histórico antigo continua acessível na `legacy`
- [ ] `ruff`, `pytest` e `docs:check` verdes na `main`

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec, `README.md`,
`docs/roadmap/main.md` e a saída de `git branch -a`/`git log --oneline --graph`.
Não abrir o código antigo.

## Arquivos prováveis

- `README.md` (na `legacy` e uma menção na `main`)
- `docs/state/CURRENT.md`
- `docs/roadmap/main.md`
- `CHANGELOG.md`

## Riscos

- Fazer merge em vez de fast-forward sem necessidade cria um commit extra;
  conferir o grafo antes.
- Um push acidental na `legacy` depois do aviso quebra a proposta de histórico;
  proteger a branch na S3b.
- O GitHub **não** tem um selo nativo de “legacy” no seletor de branches; o nome
  `legacy`, a tag e o README são o sinal disponível.
- `feat/ui` é a branch de trabalho atual; só apagar depois de confirmar a
  `main` publicada.
- Nunca usar `push --force` na `main`.

## Próximo depois desta

S3b — sinalizar a `legacy` no GitHub: tag `legacy-v1`, ruleset/proteção e
documentação do aviso.
