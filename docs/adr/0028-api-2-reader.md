# ADR 0028 — API 2 dos plugins: leitura pelo host e fim da API 1

- **Status:** aceita
- **Data:** 2026-11-25

## Contexto

Na API 1 (ADR 0023) o plugin recebia só `Path` e lia com `pd.read_excel`.
Ficava fora do pipeline `all_str` que as quatro nativas usam (texto, emojis,
reparo, tipo real, CSV e HTML), e cada plugin reinventava a leitura. A
vinculação (ADR 0027) só pode virar plugin se ler igual às nativas, e o plugin
não deve importar `core/`. Os únicos usuários da API 1 eram os dois exemplos
de `docs/plugins/exemplos/` e o `_molde` do `xl_U-Plugins`.

## Decisão

1. `PluginRequest.reader` (`shared/plugins/reader.py`, reexportado por
   `shared/plugins/api.py`) com um método:
   - `read(path)` devolve as abas marcadas em `request.sheets[path]`, na
     ordem do livro; arquivo sem seleção na tela volta inteiro;
   - `read(path, all_sheets=True)` devolve todas.
2. Retorno `dict[str, DataFrame]` igual a `filter_sheets(prepare_workbook(p))`.
   Cada livro é lido uma vez por execução (cache pela chave `path.resolve()`);
   cada chamada devolve um dicionário novo com `copy(deep=False)`, que no
   Copy-on-Write do pandas 3 é barato e protege o cache.
3. Falha de leitura levanta `ReadError`, subclasse de `WorkbookReadError`: o
   `ToolLayout` já a mostra como "Não foi possível ler a planilha". Seleção
   vazia ou aba inexistente levanta `ValueError` ("Confira a seleção").
4. O `reader` não olha `request.cancel`; o plugin confere entre arquivos.
5. Na primeira leitura de cada arquivo: `progress.stage("Lendo <arquivo>")` e
   `progress.note(log, "<arquivo>: N aba(s)")`. Nunca conteúdo de célula.
6. `API_VERSION = 2` e `SUPPORTED_API_VERSIONS = {2}`. A API 1 vira
   `RETIRED_API_VERSIONS`: o manifesto é recusado com `unsupported_api` e um
   motivo que manda migrar para a 2.
7. Arquivo aberto do Drive chega como `Path` do cache local; o `reader` não
   tem caminho especial para ele.

## Consequências

- Plugin lê `.xlsx`, `.xlsm`, `.xls`, `.csv` e `.html` com o mesmo texto das
  nativas, sem importar `core/`.
- Plugin API 1 instalado continua na lista como inválido, com o motivo, na
  área Plugins, no `list` e no `check`; nunca some.
- Exceção à regra de aposentadoria de `docs/plugins/versionamento.md` (uma
  release de transição): não havia plugin publicado na API 1.
- Exemplos foram para `version = "2.0.0"`; o `_molde` do `xl_U-Plugins` foi
  junto.

## Alternativas

- **`read(path)` com todas as abas:** obrigaria todo plugin a filtrar a
  seleção, e quem esquecesse processaria aba não marcada.
- **Uma aba por chamada:** a vinculação precisa do livro inteiro para achar a
  aba pelo cabeçalho.
- **Devolver `{}` com aviso em vez de exceção:** erro de leitura passaria
  como "nenhuma aba".
- **`reader` levantar `Cancelled`:** exigiria tratar um tipo novo no
  `ToolLayout` sem ganho, porque a leitura não é interrompível.
- **Manter a API 1 por uma release:** custo de dois contratos sem nenhum
  plugin real para proteger.
