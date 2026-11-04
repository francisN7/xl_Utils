# Roadmap atual

Ciclo ativo: **0002 — Migração**. O ciclo anterior está em
[`0001-fundacao.md`](0001-fundacao.md). A ordem segue **valor × custo × risco**:
primeiro o que deixa as próximas sessões mais baratas, depois o que mais dói no
uso. Um item só vira sessão quando a fase é escolhida.

## Fase 1 — Migração dos scripts

Objetivo: substituir cada script da raiz por core + controller + página, sem
duplicação e com teste.

- [x] **S1a — `all_str`.** Pipeline de leitura segura (texto + emojis, sem
  tocar em quebras de linha), reparo sem `xlsx2csv`/`shell=True` e página
  própria. Apagar `all_str.py`. Custo M.
- [x] **S1b — `cnj`.** Regex pura, padronização e deduplicação, usando o
  pipeline do `all_str`. Apagar `cnjs.py`. Custo M.
- [x] **S1c — `cut`.** Recorte por quantidade de linhas, com prévia.
  Apagar `cut.py`. Custo M.
- [x] **S1d — Seleção de abas.** Chips por aba com “Todas”/“Limpar”, nomes no
  core e filtro em `all_str`, `cnj` e `cut`, preservando as abas escolhidas na
  saída. Custo M.
- [x] **S1e — `merge`.** Um único modo: concatena as abas selecionadas de todos
  os arquivos, com coluna `ORIGEM` e alinhamento opcional de colunas. Apagar
  `merge.py`. Custo G.

## Fase 2 — Consolidação

- [x] **S2a — Integração do fluxo.** Testes com planilhas reais fictícias,
  leitura de `.xls`, `.csv` e `.html`, reparo de arquivo corrompido.
- [x] **S2b — Logging e erros.** Log estruturado por execução, erros tipados
  exibidos na UI e botão de copiar diagnóstico.
- [x] **S2c — Opções reais ou nada.** Remover os checkboxes desabilitados de
  Texto e CNJ: o que é obrigatório vira uma frase de comportamento fixo, não um
  controle. O card “2. Opções” só aparece quando há algo editável (linhas do
  recorte, colunas do merge). Custo S.
- [x] **S2d — Tipo real x extensão.** `FormatCheck` mostra o tipo detectado,
  avisa quando diverge da extensão e bloqueia antes de ler quando nada é
  identificável. Testes cobrem `.xlsx` como `.xls`, CSV e HTML como `.xlsx`,
  leitura pelo conteúdo e origem intacta. Nunca renomear o arquivo. Custo M.
- [x] **S2e — Saída escolhida.** Executar sem gravar automaticamente, mostrar a
  prévia e salvar só ao clicar em “Salvar”, escolhendo arquivo (saída única) ou
  pasta (lote), com “Salvar em output/” como atalho. Custo G.

## Fase 3 — Publicação

Objetivo: promover a versão com UI a `main` e manter a `main` antiga como
branch `legacy`, apenas para histórico.

- [ ] **S3a — Promover a UI a `main`.** A `main` atual é ancestral de
  `feat/ui`; avançar `main` até `feat/ui`, criar `legacy` no commit antigo,
  trocar o README da `legacy` por um aviso de descontinuação e publicar as duas.
  Remover `feat/ui` depois. Custo S.
- [ ] **S3b — Sinalizar a `legacy` no GitHub.** Não há selo nativo de “legacy”
  no seletor de branches; usar o nome `legacy`, uma tag `legacy-v1` e
  ruleset/proteção para travar a branch, documentando o aviso no README.
  Custo S.

## Backlog

| Item | Valor | Custo | Pré-requisito |
|---|---|---|---|
| Tema claro opcional | Baixo | S | — |
| Histórico de execuções | Médio | M | S2b |
| Cancelar execução em andamento | Médio | M | S1a |

## Manutenção

- Rodar `uv lock --upgrade` a cada ciclo e validar pandas/Flet — critério:
  testes verdes e app abrindo.
- Revisar `docs:check` no CI a cada mudança de documentação.

## Gatilhos (não são backlog)

- Suporte a macOS/Linux — só entra quando houver máquina para testar.
- Empacotamento, instalador e release — só entram quando o dono decidir
  distribuir.
- Internacionalização — só entra se aparecer usuário fora do PT-BR.
- Drag & drop real de arquivos — só entra se migrar para PySide6 ou houver hook
  Windows-only.

## Descartados (não voltam sem decisão nova)

- CLI com `click` — a branch `cli-app` foi apagada; ver ADR 0001.
- `demoji` — incompatível com Python 3.15 e API removida; ver ADR 0001.
- Ferramentas `convert` (JSON → planilha) e `quick_replace` (substituir
  nomes) — saem sem substituto, conforme decisão do dono.
- Página própria de `remove_emoji` — a remoção de emojis entra no pipeline do
  `all_str`; ver ADR 0004.
- Renomear o arquivo original do usuário para “corrigir” extensão — proibido
  por design; a leitura usa o tipo real sem tocar no arquivo.
- Normalizar quebras de linha automaticamente — rejeitado; preservar o texto.
