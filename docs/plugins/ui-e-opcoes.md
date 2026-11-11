# UI declarativa e opções

O plugin não desenha a tela. O manifesto declara **quais arquivos** e **quais
opções** a ferramenta aceita, e o host monta a página com o mesmo `ToolLayout`
das cinco ferramentas nativas. Isso mantém tema, espaçamento, prévia, log e
salvamento consistentes, e evita acoplar o plugin à versão do Flet.

## O que o host monta

1. Cabeçalho com `name` e `description`.
2. A dica `note`, se houver.
3. O seletor de arquivos: genérico ou slots nomeados.
4. Os controles de `[[options]]`, na ordem do manifesto.
5. O botão de executar, o painel de resultado e o log.

A ordem dos controles é a ordem das tabelas no TOML. Não existe layout livre,
abas internas, gráficos ou botões extras na API 1.

## Arquivos: genérico ou nomeado

### Seletor genérico

```toml
[ui]
multiple_files = true
default_all_sheets = true
```

- `multiple_files = false` mostra um arquivo; `true` mostra uma lista.
- `default_all_sheets = true` marca todas as abas dos livros selecionados.
- Se o plugin não declarar `[[ui.inputs]]`, o seletor genérico aparece.
- Os arquivos chegam em `request.files`; as abas, em `request.sheets`.

### Slots nomeados

Use quando cada arquivo tem um papel fixo:

```toml
[ui]
multiple_files = false
default_all_sheets = false

[[ui.inputs]]
key = "agenda"
label = "AGENDA"
required = true

[[ui.inputs]]
key = "financeiro"
label = "FINANCEIRO"
required = true
```

- Até 8 slots.
- `key` é o nome usado em `request.inputs["agenda"]`; `label` é o texto da tela.
- `required = false` permite executar sem aquele arquivo; o valor ausente não
  entra no mapping.
- Com slots nomeados, o seletor genérico não aparece e `multiple_files` deve ser
  `false`.
- As abas escolhidas para cada slot continuam em `request.sheets`, pela chave
  `Path`.

## Opções

```toml
[[options]]
key = "modo"
label = "Modo"
type = "choice"
default = "resumo"
choices = ["resumo", "detalhado"]
help = "Detalhado mantém uma linha por registro."
```

- Até 20 opções; `key` único e estável (é a chave em `request.options`).
- A ordem no TOML é a ordem na tela.
- `label` é exibição; `help` vira dica curta.
- O host valida o valor antes de chamar `run`; o plugin recebe o tipo já
  convertido.

### Tipos

| `type` | Controle | Valor em `request.options` | Regras |
|---|---|---|---|
| `text` | campo de texto | `str` | até 500 caracteres; default `""` |
| `int` | campo numérico | `int` | `min`/`max` opcionais; default `0` |
| `bool` | caixa de seleção | `bool` | default `false` |
| `choice` | lista suspensa | `str` | `choices` obrigatório, 2–50 itens; `default` obrigatório e presente na lista |

- `choices` só vale em `choice`; `min`/`max` só em `int`.
- `default` de `int` precisa caber em `min`/`max`.
- `choices` não aceita itens vazios, repetidos ou com mais de 60 caracteres.
- `text` não tem `choices`; o limite de 500 é fixo na API 1.

## Exemplo de página completa

```toml
[plugin]
id = "autor.resumo"
name = "Resumo"
version = "1.0.0"
api_version = 1
entrypoint = "main:run"
description = "Gera um resumo a partir de uma planilha."

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

[[options]]
key = "limite"
label = "Máximo de linhas"
type = "int"
default = 100
min = 1
max = 10000
```

Nesse exemplo, `request.inputs["origem"]` é a planilha, `request.sheets` traz as
abas marcadas e `request.options` chega como
`{"modo": "resumo", "limite": 100}`.

## O que não existe na API 1

- Controles Flet personalizados.
- Opções condicionais, visibilidade dinâmica ou dependência entre campos.
- Filtros de extensão por slot, arrastar e soltar ou múltiplos slots do mesmo
  tipo.
- Abas internas, gráficos, botões extras ou ações próprias na página.
- Internacionalização: os rótulos são os do manifesto, em PT-BR.

Esses itens exigem uma versão nova da API; não tente contornar com código na
função `run`, porque ela roda sem acesso à UI.

## Erros de UI

Um manifesto com `multiple_files = true` e slots nomeados, `choice` sem
`default`, `choices` repetido, `min > max`, `key` duplicado ou tipo desconhecido
é recusado inteiro com `manifest_invalid` ou `duplicate_option` antes de
qualquer instalação. Veja a tabela de erros em
[`manifesto.md`](manifesto.md).
