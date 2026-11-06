# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
Uma entrada por **versão**; o detalhe por sessão está no roadmap numerado e as
decisões nos ADRs.

## [Unreleased]

### Added

- Fundação do aplicativo desktop em Flet, com estrutura MVC híbrida em
  `src/xl_utils/`, ambiente uv no Python 3.15 e navegação entre as quatro
  ferramentas.
- UI base no tema Dracula: sidebar de 240 px com Início, quatro cartões
  alinhados à esquerda, entrada de arquivo clicável, barra de ação e painel de
  resultado com log e prévia de até 100 linhas.
- Cache de estado por ferramenta: navegar preserva a seleção; trocar o arquivo
  reseta opções e resultado.
- Helpers compartilhados de leitura/escrita de planilhas, detecção real de
  formato com `puremagic`, nomes de saída únicos e remoção de emojis.
- Leitura segura por padrão: `dtype=str`, preservação de zeros/CNJ/CPF e
  quebras de linha intactas.
- Tratamento de Texto funcional: `prepare_workbook` remove emojis de todas as
  abas, repara leitura com um fallback por formato e grava em `output/`.
- Erro tipado `WorkbookReadError` quando a planilha não pode ser lida nem
  reparada, substituindo o antigo `xlsx2csv` via `shell=True`.
- Teste funcional de 1.000 linhas fictícias geradas em memória, em CSV e XLSX,
  sem versionar dados de teste; amostra local opcional em `samples/`.
- Extração de CNJs funcional: aceita formato pontuado ou 20 dígitos,
  padroniza, remove duplicatas e grava `PROCESSOS` em `output/`.
- Recorte de planilhas funcional: divide cada aba em blocos de N linhas, com
  campo editável na página, nomes `_Recorte_NNN` e saída em `output/`.
- Seleção de abas por planilha: chips com “Todas”/“Limpar”, contador e aviso de
  leitura; `all_str`, `cnj` e `cut` processam apenas as abas marcadas,
  preservando os nomes na saída.
- Tipografia mínima de 12 px, sidebar de 260 px e fontes maiores em rótulos,
  ícones, logs e prévia.
- Lote de arquivos em todas as ferramentas: texto, CNJ e recorte processam cada
  origem e salvam saídas separadas, com prévia e log identificando o arquivo.
- Mesclagem de planilhas: concatena as abas selecionadas de um ou vários
  arquivos em `output/Merge.xlsx`, com a coluna `ORIGEM`, quadro de chips
  arrastáveis para juntar, separar e ordenar colunas e recusa de uma única aba
  útil. O primeiro chip define o cabeçalho; cada aba contribui com uma coluna
  por saída.
- Suíte de integração nos quatro formatos (`.xlsx`, `.xls`, `.csv` e `.html`):
  leitura, cabeçalhos, reparo de CSV cp1252, imutabilidade das origens e
  execução das quatro ferramentas, incluindo merge com origens mistas. O `.xls`
  usa uma fixture binária fictícia gerada com `xlwt`.
- Estrutura de contexto entre sessões (`AGENTS.md`, `CURRENT.md`, mapa em
  `docs/README.md`, roadmap `main` + histórico, specs, ADRs e check de docs).
- Log estruturado por execução (`RunLog`) com níveis e evento final, exibido no
  painel e copiável.
- “Copiar diagnóstico” com versões do app/Python/pandas/Flet, arquivos, abas,
  opções, resultado, tipo, mensagem, causa e traceback limitado.
- Erros da UI separados em leitura da planilha, seleção inválida e falha
  inesperada, sempre mantendo a mensagem original.
- Texto e CNJ sem checkboxes desabilitados: o comportamento fixo vira uma frase
  na entrada, e o card “2. Opções” só aparece em recorte e merge.
- Tipo real x extensão: `FormatCheck` mostra o formato detectado na entrada
  quando diverge do nome, bloqueia a execução quando nada é identificável e
  registra formato e divergência no log e no diagnóstico. Extensões trocadas são
  lidas pelo conteúdo sem renomear a origem.
- Saída escolhida: executar só calcula e mostra a prévia; “Salvar” abre o
  seletor nativo (arquivo único ou pasta para lote), “Salvar em output/”
  continua como atalho e cancelar não grava nada. Nomes existentes ganham
  sufixo e o log registra o caminho real.
- Publicação: a `main` passa a ser a versão com UI, a `main` antiga vira a
  branch `legacy` com aviso de descontinuação e `feat/ui` é removida depois de
  publicada; o README aponta para as duas.
- Branch `legacy` travada no GitHub: tag `legacy-v1` e rulesets que bloqueiam
  push, force-push e exclusão da branch e da tag.
- Code tour em `docs/guide/code-tour.md` e “Mapa do core” em
  `reference/architecture.md`, com docstrings e comentários do core/controllers
  em PT-BR.
- Comando global documentado (`uv tool install --editable .`) e ADR 0010 sobre
  leitura fiel de CSV/HTML.
- Execução em segundo plano nas quatro ferramentas: o handler roda fora do loop
  da página, com barra de progresso e “Arquivo X de Y”, entrada e chips
  bloqueados e atualizações de UI sempre no loop. Ver ADR 0011.
- Log ao vivo e cancelamento cooperativo: as linhas de cada arquivo chegam ao
  painel durante a execução, “Executar” vira “Cancelar” e a parada acontece
  entre arquivos, mantendo a prévia parcial sem liberar a gravação. Ver adendo
  do ADR 0011.
- Extração de CNJ tolerante a texto sujo: espaços, quebras, travessões, barras
  e caracteres invisíveis não impedem o achado; CPF e números maiores continuam
  fora. O dígito verificador não é validado e o valor inválido não é descartado.
  Ver ADR 0012.
- Recorte por quantidade de arquivos: a página alterna entre linhas por arquivo
  e arquivos por aba; a quantidade vale por aba, os blocos ficam equilibrados e
  o modo antigo continua igual.
- Mesclagem: `ORIGEM` agora é `<arquivo> - <aba>` (sem extensão) e a nova
  `LINHA_ORIGEM` numera as linhas de dados do resultado inteiro com zeros à
  esquerda, preservando a ordenação. Ver adendo do ADR 0005.
- Execução visível por etapa: as quatro ferramentas registram leitura, planilha
  carregada e cálculo no log ao vivo; a barra fica indeterminada durante cada
  arquivo e avança ao concluí-lo. O loop passa a renderizar entre eventos. Ver
  adendo do ADR 0011.
- Tema claro opcional, variante Alucard do Dracula (creme quente, sem branco
  puro): a paleta esclarece os tokens de `ui/theme.py`, a escolha fica em
  `shared/settings.py` (`%LOCALAPPDATA%/xl_utils/settings.json`) e o botão da
  sidebar pede reabertura. Ver ADR 0013.

### Changed

- CSV passa a detectar encoding e separador (`;`, tab e `|`); `NA`, `N/A` e
  `NULL` são preservados como texto.
- HTML com cabeçalho de dois níveis mantém zeros à esquerda e achata o
  cabeçalho; `.xlsm` deixou de ser tratado como divergência.
- `save_workbook` normaliza o sufixo para `.xlsx`; `save_chosen` recusa arquivo
  como destino de lote; `safe_file_part` e `summarize_cnjs` foram para o core.
- Docstrings e comentários de `ui/`, `shared/`, shell e `__init__` passam para
  PT-BR; o diagnóstico foi revisado sem incluir conteúdo de célula.
- Documentação: o backlog passa a registrar o envio direto do Google Drive e a
  vinculação entre AGENDA, CLIENTES, FINANCEIRO e PROCESSOS, com decisões em
  aberto e protocolo detalhado; nenhuma das duas foi implementada.

### Removed

- `all_str.py`, `cnjs.py`, `cut.py` e `merge.py` da raiz, substituídos por
  core + controller + página. Nenhum script legado permanece na raiz.
- Branch `cli-app` e a tentativa de interface por linha de comando.
- Ferramentas `convert`, `quick_replace` e `remove_emoji` (emojis passam para o
  pipeline do `all_str`).
- Dependências `demoji`, `file-picker-py`, `xlsx2csv`, `click` e `xlrd`; o
  `.xls` passou a ler pelo engine `calamine` (`python-calamine`).

### Fixed

- Colunas de entrada e de resultado rolam sem barra visível; log limitado a
  160 px, prévia com 240 px e rolagem nos dois eixos. O conteúdo fica recortado
  no cartão e não cobre mais a linha divisória nem a barra de ação.
- HTML agora preserva zeros à esquerda: como `read_html` não aceita `dtype`, a
  leitura refaz a tabela com converters. As fixtures declaram UTF-8 para manter
  acentos.
- CSV exportado pelo Excel em pt-BR (`;`) não vira mais uma coluna, e os
  decimais com vírgula não quebram a linha.
- O reparo de `.xls` deixou de repetir a mesma leitura: o formato falha com
  mensagem de “sem leitor alternativo” quando o calamine não consegue abrir.

## v0.1.0 — 2026-11-04

### Added

- Primeira versão em desenvolvimento: shell do app e utilitários em migração.
