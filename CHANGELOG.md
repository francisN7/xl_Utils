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

## v0.1.0 — 2026-11-04

### Added

- Primeira versão em desenvolvimento: shell do app e utilitários em migração.
