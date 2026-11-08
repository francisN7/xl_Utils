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
  sidebar troca na hora, recolorindo a árvore sem perder o estado nem os cantos
  arredondados. Ver ADR 0013.
- Vinculação AGENDA × PROCESSOS: a quinta ferramenta lê as duas planilhas
  padrão, compara CNJ, PASTA e PROTOCOLO pelo valor bruto na prioridade
  CNJ → PASTA → PROTOCOLO e grava `VINCULA?`. Sem vínculo, o protocolo é
  preservado na descrição e o campo vira `MIGRAÇÃO`; reexecução pede
  confirmação e não duplica a linha. Ver ADR 0014.
- Cabeçalhos padrão empacotados em `src/xl_utils/configs/headers.json`, lidos
  por `importlib.resources`, com override opcional em
  `%LOCALAPPDATA%/xl_utils/headers.json`. Segredos e tokens ficam fora do
  repositório e do wheel. Ver ADR 0015.
- Vinculação FINANCEIRO × PROCESSOS/CLIENTES: quatro entradas rotuladas,
  fluxos definidos pelos arquivos anexados (AGENDA exige PROCESSOS; FINANCEIRO
  exige PROCESSOS ou CLIENTES), `VINCULA?` e `VINCULA (POR NOME)?` no
  FINANCEIRO, com nomes de PROCESSOS (split cru por `;`) e CLIENTES. Só
  CLIENTES gera apenas a coluna de nome. Ver ADR 0016.
- Opções da vinculação: nome sem vínculo na descrição (FINANCEIRO) e manter
  apenas um campo vinculante (AGENDA e/ou FINANCEIRO), desligadas por padrão;
  os números perdedores vão para o fim da descrição e as colunas ficam vazias.
- Tela cheia no quadro de alinhamento do merge: botão ao lado do título, cards
  com largura fixa e sobra como espaçamento, “CONFIRMAR” no canto inferior
  direito e retorno pelo mesmo ícone sem perder grupos, seleção ou ordem.
- Entrada no Google Drive pelo navegador (S9a): cliente OAuth de app instalado
  com PKCE e `state`, redirecionamento em `127.0.0.1` com porta efêmera e
  timeout, contas por e-mail em `%LOCALAPPDATA%/xl_utils/drive/` com
  `refresh_token` protegido por DPAPI. Ver ADR 0018.
- Importação do cliente OAuth do Drive pelo seletor nativo (S9a1), sem edição
  manual de JSON: validação de tamanho, UTF-8, HTTPS e domínio do Google, com
  escrita atômica em `%LOCALAPPDATA%`. Teste offline de ponta a ponta com Google
  falso (PKCE e `state`) e `scripts/check-drive-login.py` para o consentimento
  real.
- Menu de perfis do Drive no canto superior direito (S9a2): hamburger fora da
  sidebar, ícone de perfil, conta ativa marcada, adicionar conta e sair. O
  cartão do Drive saiu do hub; o primeiro **Entrar com Google** pede o JSON do
  cliente uma única vez e depois abre o navegador direto.
- Site público no GitHub Pages (S9a3): página inicial e política de privacidade
  para a publicação do app OAuth no Google Auth Platform; os documentos
  internos ficam fora do site.
- Drive II (S9b): abrir planilha do Drive pelo Picker de apps desktop (OAuth com
  `trigger_onepick`, sem API key, JS ou webview) e processá-la como arquivo
  local, com cópia temporária de nome real em `%LOCALAPPDATA%`.
- Cliente REST da Drive API v3 com metadados, download, exportação de planilha
  nativa e renovação única do token; erros de permissão, cota e tamanho em
  PT-BR. Testes offline com transporte falso.
- Botão do Drive ao lado do seletor local, visível só com conta: uma abre direto
  e duas ou mais pedem qual conta usar.

### Changed

- O site público passa a ser publicado por workflow com filtro de caminho: só
  `docs/*.html` gera deployment, e a origem do Pages é GitHub Actions.
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
  aberto e protocolo detalhado; naquele momento, nenhuma das duas estava
  implementada.
- Documentação: o backlog passa a registrar o sistema de plugins — ferramentas
  opcionais em `.7z`, repositório privado para os plugins arriscados e
  documentação pública do contrato; nada implementado.
- Ferramenta de vinculação renomeada para **Verificar Vínculos** na sidebar, no
  cabeçalho e na documentação; a descrição acompanha o novo vocabulário. O
  `id`, os módulos `link` e a regra não mudaram.
- Cabeçalho de vínculo casa sem espaços (`VINCULA(POR NOME)?` e
  `VINCULA (POR NOME)?` são a mesma coluna) e `MIGRAÇÃO` passa a ser sentinela:
  não entra na comparação e é limpa nas linhas que vinculam.
- Log da vinculação sem o nome do arquivo duplicado: leitura, planilha
  carregada, vinculação concluída e totais de CNJ/PASTA/PROTOCOLO/nome aparecem
  uma vez nos dois fluxos. O cartão do Início e o cabeçalho citam as quatro
  planilhas e o fluxo definido pelo anexo.

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
- Reexecução da AGENDA não confunde mais `MIGRAÇÃO` com um protocolo real do
  PROCESSOS; a sentinela é limpa nas linhas que vinculam.
- O atalho global `xl-utils` voltou a abrir: o ambiente do `uv tool` foi
  reinstalado com as dependências do Google. A posição da janela é escolhida
  pelo usuário e não é mais forçada.
- Flet atualizado para 1.1.2 no `.venv`, no lock e no atalho global; a suíte
  passa nessa versão.

### Security

- Endurecimento do repositório público: `.gitignore` cobre variantes de `.env`,
  `.flet/`, chaves, bancos locais e lixo de sistema; `SECURITY.md` define o
  canal privado de relato; o CI declara `contents: read` e pina as actions por
  SHA; e o README passa a declarar todos os direitos reservados.
- Histórico reescrito e repositório recriado para eliminar metadados pessoais
  das refs públicas; o PR e os SHAs antigos deixaram de existir.
- Cliente OAuth do Drive importado só depois de validado (64 KB, UTF-8, HTTPS em
  `google.com`/`googleapis.com`); campos desconhecidos são descartados e o
  arquivo empacotado continua vazio, com teste de guarda. O `.gitignore` cobre
  `drive_client.json` local e os nomes de download do Google.
- O segredo do cliente OAuth importado é cifrado com DPAPI no Windows (campo
  `client_secret_dpapi`); em texto ele só existe em memória durante o login, e
  `ClientConfig` não o expõe em `repr`. O download original pode ser apagado
  depois da importação.
- Login do Drive: pede o escopo canônico
  `https://www.googleapis.com/auth/userinfo.email`; o Google devolve essa forma
  e o `oauthlib` não trata mais a diferença como erro.

## v0.1.0 — 2026-11-04

### Added

- Primeira versão em desenvolvimento: shell do app e utilitários em migração.
