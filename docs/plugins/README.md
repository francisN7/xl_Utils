# Plugins do xl_Utils

Um plugin é um pacote local que acrescenta uma página de ferramenta ao
xl_Utils. Ele não é baixado sozinho: você escolhe o arquivo, o app valida,
instala em `%LOCALAPPDATA%/xl_utils/plugins/` e só executa o código quando a
ferramenta é aberta.

> **Estado:** a área “Plugins” lista, instala e remove pacotes; a ferramenta é
> montada a partir do manifesto e o `lib/` só é importado no primeiro
> Executar. Comece por [`primeiro-plugin.md`](primeiro-plugin.md).

## O que um plugin pode fazer

- Ler planilhas escolhidas pelo usuário e as abas marcadas.
- Receber opções declaradas no manifesto e devolver tabelas de resultado.
- Registrar log, reportar progresso e respeitar o cancelamento.
- Guardar dados persistentes em `data/`, dentro da própria pasta.
- Declarar que usa rede, filesystem ou subprocesso.

## O que ele não pode fazer nesta versão

- Trazer `.pyd`, `.dll`, `.exe` ou qualquer binário nativo.
- Instalar dependências com `pip` durante a instalação.
- Construir a própria tela com Flet; a UI é declarativa e montada pelo host.
- Ser isolado por sandbox. O plugin roda no mesmo processo e tem os direitos do
  usuário; as permissões são avisos, não bloqueios.
- Ser baixado ou atualizado automaticamente.

## Modelo mental

```text
plugin.toml      manifesto: identidade, entrada, permissões e UI
lib/             código Python puro; o entrypoint vive aqui
assets/          imagens e dados opcionais
data/            criado pelo host; dados do plugin, apagados na desinstalação
```

O host lê o manifesto, valida o pacote, instala e — na S14 — importa
`run(request)` e exibe o resultado. O plugin devolve dados, não controles de
interface.

## Mapa do contrato

| Tema | Leia |
|---|---|
| criar o primeiro plugin, do zero ao Executar | [`primeiro-plugin.md`](primeiro-plugin.md) |
| empacotar, conferir, instalar e testar com CI | [`empacotar-testar.md`](empacotar-testar.md) |
| exemplos que rodam: mínimo e com opções | [`exemplos/`](exemplos) |
| formato, layout, limites e o que é recusado | [`pacote.md`](pacote.md) |
| todos os campos do `plugin.toml` | [`manifesto.md`](manifesto.md) |
| `run(request)`, entrada, saída, log, progresso e erros | [`api.md`](api.md) |
| entradas de arquivo e opções da página | [`ui-e-opcoes.md`](ui-e-opcoes.md) |
| confiança, permissões, hash e limites | [`permissoes-e-seguranca.md`](permissoes-e-seguranca.md) |
| SemVer, `api_version` e compatibilidade | [`versionamento.md`](versionamento.md) |
| por que `.tar.xz`, mesmo processo e UI declarativa | [`../adr/0023-contrato-de-plugins.md`](../adr/0023-contrato-de-plugins.md) |

O CLI está instalado como `xl-utils-plugin` (`pack`, `check`, `install`,
`list`, `uninstall`) e também roda como `uv run python scripts/plugin_cli.py`
dentro do repositório do app. O fluxo completo, incluindo o repositório
privado e o CI, está em [`empacotar-testar.md`](empacotar-testar.md).

## Antes de começar

- Python 3.15 e `uv` no ambiente de desenvolvimento.
- O repositório do app para usar o validador e o CLI; o plugin em si pode viver
  em outro repositório.
- Um pacote `.tar.xz` e o sidecar `.sha256`. O empacotador oficial gera os dois.
- Para instalar pela tela: abra **Plugins** na barra lateral e escolha o pacote.

## Segurança em uma linha

Instalar um plugin é confiar no código dele. O validador impede caminhos
maliciosos, binários nativos e pacotes gigantes; ele **não** impede que o
código, depois de carregado, leia arquivos, use a rede ou chame subprocessos.
Leia o manifesto e instale só o que você confia.
