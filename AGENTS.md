# AGENTS.md — xl_Utils

Aplicativo desktop em Flet que reúne quatro utilitários de planilha:
tratamento de texto (inclui remoção de emojis), extração de CNJ, recorte e
mesclagem.

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

Estado: `docs/state/CURRENT.md` · futuro: `docs/roadmap/main.md` · decisões:
`docs/adr/`. Skills: `session-start` e `project-context-init`.

## Estrutura

```text
src/xl_utils/
  app.py            shell Flet e navegação
  core/             regras puras: io, mime, paths, text, tools/
  controllers/      ponte entre UI e core
  ui/pages/         Início + uma página por ferramenta
  ui/components/    entrada, resultado, prévia e layout
  ui/theme.py       tokens e tema Dracula
  shared/           logging, config, clipboard
tests/              testes do core
scripts/            automação de docs
docs/               mapa, estado, roadmap, guias, ADRs
*.py (raiz)         scripts legados, migrados um a um para src/
```

## Convenções

- Código e identificadores em inglês; UI e documentação em PT-BR.
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
- Planilhas de teste usam dados fictícios.
- `output/` e artefatos locais ficam fora do Git.
