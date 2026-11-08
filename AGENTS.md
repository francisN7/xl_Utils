# AGENTS.md — xl_Utils

Aplicativo desktop em Flet que reúne cinco utilitários de planilha:
tratamento de texto (inclui remoção de emojis), extração de CNJ, recorte,
mesclagem e vinculação entre AGENDA, FINANCEIRO, PROCESSOS e CLIENTES.

**Stack:** Python 3.15 · uv · Flet 1.x · pandas 3.x · pytest · ruff

## Protocolo de contexto

1. No início da sessão, leia **só**: este arquivo, `docs/state/CURRENT.md` e a
   spec da sessão em `docs/sessions/`.
2. Para qualquer outro assunto, ache a **seção** em `docs/README.md` e leia só
   ela. Nunca despeje um arquivo grande no contexto.
3. Prefira `grep`/`glob` e leituras parciais (`offset`/`limit`).
4. No fim da sessão, obrigatoriamente:
   - rodar `uv run ruff check src tests`, `uv run pytest` e
     `node scripts/check-docs.mjs`;
   - atualizar `docs/state/CURRENT.md`, marcar a sessão em
     `docs/roadmap/main.md` e escrever uma linha no `CHANGELOG.md`;
   - criar/atualizar um ADR se a decisão for relevante;
   - escrever a spec da próxima sessão;
   - commitar com `SXX: resumo curto`.
5. Se o contexto encher no meio, salve o estado em `CURRENT.md` e recomece.
6. Revisão profunda de todos os `.md` é a skill `docs-review`: só sob pedido
   explícito, nunca no fim da sessão.

## Entrega final

Toda resposta que conclui trabalho termina com uma linha de estado:

- **Sessão fechada** — protocolo do item 4 aplicado; nada pendente. Não peça
  encerramento.
- **Sessão aberta** — a entrega não rodou o protocolo; peça “encerrar sessão”.
- **Sem sessão** — ajuste de processo/docs que não mexe em `CURRENT.md` nem no
  roadmap.

Nunca esconder validação vermelha atrás do selo.

Estado: `docs/state/CURRENT.md` · futuro: `docs/roadmap/main.md` · decisões:
`docs/adr/` · leitura do código: `docs/guide/code-tour.md`. Skills:
`session-start`, `project-context-init` e `docs-review` (só sob pedido
explícito).

## Estrutura

```text
src/xl_utils/
  app.py            shell Flet e navegação
  core/             regras puras: io, mime, paths, text, tools/
  controllers/      ponte entre UI e core
  ui/pages/         Início + uma página por ferramenta
  ui/components/    entrada, resultado, prévia e layout
  ui/theme.py       tokens e temas (Dracula/Alucard)
  configs/          headers.json empacotado (padrão, não estado)
  shared/           log, config, contas e Drive
tests/              testes do core e da UI (headless)
scripts/            automação de docs
docs/               mapa, estado, roadmap, guias, ADRs
```

## Convenções

- Identificadores e código em inglês; comentários, docstrings, UI e docs em
  PT-BR. Core, controllers, `ui/`, `shared/` e o shell já estão traduzidos.
- `core/` não importa Flet, não abre diálogos e não imprime no terminal.
- Páginas Flet só coletam entrada, chamam controller e exibem resultado.
- Regra de negócio fica em função pura testável, não na página.
- Toda ferramenta lê pelo pipeline do `all_str` (texto + emojis), antes da
  regra específica; quebras de linha são preservadas.
- Nunca renomear o arquivo original do usuário; detectar o tipo real e ler.
- Arquivos gerados não são editados à mão: `uv.lock`, `output/`, `dist/`.
- Commits pequenos, um por sessão.

## Comandos

| Ação | Comando |
|---|---|
| dev | `uv run xl-utils` |
| lint | `uv run ruff check src tests` |
| format | `uv run ruff format src tests` |
| test | `uv run pytest` |
| docs | `node scripts/check-docs.mjs` |
| sync | `uv sync` |
| nova dependência | `uv add <pacote>` |

## Definition of Done

- [ ] lint, testes e docs verdes
- [ ] ferramenta funciona com arquivo real
- [ ] docs afetados atualizados
- [ ] `CURRENT.md`, roadmap e `CHANGELOG.md` atualizados
- [ ] commit feito e enviado

## Segurança (repo público)

- Nunca commitar `.env`, credenciais, chaves, backups ou dados reais.
- Configuração pública em `configs/`; segredos em `%LOCALAPPDATA%/xl_utils/`.
- Planilhas de teste usam dados fictícios.
- `output/` e artefatos locais ficam fora do Git.
