# Arquitetura

**O que responde:** camadas, fluxo de dados, leitura segura, detecção de
formato e convenções do core. **O que não responde:** a interface (ver
`ui.md`) nem o porquê das decisões (ver `../adr/`). Para uma ordem de leitura
guiada, comece pelo [`guide/code-tour.md`](../guide/code-tour.md).

## Camadas

| Camada | Pasta | Regra |
|---|---|---|
| Core | `src/xl_utils/core/` | Regra pura, sem Flet, sem diálogo, sem `print`. |
| Controllers | `src/xl_utils/controllers/` | Orquestra o core e devolve dados em memória. |
| UI | `src/xl_utils/ui/` | Coleta entrada, executa em segundo plano e exibe resultado; não contém regra. |
| Shared | `src/xl_utils/shared/` | Log, diagnóstico, progresso, abertura de pasta e contas do Drive. |

Uma ferramenta = um módulo em `core/tools/` + um controller + uma página.

## Mapa do core

| Módulo | Papel | Superfície principal |
|---|---|---|
| `core/io.py` | lê e grava cada formato | `read_workbook`, `read_html_tables`, `list_sheets`, `read_headers`, `save_workbook` |
| `core/mime.py` | decide o formato pelo conteúdo | `detect_suffix`, `resolve_suffix`, `check_format`, `FormatCheck` |
| `core/paths.py` | caminhos e nomes seguros | `unique_path`, `default_output_dir`, `safe_file_part` |
| `core/save.py` | grava só depois da escolha | `SaveItem`, `save_chosen`, `save_to_output`, `save_item` |
| `core/text.py` | limpeza de texto | `remove_emojis` |
| `core/tools/all_str.py` | pipeline de leitura | `prepare_workbook` |
| `core/tools/sheets.py` | seleção de abas | `filter_sheets`, `default_selection` |
| `core/tools/cnj.py` | regra do CNJ | `extract_cnjs`, `normalize_cnj`, `summarize_cnjs` |
| `core/tools/cut.py` | regra do recorte | `split_frame`, `split_workbook` |
| `core/tools/merge.py` | regra do merge | `ColumnRef`, `ColumnGroup`, `merge_sheets`, `move_column` |
| `core/tools/link.py` | regra da vinculação | `LinkConfig`, `SheetSpec`, `link_agenda`, `find_target_sheet` |

Erros tipados: `WorkbookReadError` (leitura), `SaveError` (gravação),
`ConfigError`, `InvalidCnjError`, `MissingColumnsError` e
`AlreadyProcessedError` (vinculação), além de `ValueError` para seleção ou
regra inválida.

## Fluxo de dados

```text
arquivo escolhido
  → controller
  → all_str.prepare_workbook (leitura segura + emojis)
  → sheets.filter_sheets (abas escolhidas)
  → regra da ferramenta em core/tools/
  → SaveItem em memória (sem escrever)
  → result panel (prévia e “Pronto para salvar”)
  → escolha do usuário
  → core/save.py grava e devolve o caminho real
```

## Leitura segura

Toda ferramenta começa pelo pipeline do `all_str`, sempre antes da regra
específica:

1. lê todas as abas com `dtype=str`;
2. remove emojis com `emoji.replace_emoji`;
3. preserva o texto da célula, inclusive quebras de linha;
4. mantém `NA`, `N/A`, `NULL` e `None` como texto (`keep_default_na=False`);
5. só tenta reparo quando a leitura falha, sem `shell=True`.

Excel é lido com `openpyxl` para `.xlsx`/`.xlsm` e com `calamine` para `.xls`
(pacote `python-calamine`). `core/tools/all_str.py` expõe
`prepare_workbook(path)`, que devolve `{nome_da_aba: DataFrame}` já limpo. As
demais ferramentas importam essa função antes de aplicar a própria regra.
`controllers/all_str.py` orquestra a leitura, monta o `SaveItem` em memória e o
log; `ui/pages/all_str.py` só conecta a página.

CSV não confia na vírgula padrão: o Excel em pt-BR exporta com `;`, e ler com
vírgula transformaria a linha inteira em uma coluna **sem levantar erro**.
`core/io.py` decodifica uma amostra (`utf-8-sig`, depois `cp1252`, depois
`latin-1`) e usa `csv.Sniffer` para escolher entre `,`, `;`, tab e `|`. Se a
leitura rápida falhar, o motor Python infere o separador linha a linha.
`read_headers` usa a mesma rotina com uma amostra curta.

Quando a leitura normal falha, o pipeline tenta **um** leitor mais tolerante,
de acordo com o formato real: `openpyxl` em modo somente leitura para
`.xlsx`/`.xlsm`, codificações/separadores alternativos para `.csv` e outros
parsers para `.html`. O `.xls` não tem leitor alternativo — o calamine é o único
engine do projeto — e a falha sobe com a causa original. Se o reparo também
falhar, levanta `WorkbookReadError`; nunca renomeia nem altera o arquivo do
usuário.

O objetivo é não perder zeros à esquerda, CNJ/CPF e valores que o Excel
converteria em notação científica. A ferramenta “Tratamento de texto” também
expõe esse pipeline sozinha, para conversão e reparo explícitos. O `read_html`
do pandas não aceita `dtype`; para HTML, a leitura faz uma segunda passada com
converters nas **chaves reais** das colunas — inclusive tuplas de cabeçalho em
dois níveis — e só depois achata o cabeçalho (`Grupo - cod`) com desempate
`_2`. Assim `000123` continua texto.

## Seleção de abas

`core/io.list_sheets(path)` devolve os nomes na ordem do arquivo. Excel lê só os
metadados com `pd.ExcelFile` e o engine do formato real; CSV devolve
`["Planilha1"]`; HTML precisa ser lido, porque cada tabela vira `PáginaN`.
Falha de leitura sobe como `ValueError` com o nome do arquivo.

`core/tools/sheets.filter_sheets(sheets, selected)` mantém apenas as abas
escolhidas, na ordem original e com os mesmos nomes. `None` significa todas;
conjunto vazio ou nome inexistente levanta `ValueError`.
`default_selection` define o padrão conforme a ferramenta: no lote (texto, CNJ
e recorte) todas as abas de todos os arquivos; no merge, a primeira de cada um.
Ver ADR 0006.

A seleção vive em `ToolState.sheet_names` e `ToolState.selected_sheets`, por
arquivo; trocar a lista de arquivos recarrega os nomes e reaplica o padrão. Os
controllers recebem `selected` e filtram logo depois do `prepare_workbook`,
antes da regra da ferramenta.

## Lote de arquivos

Texto, CNJ e recorte aceitam vários arquivos. A página monta a lista de
`(origem, abas)` com `ui/pages/batch.py`, chama o controller uma vez por arquivo
e junta logs e prévias. Cada `SaveItem` carrega o `output/` da própria origem
para o atalho “Salvar em output/”; o destino escolhido no seletor vence. O merge
continua sendo o único que produz uma saída única. Ver ADR 0006 e ADR 0008.

## Detecção de formato

`core/mime.py` usa `puremagic` no conteúdo e nunca renomeia o arquivo do
usuário. Quando o detectado é genérico (`.txt`) e a extensão original é
suportada, a extensão original vence. Formatos: `.xlsx`, `.xlsm`, `.xls`,
`.csv`, `.html` e `.htm`.

`check_format` devolve um `FormatCheck` imutável com o tipo detectado, a
extensão declarada, o tipo efetivo de leitura e os estados `identified` e
`diverges`. A UI mostra `conteúdo: .xlsx · nome: .xls` somente quando dois
formatos suportados divergem. Formatos equivalentes (`.xlsx`/`.xlsm` e
`.htm`/`.html`) não contam como divergência, porque usam o mesmo leitor.
`ToolLayout._run` bloqueia antes de ler quando `identified` é falso, mostra
“Não foi possível identificar o formato” e registra o motivo no log e no
diagnóstico. A leitura continua usando `resolve_suffix`, então o conteúdo vence
o nome sem tocar no arquivo.

## Saída

Os controllers não gravam: cada execução devolve `SaveItem` com o nome sugerido,
as abas em memória e a pasta `output/` da origem. `core/save.py` concentra a
gravação depois da escolha: `save_chosen` grava um item no arquivo escolhido ou
vários na pasta escolhida; `save_to_output` usa o atalho. Com vários itens, um
destino que existe e não é pasta é recusado com `SaveError`, em vez de virar uma
pasta com nome de arquivo. `SaveError` embrulha qualquer falha de escrita sem
apagar a prévia.

`core/paths.py` cria a pasta e devolve um nome livre (`saida_001.xlsx`).
`core/io.py` grava todas as abas em um `.xlsx` — o sufixo do destino é sempre
normalizado para `.xlsx` — com nomes saneados (limite de 31 caracteres e
caracteres inválidos do Excel). O arquivo de origem nunca é alterado e nada é
criado antes da escolha do usuário.

## Logging e erros

`shared/log.py` define `RunLog`, uma lista ordenada de eventos `(nível, texto)`
com helpers `info`, `success`, `warning` e `error`. `to_text()` devolve uma linha
por evento (`[INFO]`, `[OK]`, `[AVISO]`, `[ERRO]`) e a iteração continua
compatível com listas de strings, então `join_logs` e as prévias seguem iguais.
Os controllers registram arquivo, tipo, abas, linhas, colunas e saída; a página
anexa os logs ao `ToolState.log`, e o `ToolLayout` grava o evento final.

`ToolLayout._run` distingue `WorkbookReadError` (“Não foi possível ler a
planilha”), `ValueError` (“Confira a seleção”) e falhas inesperadas. A mensagem
original fica no painel, o traceback em `ToolState.error_detail` e o log recebe
o evento de erro. `build_diagnostics` monta o texto de “Copiar diagnóstico” com
versões do app, Python, pandas e Flet, arquivos e abas, formato detectado e
divergência, opções, resultado, tipo, mensagem, causa e traceback limitado a
4.000 caracteres. Versão ausente vira “desconhecida”; nenhum conteúdo de célula
entra no diagnóstico.

## Execução e progresso

`ToolLayout._run` valida o formato no loop da página e, quando existe página com
`run_task`, agenda `_execute_async`. O handler roda em `asyncio.to_thread`; os
marcos de `shared/progress.py` (`start`, `file_started`, `file_done`, `finish`)
viram `ProgressEvent` e chegam ao loop por uma `asyncio.Queue` alimentada com
`call_soon_threadsafe`. A barra e o texto “Arquivo X de Y” ficam no painel de
resultado. `ResultPanel` e `PreviewTable` recebem um dispatcher para que o
`update` também seja agendado no loop; a thread de trabalho nunca chama a UI.

A fila também leva `ProgressEvent(kind="stage")`: cada controller recebe o
reporter e chama `note(log, texto)`, que acrescenta a etapa ao `RunLog` e a
emite ao vivo. O painel atualiza o texto de andamento e anexa a linha formatada
ao log; assim o usuário vê “lendo”, “planilha carregada”, “procurando CNJs” etc.
antes de o arquivo terminar. O `ToolState` mantém a versão canônica usada no fim
e no diagnóstico.

A barra fica **indeterminada** enquanto um arquivo está em andamento e assume a
fração concluída ao terminar cada arquivo. Depois de aplicar um evento, o loop
cede com `asyncio.sleep(0)` para a atualização ser renderizada antes do próximo;
sem isso, lotes rápidos acumulam eventos e a tela só muda no fim.

`CancelToken` (mesmo módulo) expõe `cancel()` e `cancelled`. O layout cria um
token por execução, entrega ao handler e troca “Executar” por “Cancelar”. As
páginas checam o token entre arquivos: a chamada em curso termina, a prévia
parcial permanece e `ResultPanel.set_cancelled` marca “Execução cancelada” sem
liberar salvar nem gravar. Merge emite etapas por fonte, mas continua uma única
chamada de controller; o cancelamento só vale antes de começar.

Sem página (testes headless), o handler roda no próprio loop com um reporter
síncrono. O estado da ferramenta é preenchido durante a execução, mas a entrada,
os chips de abas e “Executar” ficam desabilitados até `_finish`. Ver ADR 0011.

## Ferramentas

| Ferramenta | Módulo | Estado |
|---|---|---|
| Tratamento de texto | `core/tools/all_str.py` | pronta |
| Extrair CNJs | `core/tools/cnj.py` | pronta |
| Recortar planilha | `core/tools/cut.py` | pronta |
| Mesclar planilhas | `core/tools/merge.py` | pronta |
| Verificar vínculos | `core/tools/link.py` | pronta: quatro planilhas em dois fluxos |

## Extração de CNJ

`core/tools/cnj.py` reconhece 20 dígitos com separadores flexíveis (ponto,
barra, hífen, espaço, travessão e quebra de linha) ou a sequência contínua, sem
aceitar trecho de número maior nem CPF. Antes da busca, remove invisíveis
(zero-width, BOM), troca NBSP por espaço e uniformiza travessões, só na cópia
usada pela regex. O dígito verificador **não** é validado: o valor é extraído e
padronizado mesmo inválido. `normalize_cnj` devolve sempre o formato pontuado;
`summarize_cnjs` percorre todas as abas e célula a célula **uma vez** e devolve
`(achados, únicos ordenados)`. `collect_cnjs` e `count_cnjs` continuam como
atalhos. `controllers/cnj.py` prepara `SaveItem` com `<nome> lista cnj.xlsx` na
coluna `PROCESSOS` e registra encontrados, duplicados e únicos no log.

## Vinculação

`core/tools/link.py` recebe as abas das planilhas e o `LinkConfig` carregado de
`headers.json`. `column_map` casa o cabeçalho com `header_key`, que dobra caixa
e acento e remove todos os espaços; os valores das células continuam brutos.
`find_target_sheet` escolhe a primeira aba que tem todos os campos exigidos e,
se nenhuma tiver, lista o que faltou por aba.

A AGENDA usa `link_agenda`: valida o CNJ, compara CNJ → PASTA → PROTOCOLO e
grava `VINCULA?`. Sem vínculo, o protocolo vira `<cabeçalho real>: <valor>` no
fim da descrição e o campo recebe `MIGRAÇÃO`. A sentinela nunca entra na
comparação; em linha vinculada ela é limpa. A reexecução exige
`allow_migrated` e não repete a linha.

O FINANCEIRO usa `link_financeiro`: com PROCESSOS, grava `VINCULA?` na mesma
prioridade e `VINCULA (POR NOME)?` (SIM/NÃO) com a união dos nomes de
PROCESSOS (split cru por `;`) e de CLIENTES. Só com CLIENTES, grava apenas a
coluna de nome e não toca em `VINCULA?`. As duas colunas entram depois do bloco
padrão e antes das extras, na ordem `VINCULA?` e `VINCULA (POR NOME)?`; uma
coluna existente, mesmo com grafia sem espaço, é sobrescrita no lugar.

As opções `single_field` (AGENDA e/ou FINANCEIRO) mantêm o campo vencedor e
movem os outros dois para o fim da descrição como `<cabeçalho real>: <valor>`,
esvaziando as colunas; `MIGRAÇÃO` não é movida. `name_in_description` prefixa
`NOME DO CLIENTE: <valor>` no FINANCEIRO quando o nome não vincula. Os fluxos
são independentes: AGENDA exige PROCESSOS; FINANCEIRO exige PROCESSOS ou
CLIENTES; cada um gera um `SaveItem`. As demais abas são preservadas.

`shared/configs.py` lê `src/xl_utils/configs/headers.json` por
`importlib.resources` e, se existir, o override em
`%LOCALAPPDATA%/xl_utils/headers.json` (ADR 0015). O JSON traz as quatro
planilhas padrão, os campos usados, o bloco padrão na ordem e o separador de
descrição (quebra de linha na AGENDA, `" | "` no FINANCEIRO).

## Drive

`shared/drive_auth.py` monta o cliente OAuth (`configs/drive_client.json`
empacotado, override em `%LOCALAPPDATA%/xl_utils/drive_client.json`), roda o
fluxo de app instalado com PKCE e `state` da `google-auth-oauthlib` em
`127.0.0.1` numa porta efêmera e devolve uma `Account` com e-mail e nome lidos
do `id_token`. `import_client` aceita o JSON baixado do Google Cloud Console,
recusa arquivo acima de 64 KB, exige HTTPS em `google.com`/`googleapis.com` e
grava só os campos usados, de forma atômica; `is_configured` diz se há cliente
válido. `shared/accounts.py` grava uma conta por e-mail em
`%LOCALAPPDATA%/xl_utils/drive/accounts/`, com o `refresh_token` cifrado por
DPAPI e escrita atômica; o e-mail ativo fica em `drive/active.json`. `ui/drive.py`
é o estado compartilhado entre o menu do topo e o cartão do hub, e o login roda
fora da thread da UI (ADR 0018).

## Recorte

`core/tools/cut.py` divide cada aba de dois modos: blocos de N linhas
(`split_frame`) ou uma quantidade de arquivos por aba (`split_frame_by_parts`).
No modo por quantidade, os blocos são equilibrados com diferença de no máximo
uma linha; quantidade acima do total de linhas é reduzida para não gerar arquivo
vazio, e uma aba vazia ainda gera um arquivo. `controllers/cut.py` lê pelo
`prepare_workbook`, filtra as abas escolhidas e prepara um `SaveItem` por bloco,
com `<stem>_Recorte_NNN.xlsx` (ou `<stem>_<aba>_Recorte_NNN.xlsx` com várias
abas processadas). O nome da aba passa por `core/paths.safe_file_part`, que troca
caracteres inválidos de arquivo. O seletor de modo e os dois campos numéricos
vivem em `ToolState.options`; só o campo do modo ativo aparece.

## Mesclagem

`core/tools/merge.py` recebe uma sequência de `(arquivo, aba, DataFrame)` e uma
lista de `ColumnGroup`, concatena na mesma ordem e descarta apenas abas sem
linhas. Cada grupo vira uma coluna de saída: o primeiro `ColumnRef` define o
cabeçalho e os demais alimentam a mesma coluna; `group_by_name` agrupa
automaticamente colunas de mesmo nome. O núcleo valida que uma aba contribui com
no máximo uma coluna por saída, preenche lacunas com `pd.NA`, insere `ORIGEM` e
`LINHA_ORIGEM` como duas primeiras colunas e desempata cabeçalhos repetidos com
sufixo `_2`. `ORIGEM` é `<stem do arquivo> - <aba>`. `LINHA_ORIGEM` numera as
linhas de dados do resultado inteiro, com zeros à esquerda na largura do total
(12 linhas → `01`..`12`), preservando a ordenação lexical. Uma coluna de origem
com esses nomes vira `<nome>_original`.

`controllers/merge.py` lê cada fonte pelo `prepare_workbook`, filtra as abas com
`filter_sheets` e chama `merge_sheets`; exige ao menos duas abas com dados e
prepara `SaveItem` com `Merge.xlsx` na pasta da primeira origem. `inspect_columns`
usa `core/io.read_headers` para devolver os `ColumnRef`s sem carregar as linhas; a
página monta o quadro arrastável e guarda os grupos em `ToolState.options`.
`move_column` concentra a regra de mover/juntar chips. O painel é reconstruído
quando arquivos ou abas mudam.

## Testes

O core é testado com `pytest` e `tmp_path`; a UI tem testes headless para
layout, tema, estado e quadro do merge (`test_layout.py`, `test_merge_page.py`,
`test_theme.py`, `test_settings.py`, `test_ui_state.py`), além do smoke manual
para o visual. O teste funcional do `all_str` gera 1.000 linhas fictícias em
memória, roda em CSV e XLSX e confere zeros à esquerda, numeração CNJ-like,
remoção de emojis e quebras de linha.

`tests/test_formats.py` percorre `.xlsx`, `.xls`, `.csv` e `.html` com as mesmas
linhas fictícias e confere `read_workbook`, `list_sheets`, `read_headers` e
`prepare_workbook`; também cobre CSV com `;`, tab e `|`, preservação de
`NA`/`N/A`, cabeçalho HTML de dois níveis e a falha explícita de `.xls`.
`tests/test_integration.py` roda as quatro ferramentas sobre os quatro formatos,
incluindo origens mistas no merge e a imutabilidade das origens.
`tests/test_save.py` cobre controllers sem escrita, arquivo único, pasta, nome
livre, cancelamento, `SaveError` e recusa de arquivo no lote. O `.xls` é uma
fixture binária mínima em `tests/fixtures/minimo.xls`, gerada uma vez com `xlwt`
e **sem** adicionar a dependência ao projeto.

`tests/test_link.py` cobre prioridade, comparação bruta, CNJ inválido,
`MIGRAÇÃO`, reexecução, colunas e abas preservadas, com cabeçalhos fictícios.
`tests/test_configs.py` carrega o JSON empacotado e um override temporário. O
end-to-end com arquivo real continua no smoke manual.

## Limites conhecidos

- Datas do Excel chegam como texto ISO (`2024-01-02 00:00:00`), não no formato
  exibido na planilha.
- O `.xls` não tem leitor alternativo: se o calamine falhar, o erro é final.
- A detecção de separador de CSV pode errar em arquivo atípico com aspas
  inconsistentes; nesse caso o motor Python tenta inferir linha a linha.
- HTML sem tabela e planilha sem aba útil falham com mensagem, nunca em
  silêncio.

## Decisões

- [ADR 0001](../adr/0001-stack-ui-e-ambiente.md) — stack, uv e Flet.
- [ADR 0002](../adr/0002-arquitetura-core-ui.md) — camadas.
- [ADR 0004](../adr/0004-leitura-segura-e-emojis.md) — leitura segura e emojis.
- [ADR 0008](../adr/0008-saida-escolhida.md) — saída escolhida depois da prévia.
- [ADR 0010](../adr/0010-leitura-fiel-csv-html.md) — CSV/HTML fiéis e `NA` como
  texto.
- [ADR 0011](../adr/0011-execucao-fora-da-ui.md) — execução fora da UI thread e
  progresso por arquivo.
- [ADR 0014](../adr/0014-regra-de-vinculacao.md) — vinculação por valor bruto e
  `MIGRAÇÃO`.
- [ADR 0015](../adr/0015-config-empacotada.md) — config empacotada e estado por
  máquina.
