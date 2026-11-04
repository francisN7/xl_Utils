# xl_Utils

Aplicativo desktop que reúne pequenos utilitários de planilha em uma única
interface. O núcleo é compartilhado: toda leitura passa por um pipeline de
texto seguro antes de chegar à ferramenta.

![Tela inicial do xl_Utils](docs/assets/ui-base.png)

## Ferramentas

| Ferramenta | O que faz | Estado |
|---|---|---|
| Tratamento de Texto | Converte tudo para texto, remove emojis e repara metadados | em migração |
| Extrair CNJs | Encontra e padroniza numerações CNJ em uma planilha | em migração |
| Recortar Planilha | Divide uma planilha em arquivos por quantidade de linhas | em migração |
| Mesclar Planilhas | Unifica arquivos com o mesmo cabeçalho ou abas de um arquivo | em migração |

## Requisitos

- [uv](https://docs.astral.sh/uv/) — o Python 3.15 é baixado e gerenciado por ele.
- Node.js apenas para o check de documentação.

## Como rodar

```bash
uv sync
uv run xl-utils
```

Alternativa sem o entry point:

```bash
uv run python -m xl_utils
```

## Desenvolvimento

```bash
uv run ruff check src tests
uv run pytest
node scripts/check-docs.mjs
```

## Estrutura

```text
src/xl_utils/
  app.py       shell Flet e navegação
  core/        regras puras (io, mime, paths, text, tools)
  controllers/ orquestração entre UI e core
  ui/          páginas e componentes Flet
  shared/      logging, config e clipboard
tests/         testes do core
docs/          documentação e memória entre sessões
```

## Documentação

O mapa completo está em [`docs/README.md`](docs/README.md). Para retomar o
projeto, leia [`AGENTS.md`](AGENTS.md) e
[`docs/state/CURRENT.md`](docs/state/CURRENT.md).

## Licença

Ainda não definida.
