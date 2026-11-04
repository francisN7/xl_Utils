# S3b — Sinalizar a `legacy` no GitHub

## Objetivo

Deixar a branch `legacy` identificável e travada no GitHub: tag `legacy-v1`,
ruleset de proteção e aviso documentado para quem chegar por link antigo.

## Fora de escopo

Empacotamento, instalador e release; reescrever ou apagar a história da
`legacy`; voltar a mexer no código antigo; marcar o ciclo como fechado.

## Tarefas

1. Criar a tag anotada `legacy-v1` no HEAD de `legacy` e publicar com
   `git push origin legacy-v1`.
2. Criar um ruleset para a branch `legacy` que bloqueie push, force-push e
   exclusão, mantendo leitura pública. Preferir `gh api`/interface do GitHub;
   registrar o ID ou o nome do ruleset na spec/CURRENT.
3. Confirmar que a regra vale: tentar um push vazio ou consultar o ruleset pela
   API e verificar que a atualização é recusada. Não deixar commit de teste.
4. Documentar o aviso: conferir a seção `legacy` do README da `main` e citar a
   tag `legacy-v1` como ponto estável. Se necessário, acrescentar uma linha em
   `docs/guide/setup.md`.
5. Rodar `ruff`, `pytest` e `docs:check` na `main`, atualizar `CURRENT.md`,
   marcar S3b no roadmap e registrar no `CHANGELOG.md`.

## Aceite

- [ ] tag `legacy-v1` publicada apontando para o commit do aviso na `legacy`
- [ ] ruleset ativo bloqueia push, force-push e exclusão da `legacy`
- [ ] leitura/clonagem da `legacy` continua pública
- [ ] README da `main` cita a tag como referência estável
- [ ] `ruff`, `pytest` e `docs:check` verdes na `main`

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec, o ADR 0009 e a saída de
`git tag`/`git log --oneline -3 legacy`. Não abrir o código antigo.

## Arquivos prováveis

- `README.md`, `docs/guide/setup.md`
- `docs/state/CURRENT.md`, `docs/roadmap/main.md`, `CHANGELOG.md`
- Configuração de ruleset no GitHub (sem arquivo no repositório, se possível)

## Riscos

- Proteção ampla demais pode travar a própria correção do README da `legacy`;
  limitar ao branch exato e revisar o bypass de administrador.
- Tag anotada criada no commit errado; conferir `git rev-parse legacy` antes.
- Ruleset que bloqueia leitura quebra o link do README; testar em janela
  anônima ou com `gh api` sem autenticação de escrita.
- Exclusão de tag não é coberta por proteção de branch; avaliar regra de tag ou
  aceitar o risco e registrar.

## Próximo depois desta

Fim da Fase 3. Avaliar o fechamento do ciclo 0002 e a próxima fase do roadmap.
