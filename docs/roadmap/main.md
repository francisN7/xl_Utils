# Roadmap atual

Fases e backlog. A ordem segue **valor × custo × risco**: primeiro o que deixa as
próximas sessões mais baratas, depois o que mais dói no uso. Um item só vira
sessão quando a fase é escolhida.

## Fase 0 — Fundação

Objetivo: app desktop navegável, com tema Dracula e ambiente reproduzível.

- [x] **S0a — Scaffold e contexto.** Branch `feat/ui`, uv no Python 3.15,
  estrutura MVC híbrida, shell Flet com placeholders, helpers de core com
  testes e documentação entre sessões. Custo M.
- [x] **S0b — UI base.** Tema Dracula, sidebar própria com Início, quatro
  cartões alinhados à esquerda, entrada de arquivo, resultado com prévia,
  barra de ação e estado por ferramenta. Custo M/L.

## Fase 1 — Migração dos scripts

Objetivo: substituir cada script da raiz por core + controller + página, sem
duplicação e com teste.

- [ ] **S1a — `all_str`.** Pipeline de leitura segura (texto + emojis, sem
  tocar em quebras de linha), reparo sem `xlsx2csv`/`shell=True` e página
  própria. Apagar `all_str.py` e `remove_emoji.py`. Custo M.
- [ ] **S1b — `cnj`.** Regex pura, padronização e deduplicação, usando o
  pipeline do `all_str`. Apagar `cnjs.py`. Custo M.
- [ ] **S1c — `cut`.** Recorte por quantidade de linhas, com prévia.
  Apagar `cut.py`. Custo M.
- [ ] **S1d — `merge`.** Unificar arquivos ou abas, com erros tipados.
  Apagar `merge.py`. Custo M.

## Fase 2 — Consolidação

- [ ] **S2a — Integração do fluxo.** Testes com planilhas reais fictícias,
  leitura de `.xls`, `.csv` e `.html`, reparo de arquivo corrompido.
- [ ] **S2b — Logging e erros.** Log estruturado por execução, erros tipados
  exibidos na UI e botão de copiar diagnóstico.

## Fase 3 — Distribuição

- [ ] **S3a — Empacotamento.** `flet pack`/PyInstaller, ícone e teste em
  máquina limpa.
- [ ] **S3b — Release.** Notas em `docs/releases/` e tag no GitHub.

## Backlog

| Item | Valor | Custo | Pré-requisito |
|---|---|---|---|
| Tema claro opcional | Baixo | S | S0b |
| Histórico de execuções | Médio | M | S2b |
| Abrir pasta de saída no Explorer/Finder | Alto | S | S0b |
| Cancelar execução em andamento | Médio | M | S0b |
| Arrastar e soltar múltiplos arquivos | Alto | S | S0b |

## Manutenção

- Rodar `uv lock --upgrade` a cada ciclo e validar pandas/Flet — critério:
  testes verdes e app abrindo.
- Revisar `docs:check` no CI a cada mudança de documentação.

## Gatilhos (não são backlog)

- Suporte a macOS/Linux — só entra quando houver máquina para testar.
- Instalador nativo (MSI) — só entra se o PyInstaller não bastar.
- Internacionalização — só entra se aparecer usuário fora do PT-BR.

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
