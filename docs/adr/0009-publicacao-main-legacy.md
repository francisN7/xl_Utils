# ADR 0009 — Publicar a UI na `main` e preservar a `legacy`

- **Status:** aceita
- **Data:** 2026-11-04

## Contexto

A `main` ainda apontava para os scripts sem interface, enquanto todo o
aplicativo Flet vivia em `feat/ui`, 29 commits à frente. Quem clonava o
repositório recebia a versão errada. Apagar a história antiga ou reescrever a
`main` perderia o trabalho anterior e quebraria links já publicados.

## Decisão

- `main` avança até `feat/ui` por **fast-forward** (`git merge --ff-only`), sem
  commit de merge e sem `push --force`.
- O commit antigo da `main` vira a branch `legacy`, cujo único commit adicional
  troca o README por um aviso de descontinuação com link para a `main`.
- Depois de validar a `main` publicada, `feat/ui` é removida local e
  remotamente; o conteúdo dela já está na `main`.
- O README da `main` ganha uma seção curta apontando para a `legacy`.
- A branch padrão do GitHub continua sendo `main`.

## Consequências

- Clonar o repositório entrega o aplicativo com UI por padrão.
- O histórico antigo continua acessível em `legacy`, mas sem manutenção.
- Não há commit de merge nem reescrita: o grafo permanece linear e auditável.
- Tags e proteção da `legacy` ficam para a S3b; até lá, só o nome, o README e a
  documentação sinalizam a branch.

## Alternativas

- **Forçar a `main` para `feat/ui`:** reescreve a história publicada e quebra
  clones existentes; rejeitado.
- **Merge commit em vez de fast-forward:** cria um commit extra sem ganho, já
  que a `main` era ancestral; rejeitado.
- **Apagar a versão antiga:** perde o registro histórico dos scripts; rejeitado.
- **Manter `feat/ui` para sempre:** duplica a branch padrão e confunde qual é a
  versão ativa; rejeitado.
