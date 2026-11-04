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
- [ ] **S1e — `merge`.** Um único modo: concatena as abas selecionadas de todos
  os arquivos, com coluna `ORIGEM` e alinhamento opcional de colunas. Apagar
  `merge.py`. Custo G.

## Fase 2 — Consolidação

- [ ] **S2a — Integração do fluxo.** Testes com planilhas reais fictícias,
  leitura de `.xls`, `.csv` e `.html`, reparo de arquivo corrompido.
- [ ] **S2b — Logging e erros.** Log estruturado por execução, erros tipados
  exibidos na UI e botão de copiar diagnóstico.
- [ ] **S2c — Opções reais ou nada.** Remover os checkboxes desabilitados de
  Texto e CNJ: o que é obrigatório vira uma frase de comportamento fixo, não um
  controle. O card “2. Opções” só aparece quando há algo editável (linhas do
  recorte, colunas do merge). Custo S.

## Fase 3 — Distribuição

- [ ] **S3a — Empacotamento.** `flet pack`/PyInstaller, ícone e teste em
  máquina limpa.
- [ ] **S3b — Release.** Notas em `docs/releases/` e tag no GitHub.

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
- Instalador nativo (MSI) — só entra se o PyInstaller não bastar.
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
