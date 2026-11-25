# xl_Utils

Aplicativo desktop que reúne pequenos utilitários de planilha em uma única
interface. O núcleo é compartilhado: toda leitura passa por um pipeline de
texto seguro antes de chegar à ferramenta.

## Instalação (Windows)

Baixe o instalador da última versão em
[Releases](https://github.com/francisN7/xl_Utils/releases/latest) e confira o
SHA-256 publicado junto. É uma instalação por usuário (sem administrador), com
entrada no menu Iniciar e atalho opcional na área de trabalho; Python e `uv` não
são necessários na máquina de destino.

## Ferramentas

| Ferramenta | O que faz | Estado |
|---|---|---|
| Tratamento de Texto | Converte tudo para texto, remove emojis e repara metadados | pronta |
| Extrair CNJs | Encontra e padroniza numerações CNJ em uma ou mais planilhas | pronta |
| Recortar Planilha | Divide planilhas em arquivos por quantidade de linhas | pronta |
| Mesclar Planilhas | Concatena as abas selecionadas com a origem de cada linha | pronta |

> **Plugins:** ferramentas de fluxo específico, que não servem a qualquer
> usuário, ficam fora do app e entram como plugins locais pela área **Plugins**
> (rodapé da barra lateral). O contrato está em [`docs/plugins/`](docs/plugins/README.md).

## Requisitos

- [uv](https://docs.astral.sh/uv/) — o Python 3.15 é baixado e gerenciado por ele.

## Como rodar

```bash
uv sync
uv run xl-utils
```

Alternativa sem o entry point:

```bash
uv run python -m xl_utils
```

Para chamar `xl-utils` de qualquer pasta (uma vez, apontando para este
checkout):

```bash
uv tool install --editable .
xl-utils
```

## Exemplo de uso

1. Abra o app, escolha uma ferramenta e anexe uma planilha pelo seletor nativo.
2. Confira as abas marcadas e ajuste as opções, quando existirem.
3. Execute, veja a prévia e só então salve em `output/` ou na pasta escolhida.

## Problemas comuns

- **A janela não abre:** confirme `flet[desktop]` no `pyproject.toml` e rode
  `uv sync`.
- **Python errado:** `uv python pin 3.15` e `uv sync` recriam o `.venv`.
- **Link quebrado nas docs:** `uv run python scripts/check_docs.py` mostra o arquivo e a
  linha; corrija o caminho relativo.

Mais detalhes em [setup e execução](docs/guide/setup.md#problemas-comuns).

## Desenvolvimento

```bash
uv run ruff check src tests
uv run pytest
uv run python scripts/check_docs.py
```

## Estrutura

```text
src/xl_utils/
  app.py       shell Flet e navegação
  core/        regras puras (io, mime, paths, text, tools)
  controllers/ orquestração entre UI e core
  ui/          páginas, componentes e tema
  configs/     modelo do cliente OAuth do Drive (padrão)
  shared/      log, config, progresso e abertura de pasta
tests/         testes do core e da UI (headless)
docs/          documentação e memória entre sessões
```

## Documentação

O mapa completo está em [`docs/README.md`](docs/README.md). Para entender o
código em ordem guiada, comece pelo
[code tour](docs/guide/code-tour.md). Para retomar o projeto, leia
[`AGENTS.md`](AGENTS.md) e [`docs/state/CURRENT.md`](docs/state/CURRENT.md).

## Branch `legacy`

A versão anterior, sem interface gráfica, fica na branch
[`legacy`](https://github.com/francisN7/xl_Utils/tree/legacy), mantida apenas
como registro histórico. Ela não recebe manutenção e está protegida contra
alterações.

O ponto estável é a tag
[`legacy-v1`](https://github.com/francisN7/xl_Utils/tree/legacy-v1).

## Segurança

O app processa planilhas locais; o Google Drive é opcional e só acessa arquivos
ou pastas que você escolher. Para relatar uma falha, use o relato privado de
vulnerabilidades do GitHub — o canal está descrito em [`SECURITY.md`](SECURITY.md).
Não abra issue pública com dados reais, credenciais ou passos que exponham
terceiros.

## Contribuindo

Este é um projeto pessoal e não há processo formal de contribuição. Sugestões e
relatos podem ser abertos como issue no repositório.

## Licença

O código é público para consulta, mas **não há licença de uso**. Todos os
direitos são reservados: não é permitido copiar, modificar ou distribuir sem
autorização por escrito. Para reutilizar, entre em contato pelo perfil do
GitHub.
