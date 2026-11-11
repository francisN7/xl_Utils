# O manifesto `plugin.toml`

O manifesto é o contrato declarativo do plugin. Ele fica na **raiz** do tar,
é lido com `tomllib` (stdlib) e nunca executa código. Tudo o que o host precisa
saber para validar, instalar e montar a página está aqui.

## Exemplo completo

```toml
[plugin]
id = "autor.ferramenta"
name = "Minha Ferramenta"
version = "1.0.0"
api_version = 1
entrypoint = "main:run"
description = "Converte a aba escolhida em uma tabela de resumo."
authors = ["Autor"]
min_app_version = "0.4.0"
dependencies = ["pandas"]
license = "MIT"
homepage = "https://exemplo.invalid/ferramenta"

[permissions]
network = false
filesystem = "read"
subprocess = false

[ui]
multiple_files = false
default_all_sheets = true
note = "A primeira linha é usada como cabeçalho."

[[ui.inputs]]
key = "origem"
label = "Planilha de origem"
required = true

[[options]]
key = "modo"
label = "Modo"
type = "choice"
default = "resumo"
choices = ["resumo", "detalhado"]
help = "Detalhado mantém uma linha por registro."
```

## `[plugin]`

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `id` | string | sim | `autor.ferramenta`, 3–64, minúsculas, `[a-z0-9._-]`, sem `..`, sem nome reservado do Windows |
| `name` | string | sim | 1–80 caracteres, sem controle |
| `version` | string | sim | SemVer `X.Y.Z` |
| `api_version` | inteiro | sim | versão da API do host; esta versão aceita `1` |
| `entrypoint` | string | sim | `modulo:funcao`, resolvido dentro de `lib/` |
| `description` | string | sim | 1–500 caracteres |
| `authors` | lista de strings | não | até 10 nomes, 1–80 cada |
| `min_app_version` | string | não | SemVer; recusa se o app for mais antigo |
| `dependencies` | lista de strings | não | até 20 nomes de distribuições que o host deve ter |
| `license` | string | não | 1–40 caracteres; informativo |
| `homepage` | string | não | URL `http(s)`, 1–200 |

O `id` vira o nome da pasta em `plugins/`. Ele não pode ser `con`, `nul`,
`com1` etc., mesmo em minúsculas. O `name` é só exibição.

`dependencies` **não instala nada**. O host confere se cada distribuição existe
com `importlib.metadata`; versões e instalação por `pip` ficam fora desta API.
Se faltar uma dependência, a instalação falha com `missing_dependency`.

## `[permissions]`

Tabela opcional. Os padrões são conservadores:

| Campo | Tipo | Padrão | Significado |
|---|---|---|---|
| `network` | booleano | `false` | o plugin pode usar a rede |
| `filesystem` | string | `"none"` | `"none"`, `"read"` ou `"write"` |
| `subprocess` | booleano | `false` | o plugin pode iniciar processos |

São **declarações**, não bloqueios. O plugin roda no mesmo processo e tem os
direitos do usuário; a UI da S14 mostra o aviso. O install não tenta impedir
rede, leitura ou subprocesso em tempo de execução. Veja
[`permissoes-e-seguranca.md`](permissoes-e-seguranca.md).

## `[ui]`

Tabela opcional que descreve a página. O host monta o layout; o plugin não
importa Flet.

| Campo | Tipo | Padrão | Efeito |
|---|---|---|---|
| `multiple_files` | booleano | `false` | seletor genérico aceita vários arquivos |
| `default_all_sheets` | booleano | `false` | marca todas as abas por padrão |
| `note` | string | `""` | dica curta, até 200 caracteres |

### Entradas nomeadas: `[[ui.inputs]]`

Use quando a ferramenta precisa de papéis fixos, como AGENDA e FINANCEIRO.
Cada tabela declara um slot de arquivo:

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `key` | string | sim | `^[a-z][a-z0-9_]{0,31}$`, único |
| `label` | string | sim | 1–40 caracteres |
| `required` | booleano | não | padrão `true` |

No máximo 8 entradas. Com `[[ui.inputs]]`, o seletor genérico não aparece e
`multiple_files` deve continuar `false`. A UI, os filtros e a ordem dos slots
são responsabilidade do host.

## `[[options]]`

Opções viram controles na página e chegam em `request.options`, já convertidas
para o tipo declarado. No máximo 20.

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `key` | string | sim | `^[a-z][a-z0-9_]{0,31}$`, único |
| `label` | string | sim | 1–60 caracteres |
| `type` | string | sim | `"text"`, `"int"`, `"bool"` ou `"choice"` |
| `default` | depende | depende | ver abaixo |
| `choices` | lista | só em `choice` | 2–50 strings únicas, 1–60 cada |
| `help` | string | não | 0–200 caracteres |
| `min` | inteiro | não | só em `int`; limite inferior |
| `max` | inteiro | não | só em `int`; limite superior |

Padrões e regras por tipo:

- `text`: `default` é string, padrão `""`; o valor final é limitado a 500
  caracteres.
- `int`: `default` é inteiro, padrão `0`; `min`/`max` opcionais; o default
  precisa caber no intervalo.
- `bool`: `default` é booleano, padrão `false`.
- `choice`: `default` é obrigatório e precisa estar em `choices`.

`choices` só é aceito em `choice`; `min`/`max` só em `int`. O host não faz
opções dinâmicas nem esconde campos: a página é estática por enquanto.

## Resolução do entrypoint

`entrypoint = "main:run"` procura `lib/main.py` e a função `run`. Um módulo com
pacote usa `pkg.mod:run`, que procura `lib/pkg/mod.py` ou
`lib/pkg/mod/__init__.py`.

A instalação confere se o arquivo do módulo existe, mas **não importa** o
código. A existência da função e a assinatura correta são conferidas no
carregamento, na S14; um erro ali isola o plugin e aparece no log.

## Validação e erros

O manifesto é recusado inteiro se qualquer regra falhar. Chaves e tabelas
desconhecidas são recusadas para pegar erro de digitação; um campo novo exige
`api_version` novo. O TOML é UTF-8 e chaves duplicadas são erro do parser.

| Código | Quando |
|---|---|
| `manifest_missing` | não existe `plugin.toml` na raiz |
| `manifest_too_large` | passa de 256 KB |
| `manifest_invalid` | TOML quebrado, campo faltando, tipo ou valor inválido |
| `invalid_id` | `id` fora da regra ou nome reservado |
| `duplicate_option` | `key` repetido em opções ou entradas |
| `unsupported_api` | `api_version` não suportado pelo host |
| `app_too_old` | `min_app_version` maior que a versão do app |
| `missing_dependency` | distribuição declarada não está instalada |
| `entrypoint_missing` | arquivo do entrypoint não existe em `lib/` |

O parser devolve um modelo tipado; nenhum código do plugin é executado durante
a leitura.
