# Roadmap atual

Ciclo ativo: **0009 — Investigações de UI**. Os ciclos fechados estão em
[`README.md`](README.md), nesta mesma pasta.

## Sessões

| Sessão | Entrega | Estado |
|---|---|---|
| S15 | Seletor de arquivos integrado à UI — investigação | [x] |
| S16 | Drive sem consentimento repetido — investigação | [ ] |
| S17 | Ícone da sidebar e da janela | [ ] |
| S18 | Plugins no rodapé da sidebar, fora do Início | [ ] |
| S19 | Remover Verificar Vínculos e preparar o repo de plugins | [ ] |
| S20 | Leitura de planilhas pelo host e API 2 dos plugins | [ ] |
| S21 | Menu de perfis do Drive sem troca de conta | [ ] |
| S22 | Auditoria dos docs e README com badges e screenshots | [ ] |
| S23 | Release 0.4.0 e fechamento do ciclo | [ ] |

Ordem definida pelo dono: **S15 → S16 → S17 → S18 → S19 → S20 → S21 → S22 →
S23**. A release 0.4.0 entra depois dos ajustes de UI, da limpeza do Verificar
Vínculos e da API 2 dos plugins. Plugins foram entregues no ciclo 0008.

## S15 — concluída

O spike em Flet puro provou a viabilidade da UI: 25.000 itens, filtro por
formato, recentes, navegação e seleção no tema. O adendo do
[ADR 0025](../adr/0025-seletor-de-arquivos.md) restringe o seletor interno à
**rota do Drive**; arquivo local continua sempre no seletor nativo do sistema
operacional. A listagem definitiva virá da Drive API, a ser medida na S16. A
implementação fica para depois da 0.4.0; nenhum fluxo padrão mudou.

## S16 — próxima

Investigar um pipeline de Drive que use o token do login para listar e escolher
arquivos e pastas dentro do app, comparando consentimento único, verificação do
Google, acesso mínimo, esforço e risco com o desenho atual (`drive.file` +
Picker + concessão de pasta). Não trocar o escopo sem ADR. Ver a
[spec](../sessions/S16-drive-sem-consentimento.md). A implementação do seletor
do Drive (S24) depende desta decisão.

## S17–S23 — próximas

- **S17:** trocar o quadrado “x” da sidebar pelo ícone real e usar o `.ico` no
  cabeçalho da janela; o build precisa levar `assets/` para o lado do exe.
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
- **S22:** auditar todos os `.md`, atualizar README/site e adicionar banner,
  badges, tagline animada e screenshots.
- **S23:** versão 0.4.0, notas, build, Sandbox, publicação e fechamento do
  ciclo 0009; o 0010 nasce limpo.

## Backlog

### Seletor do Drive (implementação)

O adendo do ADR 0025 restringe o seletor interno à rota do Drive; arquivo local
continua no seletor nativo. A implementação depende do ADR 0026 (S16), fica para
depois da 0.4.0 e está na [spec de backlog](../sessions/S24-seletor-do-drive.md).

## Manutenção

- Rodar `uv lock --upgrade` no início do ciclo e validar pandas/Flet — critério:
  testes verdes e app abrindo.
- Revisar o check de docs no CI a cada mudança de documentação.
- Atualizar o code tour quando um módulo do core mudar de papel.
- Refazer o instalador e a validação no Sandbox quando a versão ou o ícone
  mudar; o roteiro está em [`../guide/release-windows.md`](../guide/release-windows.md).
- Fechar o ciclo transformando esta página em `docs/roadmap/NNNN-titulo.md` e
  limpando as specs do working tree.

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
