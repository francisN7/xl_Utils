# ADR 0019 — Publicação do site por workflow com filtro de caminho

- **Status:** aceita
- **Data:** 2026-11-08

## Contexto

O site público (`docs/index.html` e `docs/privacy.html`) estava no GitHub Pages
com origem **Deploy from a branch** (`main` / `/docs`). Nesse modo o GitHub
republica a cada push na `main`, mesmo quando só código, testes ou docs internos
mudam: cada commit virava um deployment `github-pages` e enchia a aba
Deployments sem alterar o site. O repositório também exige que toda action seja
fixada por SHA completo.

## Decisão

- A origem do Pages passa a ser **GitHub Actions**.
- `.github/workflows/pages.yml` copia só os HTML de topo de `docs/` para
  `_site`, empacota em `artifact.tar` e publica.
- O workflow roda apenas em push para `main` que toque `docs/*.html`, ou por
  `workflow_dispatch`.
- Nada de Jekyll: o site é estático e o artefato leva apenas o que deve ser
  servido. `docs/_config.yml` fica como fallback caso a origem volte à branch.
- `upload-pages-artifact` não é usado: é ação composta e referencia
  `actions/upload-artifact` por tag, o que a política de SHA completo recusa. O
  `tar` + `actions/upload-artifact` fixado reproduzem o mesmo artefato.
- As actions do Pages ficam fixadas por SHA e em Node 24; o job usa
  `ubuntu-24.04` para não depender da migração do `ubuntu-latest`.

## Consequências

- Push de código, testes ou docs internos não gera deployment nem run.
- Publicar exige tocar nos HTML ou rodar o workflow manualmente.
- A troca de origem é configuração do repositório (**Settings → Pages**), feita
  uma vez e documentada em `docs/guide/setup.md`.
- O CI continua em `ubuntu-latest` e com actions em Node 20; o aviso de
  depreciação só sai numa atualização própria.

## Alternativas

- **Continuar em “Deploy from a branch”:** zero configuração, mas sem filtro de
  caminho — era a origem do ruído.
- **Branch `gh-pages`:** publicaria só quando a branch mudasse, mas exigiria
  manter uma cópia do site fora de `docs/`; pior de manter.
- **Só deploy manual:** elimina o ruído, mas o site envelhece até alguém lembrar
  de rodar; o filtro mantém a atualização automática no caso que importa.
