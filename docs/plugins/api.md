# A API do plugin

O host chama uma função só:

```python
def run(request: PluginRequest) -> PluginResult: ...
```

Ela roda **fora da UI thread**, no mesmo processo do app. O plugin não importa
Flet, não abre diálogo, não imprime e não chama `sys.exit`; ele recebe dados,
faz o trabalho e devolve tabelas. A página é montada pelo host a partir do
manifesto.

## `PluginRequest`

Importe de `xl_utils.shared.plugins.api`:

| Campo | Tipo | O que é |
|---|---|---|
| `files` | `tuple[Path, ...]` | arquivos do seletor genérico, na ordem da tela |
| `inputs` | `Mapping[str, Path]` | slots nomeados de `[[ui.inputs]]`, por `key` |
| `sheets` | `Mapping[Path, tuple[str, ...]]` | abas marcadas para cada arquivo |
| `options` | `Mapping[str, object]` | opções já convertidas para `str`, `int` ou `bool` |
| `log` | `RunLog` | log canônico da execução |
| `progress` | `ProgressReporter` | marcos ao vivo da barra |
| `cancel` | `CancelToken` | pedido cooperativo de parada |
| `data_dir` | `Path` | pasta `data/` do plugin, criada e persistente |
| `plugin_dir` | `Path` | raiz instalada do plugin; trate como somente leitura |
| `app_version` | `str` | versão do xl_Utils em execução |

`files` e `inputs` são alternativas: com `[[ui.inputs]]`, o seletor genérico não
aparece. `sheets` cobre os arquivos escolhidos nos dois modos; abas não se
aplicam a formatos que não são planilha.

## `PluginResult`

| Campo | Tipo | Padrão | O que é |
|---|---|---|---|
| `frames` | `Mapping[str, DataFrame]` | `{}` | tabelas de resultado; a chave vira o nome da aba na prévia |
| `message` | `str` | `""` | resumo curto exibido no cartão |
| `save_items` | `Sequence[SaveItem]` | `()` | livros opcionais para a ação de salvar |

`SaveItem` vem de `xl_utils.core.save` e tem `suggested_name`, `sheets` e
`output_dir`. Na dúvida, devolva só `frames` e `message`: o host monta a prévia
e a gravação como faz nas ferramentas nativas.

Recomendação: devolva células como texto, preservando quebras de linha, para
ficar igual ao pipeline das cinco ferramentas. A prévia aceita outros tipos,
mas texto é o mais previsível.

## Log, progresso e cancelamento

Use o log para o que deve ficar no diagnóstico:

```python
request.log.info("Lendo 3 arquivos")
request.log.warning("Aba vazia ignorada")
request.log.success("Resumo pronto")
```

Use o progresso para o que aparece ao vivo:

```python
request.progress.start(len(request.files))
request.progress.file_started(path.name)
# ... trabalho ...
request.progress.file_done(path.name)
request.progress.finish()
```

O host costuma chamar `start` e `finish`; o plugin chama `file_started`,
`file_done` e, se quiser, `stage(text)`. `progress.note(request.log, text)`
registra no log e mostra ao vivo ao mesmo tempo.

Nunca registre conteúdo de célula no log ou no progresso. Nomes de arquivo,
aba e coluna bastam para o diagnóstico.

Cancelamento é cooperativo:

```python
for path in request.files:
    if request.cancel.cancelled:
        break
    ...
```

O host sinaliza `request.cancel.cancelled`; o plugin decide onde parar. Devolva
o que já produziu e uma mensagem curta; não chame `sys.exit`.

## Erros

Levante uma exceção normal. O host captura, registra o tipo, a mensagem e o
traceback no diagnóstico e mostra o erro sem derrubar o app. Um erro dentro do
plugin não deve virar `print`, `os._exit` ou alteração global do processo.

Falhas duras (segfault, `os._exit`, consumo total de memória) não são
recuperáveis no mesmo processo; por isso a v1 trata plugin como código
confiável. Sandbox/subprocesso é decisão futura, não promessa desta API.

## Esqueleto

```python
from xl_utils.shared.plugins.api import PluginRequest, PluginResult


def run(request: PluginRequest) -> PluginResult:
    request.progress.start(len(request.files))
    frames = {}

    for path in request.files:
        if request.cancel.cancelled:
            break
        request.progress.file_started(path.name)
        request.log.info(f"Processando {path.name}")
        # leia com pandas/openpyxl e monte um DataFrame
        frames[path.stem] = ...
        request.progress.file_done(path.name)

    request.progress.finish()
    return PluginResult(frames=frames, message="Pronto")
```

A função só existe de verdade quando o plugin é carregado; instalar e listar
**não** importam `lib/`. O host importa na primeira execução, confere ali a
função e a assinatura, valida o retorno e isola a falha; a página é montada a
partir do manifesto.

## Compatibilidade

A API é versionada por `api_version` no manifesto. Esta versão aceita `1`.
Mudança de campo, de tipo, de semântica ou de schema de UI exige uma versão
nova; veja [`versionamento.md`](versionamento.md).
