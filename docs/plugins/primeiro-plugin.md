# Primeiro plugin

Este guia cria, empacota e executa o plugin de referência
[`exemplos/hello`](exemplos/hello), o mesmo que os testes do repositório usam.

## 1. Pastas

```text
hello/
  plugin.toml     manifesto: identidade, entrada, permissões e UI
  lib/
    main.py       código Python puro, importado só ao executar
```

`lib/` contém apenas `.py`. Imports entre arquivos do plugin são **relativos**
(`from .helper import contar`): o host cria um pacote sintético e não coloca
`lib/` no `sys.path`.

## 2. Manifesto

```toml
[plugin]
id = "exemplo.hello"
name = "Hello Planilha"
version = "1.0.0"
api_version = 1
entrypoint = "main:run"
description = "Conta as linhas de cada aba escolhida e devolve um resumo."
authors = ["xl_Utils"]

[ui]
multiple_files = true
default_all_sheets = true
note = "Marca as abas que quer contar; o resultado tem uma linha por aba."

[permissions]
network = false
filesystem = "read"
subprocess = false
```

- `entrypoint = "main:run"` procura `lib/main.py` e a função `run`.
- `[ui]` decide quais arquivos a página mostra; `[[options]]` cria os controles.
- `[permissions]` é declaração para o aviso da tela, não sandbox.

Todos os campos estão em [`manifesto.md`](manifesto.md); a montagem da página,
em [`ui-e-opcoes.md`](ui-e-opcoes.md).

## 3. Código

```python
import pandas as pd

from xl_utils.shared.plugins.api import PluginRequest, PluginResult


def run(request: PluginRequest) -> PluginResult:
    pairs = [
        (path, name)
        for path, names in request.sheets.items()
        for name in names
    ]
    request.progress.start(len(pairs))
    rows = []
    for path, name in pairs:
        if request.cancel.cancelled:
            break
        request.progress.file_started(f"{path.name} · {name}")
        frame = pd.read_excel(path, sheet_name=name, engine="openpyxl")
        rows.append({"arquivo": path.name, "aba": name, "linhas": len(frame)})
        request.log.info(f"{path.name} · {name}: {len(frame)} linha(s)")
        request.progress.file_done(f"{path.name} · {name}")
    request.progress.finish()
    if not rows:
        return PluginResult(message="Nenhuma aba selecionada.")
    return PluginResult(
        frames={"resumo": pd.DataFrame(rows)},
        message=f"{len(rows)} aba(s) lida(s)",
    )
```

Regras da função: um parâmetro posicional, nada de Flet, `print`, diálogo ou
`sys.exit`. Devolva `PluginResult`; exceções viram erro na tela e no
diagnóstico. Veja [`api.md`](api.md).

## 4. Empacotar e instalar

No repositório do app:

```powershell
uv run python scripts/plugin_cli.py pack docs/plugins/exemplos/hello -o build/hello.tar.xz
uv run python scripts/plugin_cli.py check build/hello.tar.xz
uv run python scripts/plugin_cli.py install build/hello.tar.xz
```

O `pack` grava também `build/hello.tar.xz.sha256`. O sidecar precisa ficar ao
lado do pacote na instalação.

## 5. Abrir no app

1. Na barra lateral, abra **Plugins**.
2. Clique em **Instalar plugin** e escolha o `.tar.xz` (com o sidecar ao lado).
3. Confira nome, versão, API e permissões; confirme.
4. Clique em **Abrir**, marque as abas e clique em **Executar**.

O código do plugin **não** é importado ao abrir o app, listar ou montar a
página: só no primeiro **Executar**. As execuções seguintes reusam o módulo.

## 6. O que cada ação lê

| Ação | O que acontece |
|---|---|
| abrir a área e listar | lê `plugin.toml`; não importa `lib/` |
| abrir a ferramenta | monta a página a partir de `[ui]` e `[[options]]` |
| executar | importa `lib/`, confere `run` e chama `run(request)` |
| instalar | confere sidecar, manifesto, caminhos e limites; extrai |
| remover | apaga `plugins/<id>/`, inclusive `data/` |

## 7. Erros de código

Aparecem na página, no log e no diagnóstico — o app continua aberto.

| Código | Quando |
|---|---|
| `run_missing` | o módulo carregou, mas não existe a função do entrypoint |
| `run_signature` | `run` não recebe exatamente um parâmetro posicional |
| `plugin_import_failed` | exceção durante o import de `lib/` |
| `result_invalid` | `run` devolveu algo que não é `PluginResult` |
| `option_invalid` | um valor de `[[options]]` não passou na validação |

Falha dura (segfault, `os._exit`, memória esgotada) não é recuperável: o plugin
roda no mesmo processo.

## 8. Próximo passo

[`empacotar-testar.md`](empacotar-testar.md) cobre o CLI completo, os códigos de
erro de instalação e o fluxo de repositório privado com CI. Para opções
tipadas, slots nomeados e progresso, estude [`exemplos/com-opcoes`](exemplos/com-opcoes).
