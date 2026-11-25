# Roadmap atual

Ciclo ativo: **0009 — Investigações de UI**. Os ciclos fechados estão em
[`README.md`](README.md), nesta mesma pasta.

## Sessões

Estado: `[ ]` pendente · `[~]` em andamento · `[x]` concluída. Ao concluir,
a linha recebe entrega e aceite e a spec sai de `docs/sessions/`.

| Sessão | Entrega | Aceite | Estado |
|---|---|---|---|
| S15 | Spike em Flet puro com 25.000 itens; seletor interno restrito à rota do Drive (adendo do ADR 0025) | ADR 0025 aceito com medições; fluxo padrão intacto; ruff, pytest e docs verdes | [x] |
| S16 | Spike do Picker JS em `127.0.0.1` com o token do login; ADR 0026 escolhe esse caminho e descarta o seletor do Drive em Flet | ADR 0026 aceito com medições; fluxo atual intacto; spike fora do Git; ruff, pytest e docs verdes | [x] |
| S17 | Ícone real na sidebar (`assets/icon.png`, fallback “x”) e na janela (`.ico` no Windows, `.png` no Linux); `ui/assets.py` resolve dev e `_MEIPASS`; build leva `assets/` e checa o ícone | Sidebar e janela conferidas no Linux (tema escuro); build Windows pendente de validação no Windows; ruff, pytest e docs verdes | [x] |
| S18 | Plugins saiu do Início e da lista da sidebar e virou item fixo no rodapé, acima de `uv · Python 3.15`; sidebar e app navegam por `id` da página (`TOOLS`, `FOOTER_PAGES`, `PAGES`) | Testes headless do rodapé, do realce único e da abertura por `tool_id`; app conferido pelo dono nos dois temas; ruff, pytest e docs verdes | [x] |
| S19 | Remover Verificar Vínculos e preparar o repo de plugins | — | [ ] |
| S20 | Leitura de planilhas pelo host e API 2 dos plugins | — | [ ] |
| S21 | Menu de perfis do Drive sem troca de conta | — | [ ] |
| S22 | Auditoria dos docs, documentação completa para quem chega e README com badges e screenshots | — | [ ] |
| S23 | Release 0.4.0 e fechamento do ciclo | — | [ ] |

Ordem definida pelo dono: **S15 → S16 → S17 → S18 → S19 → S20 → S21 → S22 →
S23**. A release 0.4.0 entra depois dos ajustes de UI, da limpeza do Verificar
Vínculos e da API 2 dos plugins. Plugins foram entregues no ciclo 0008.

## S18–S23 — próximas

- **S18:** tirar **Plugins** do Início e fixar o item no rodapé da sidebar,
  acima de `uv · Python 3.15`, sem quebrar o índice de navegação.
- **S19:** remover Verificar Vínculos (código, config, testes, docs e site) e
  criar o esqueleto do repo privado `xl_U-Plugins`, com o código atual como
  referência e o guia reutilizável de criação de plugins.
- **S20:** `PluginRequest.reader` para ler com o pipeline do host, incluindo
  arquivos do cache do Drive; API 2 sem compatibilidade com a 1.
- **S21:** menu de perfis nativo, sem `checked` e sem troca de conta; o “Sair
  desta conta” aparece no submenu do e-mail. O salvamento do Drive continua
  usando a conta de origem do arquivo.
- **S22:** auditar todos os `.md` contra o código e deixar a documentação
  completa e intuitiva para quem nunca viu o projeto: trilha de onboarding
  (o que é → rodar → arquitetura → tour do código → primeira contribuição),
  glossário dos termos do domínio (CNJ, AGENDA, FINANCEIRO, `all_str`…),
  diagramas do fluxo de dados e das camadas, guia de contribuição e de
  "onde mexer para…", e conferência de que todo módulo atual aparece em
  `architecture.md`/`code-tour.md`. Atualizar README/site com banner, badges,
  tagline animada e screenshots.
- **S23:** versão 0.4.0, notas, build, Sandbox, publicação e fechamento do
  ciclo 0009; o 0010 nasce limpo.

## Backlog

### Picker JS do Drive (implementação)

O ADR 0026 troca o Picker de desktop pelo Picker JavaScript no navegador, com o
token do login: consentimento só no login, sem mudar `drive.file`. Fica para
depois da 0.4.0, na [spec de backlog](../sessions/S24-seletor-do-drive.md).

### Credenciais do Google no build

O build não embute o cliente OAuth: quem recebe o instalador teria de importar
o JSON. Embutir cliente, API key e número do projeto no build, sem commitar
nada, antes de distribuir para terceiros (ADR 0026).

## Manutenção

- Rodar `uv lock --upgrade` no início do ciclo e validar pandas/Flet — critério:
  testes verdes e app abrindo.
- Revisar o check de docs no CI a cada mudança de documentação.
- Atualizar o code tour quando um módulo do core mudar de papel.
- Refazer o instalador e a validação no Sandbox quando a versão ou o ícone
  mudar; o roteiro está em [`../guide/release-windows.md`](../guide/release-windows.md).
- Fechar o ciclo transformando esta página em `docs/roadmap/NNNN-titulo.md`; as
  specs já saíram a cada encerramento.

## Gatilhos (não são backlog)

- Suporte a macOS/Linux — só entra quando houver máquina para testar.
- Internacionalização — só entra se aparecer usuário fora do PT-BR.
- Drag & drop real de arquivos — só entra se migrar para PySide6 ou houver hook
  Windows-only.
- Auto-update e assinatura de código — só entram se o SmartScreen incomodar
  usuários de verdade.
- Sandbox/subprocesso de plugin — só entra com uma API nova e um motivo real.

## Descartados (não voltam sem decisão nova)

- Histórico de execuções — descartado pelo dono ao fechar o ciclo 0004.
- CLI com `click` — a branch `cli-app` foi apagada; ver ADR 0001.
- `demoji` — incompatível com Python 3.15 e API removida; ver ADR 0001.
- Ferramentas `convert` (JSON → planilha) e `quick_replace` (substituir nomes) —
  saem sem substituto, conforme decisão do dono.
- Página própria de `remove_emoji` — a remoção de emojis entra no pipeline do
  `all_str`; ver ADR 0004.
- Renomear o arquivo original do usuário para “corrigir” extensão — proibido por
  design; a leitura usa o tipo real sem tocar no arquivo.
- Normalizar quebras de linha automaticamente — rejeitado; preservar o texto.
- Arquivar documentação em `.7z`/`.zip` — o Git é o arquivo; ver ADR 0020.
- Nuitka no empacotamento — sem integração com o cliente desktop do Flet; ver
  ADR 0021.
- Importar todos os plugins na abertura do app — ver ADR 0024.
- Migrar a stack para PySide6 ou embutir webview só para ter seletor de arquivos
  — preterido no ADR 0025.
- Seletor do Drive em Flet e escopo `drive`/`drive.readonly` — exigiriam escopo
  restrito e verificação anual; ver ADR 0026.
