# Roadmap atual

Ciclo ativo: **0009 — Investigações de UI**. Os ciclos fechados estão em
[`README.md`](README.md), nesta mesma pasta.

## Sessões

| Sessão | Entrega | Estado |
|---|---|---|
| S15 | Seletor de arquivos integrado à UI — investigação | [ ] |
| S16 | Drive sem consentimento repetido — investigação | [ ] |
| — | Release 0.4.0 (plugins + guia do autor) | no backlog; o dono decide |
| — | Ícone do cabeçalho | sem sessão |

Ordem definida pelo dono: **primeira release → plugins → investigações
pesadas**. Plugins foram entregues no ciclo 0008; a 0.4.0 está pronta para
empacotar quando o dono decidir.

## S15 — próxima

Medir um seletor de arquivos próprio, dentro do tema e do fluxo da janela, e
decidir com evidências se o Flet 1.1 permite ou se a migração para
webview/PySide6 é necessária. A decisão vira ADR 0025; o seletor nativo e o
Picker continuam como fallback obrigatório. Ver a
[spec](../sessions/S15-seletor-de-arquivos.md).

## S16 — esboço

Investigar um pipeline de Drive que use o token do login para listar e escolher
arquivos e pastas dentro do app, comparando consentimento único, verificação do
Google, acesso mínimo, esforço e risco com o desenho atual (`drive.file` +
Picker + concessão de pasta). Não trocar o escopo sem ADR.

## Backlog

### Release 0.4.0

O código dos plugins e o guia do autor estão no repositório; falta decidir a
versão, regerar o instalador e publicar. Segue o roteiro de
[`../guide/release-windows.md`](../guide/release-windows.md), incluindo o teste
do exe com um plugin real instalado.

### Ícone do aplicativo

O instalador e o executável usam o ícone escolhido na S12 (`assets/icon.png` e
`assets/icon.ico`); o cabeçalho do app continua com o ícone padrão. Trocar o
ícone do canto superior esquerdo pelo mesmo desenho, legível em 24–32 px e sem
quebrar o layout do menu.

### Seletor de arquivos integrado à UI

Hoje o arquivo local abre no diálogo nativo do Windows e o do Drive abre uma aba
do navegador; os dois saem do visual e do fluxo da janela. Estudar um seletor
próprio (pastas e arquivos, filtros por formato, recentes e, no Drive, as pastas
já concedidas) que siga o tema e caiba no app, mantendo o seletor nativo e o
Picker como fallback. A decisão depende de o Flet suportar ou de migrar para
webview/PySide6; medir antes — é o escopo da S15.

### Drive sem consentimento repetido

O Picker de desktop exige `prompt=consent` e abre o navegador a cada escolha,
então o login inicial parece não servir para nada. Investigar um pipeline que
use o token do login para listar e escolher arquivos e pastas dentro do app —
por exemplo o Picker web com API key e webview, ou o escopo `drive` com um
navegador próprio — e comparar com o desenho atual (`drive.file` + Picker +
concessão de pasta): consentimento único, verificação do Google, acesso mínimo,
esforço e risco. Não trocar o escopo sem ADR.

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
