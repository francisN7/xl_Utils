# Empacotar, conferir e testar

O CLI de autoria vive em `src/xl_utils/plugin_cli.py` e é instalado como
`xl-utils-plugin`. Dentro do repositório do app ele também roda pelo atalho
`scripts/plugin_cli.py`.

Ele **não executa código do plugin**: empacota, confere, instala e lista. Quem
chama `run(request)` é o app, na área Plugins.

## Comandos

| Comando | O que faz |
|---|---|
| `pack <pasta> -o <pacote.tar.xz>` | valida a pasta e grava o pacote + sidecar |
| `check <pacote.tar.xz>` | confere sidecar, manifesto, caminhos e limites |
| `install <pacote.tar.xz>` | instala em `%LOCALAPPDATA%/xl_utils/plugins/` |
| `list [--root <pasta>]` | lista válidos e inválidos |
| `uninstall <id> [--root <pasta>]` | remove o plugin, inclusive `data/` |

```powershell
uv run xl-utils-plugin pack . -o build/meu-plugin.tar.xz
uv run xl-utils-plugin check build/meu-plugin.tar.xz
uv run xl-utils-plugin install build/meu-plugin.tar.xz
uv run xl-utils-plugin list
uv run xl-utils-plugin uninstall autor.ferramenta
```

No checkout do app, troque `uv run xl-utils-plugin` por
`uv run python scripts/plugin_cli.py`.

`--root` aponta para uma pasta alternativa — útil para testar sem sujar a
instalação real:

```powershell
uv run xl-utils-plugin install build/meu-plugin.tar.xz --root .tmp/plugins
uv run xl-utils-plugin list --root .tmp/plugins
```

## Saída do `pack`

```text
Pacote: build/meu-plugin.tar.xz
Sidecar: build/meu-plugin.tar.xz.sha256
```

O sidecar é SHA-256 do arquivo, no formato `<hash>  <nome>`. Ele detecta
corrupção e troca por engano; **não** prova autoria. Guarde os dois arquivos
juntos — a instalação recusa pacote sem sidecar.

## Testar sem instalar

1. `pack` — pega erro de manifesto, caminho, binário nativo e limite.
2. `check` — relê o pacote como a instalação leria.
3. `install --root .tmp/plugins` — ensaia a promoção atômica.
4. Abra o app, instale pelo botão e execute uma vez com dados fictícios.

O import do `lib/` só acontece no **Executar**. Se o plugin tiver erro de
import ou assinatura, ele aparece ali; o `check` não abre o código.

## Códigos de erro

O CLI imprime `ERRO [codigo] mensagem` e devolve 1.

| Código | Quando |
|---|---|
| `source_missing` | pasta de origem do `pack` não existe |
| `archive_type` | saída ou pacote não termina em `.tar.xz` |
| `archive_missing` | arquivo não encontrado |
| `archive_too_large` | passa de 100 MB |
| `digest_invalid` | sidecar não confere com o arquivo |
| `manifest_missing` / `manifest_invalid` | manifesto ausente, quebrado ou inválido |
| `invalid_id` | `id` fora da regra ou nome reservado do Windows |
| `duplicate_option` | `key` repetido em opções ou entradas |
| `unsupported_api` / `app_too_old` | API ou versão mínima incompatível |
| `missing_dependency` | distribuição declarada não está instalada |
| `entrypoint_missing` | arquivo do entrypoint não existe em `lib/` |
| `entry_unsafe` / `entry_type` | caminho perigoso, link ou tipo de entrada recusado |
| `plugin_duplicate` | já existe plugin instalado com o mesmo `id` |
| `not_installed` | `uninstall` de um id que não está na pasta |
| `no_space` | espaço livre insuficiente para extrair |
| `install_failed` | falha de sistema durante instalação ou remoção |

Erros de **execução** (`run_missing`, `run_signature`,
`plugin_import_failed`, `result_invalid`, `option_invalid`) não passam pelo
CLI: veja [`primeiro-plugin.md`](primeiro-plugin.md#7-erros-de-código).

## Repositório privado e CI

O plugin pode viver num repositório separado, inclusive privado. O CI precisa
do pacote `xl-utils` para rodar o CLI; instale-o do Git com um token de leitura:

```yaml
name: plugin

on:
  push:
  pull_request:

jobs:
  pacote:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v5
      - uses: astral-sh/setup-uv@v6
      - name: Instalar o xl_Utils
        env:
          TOKEN: ${{ secrets.XL_UTILS_TOKEN }}
        run: |
          uv venv
          uv pip install "xl-utils @ git+https://x-access-token:$env:TOKEN@github.com/SEU_USUARIO/xl_Utils"
      - name: Empacotar e conferir
        run: |
          uv run xl-utils-plugin pack . -o build/plugin.tar.xz
          uv run xl-utils-plugin check build/plugin.tar.xz
      - uses: actions/upload-artifact@v4
        with:
          name: plugin
          path: |
            build/plugin.tar.xz
            build/plugin.tar.xz.sha256
```

- `XL_UTILS_TOKEN` é um fine-grained token com leitura no repositório do app.
  Nunca escreva o token no `pyproject.toml` nem no workflow em texto puro.
- O job não abre o app: valida o pacote e publica o `.tar.xz` com o sidecar.
- Para um teste real de execução, instale em `.tmp/plugins` com `--root` e abra
  o app manualmente; o CI não tem a UI.

## Checklist antes de distribuir

- [ ] `check` verde e sidecar ao lado do pacote.
- [ ] `id` estável e igual ao nome da pasta instalada.
- [ ] `[ui]` e `[[options]]` batem com o que `run` lê.
- [ ] Permissões declaradas descrevem o que o código faz.
- [ ] Testado uma vez com o app, incluindo cancelar e um arquivo inválido.
