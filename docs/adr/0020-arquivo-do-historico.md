# ADR 0020 — Histórico em texto, uma página por ciclo

- **Status:** aceita
- **Data:** 2026-11-08

## Contexto

No fechamento do ciclo 0006 a documentação tinha 52 arquivos e 207 KB, sendo
40 KB de specs de sessão (14 arquivos fechados no working tree) e 28 KB em
`roadmap/`, onde o `main.md` ativo convivia com cinco páginas de ciclos
fechados. A tendência é crescer a cada sessão: só o ciclo 0009 teve nove specs.

Foi proposta uma alternativa: compactar `roadmap/`, `sessions/` e afins em `.7z`
com compressão máxima a cada lote de dez sessões, guardar o pacote numa pasta de
histórico e apagar os originais.

## Decisão

- **Fronteira do arquivo é o ciclo, não a sessão.** Ciclo fechado vira uma
  página `docs/history/NNNN-titulo.md`, em texto, com o resumo das entregas.
- **Spec não tem arquivo permanente.** Vive enquanto a sessão está aberta; todas
  as specs do ciclo saem do working tree no fechamento. O Git guarda o texto e
  a página do ciclo guarda o resumo.
- **Nada comprimido no repositório.** Sem `.7z`, `.zip` ou pacote de docs
  versionado. O Git já comprime e mantém diff, busca e `git show`.
- **`docs/roadmap/` fica só com o futuro:** `main.md` e o guia do processo. O
  índice dos ciclos fechados é `docs/history/README.md`.
- **Páginas de histórico não são reescritas** nem têm links cobrados pelo
  `scripts/check-docs.mjs`; links para specs viram “histórico no Git”, sem
  caminho.
- **O site público não serve o histórico:** `history` entra no `_config.yml`.

## Consequências

- O working tree não cresce com spec antiga nem com ciclo fechado; o contexto
  recente continua curto (`AGENTS.md`, `CURRENT.md` e a spec da vez).
- O passado é consultável com `grep`, `git log -- docs/history` e
  `git log -- docs/sessions`, sem extrair nada.
- Custos: o resumo do ciclo precisa ser escrito no fechamento (antes a spec
  servia de registro); sem pacote único para baixar, quem quiser o dump usa
  `git archive`.
- Um `.7z` de release continua possível como **artefato** de Release, gerado
  por script fora do repositório; não é o arquivo do projeto.

## Alternativas

- **`.7z` a cada dez sessões, commitado:** reduz bytes no disco (poucos), mas
  cria binário sem diff nem busca, duplica o histórico do Git e quebra o
  protocolo de leitura por seção. Descartada.
- **Pasta de histórico por sessão:** mantém tudo, mas multiplica arquivos e
  dificulta o contexto recente, que é o que a sessão realmente precisa.
  Descartada.
- **Só o Git, sem página de ciclo:** menos trabalho no fechamento, mas o resumo
  passaria a depender de ler diffs; a página numerada é o índice barato do
  passado.
