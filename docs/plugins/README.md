# Plugins do xl_Utils

Um plugin é um pacote local que acrescenta uma página de ferramenta ao
xl_Utils. Ele não é baixado sozinho: você escolhe o arquivo, o app valida,
instala em `%LOCALAPPDATA%/xl_utils/plugins/` e só executa o código quando a
ferramenta é aberta.

> **Estado:** a S13 entrega o contrato, o validador, a instalação atômica e o
> CLI de desenvolvimento. A área “Plugins” na UI, o carregamento e o guia
> prático com exemplos chegam na S14. Até lá, este diretório é a referência do
> contrato.

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
| formato, layout, limites e o que é recusado | [`pacote.md`](pacote.md) |
| todos os campos do `plugin.toml` | [`manifesto.md`](manifesto.md) |
| `run(request)`, entrada, saída, log, progresso e erros | [`api.md`](api.md) |
| entradas de arquivo e opções da página | [`ui-e-opcoes.md`](ui-e-opcoes.md) |
| confiança, permissões, hash e limites | [`permissoes-e-seguranca.md`](permissoes-e-seguranca.md) |
| SemVer, `api_version` e compatibilidade | [`versionamento.md`](versionamento.md) |
| por que `.tar.xz`, mesmo processo e UI declarativa | [`../adr/0023-contrato-de-plugins.md`](../adr/0023-contrato-de-plugins.md) |

O CLI já existe em `scripts/plugin_cli.py` (`pack`, `check`, `install`, `list`,
`uninstall`). O guia de “primeiro plugin”, os comandos passo a passo e os
exemplos copiáveis entram na S14, quando o fluxo rodar de ponta a ponta. O
roteiro da sessão está em
[`../sessions/S14-plugins-ui.md`](../sessions/S14-plugins-ui.md).

## Antes de começar

- Python 3.15 e `uv` no ambiente de desenvolvimento.
- O repositório do app para usar o validador e o CLI; o plugin em si pode viver
  em outro repositório.
- Um pacote `.tar.xz` e o sidecar `.sha256`. O empacotador oficial gera os dois.

## Segurança em uma linha

Instalar um plugin é confiar no código dele. O validador impede caminhos
maliciosos, binários nativos e pacotes gigantes; ele **não** impede que o
código, depois de carregado, leia arquivos, use a rede ou chame subprocessos.
Leia o manifesto e instale só o que você confia.
