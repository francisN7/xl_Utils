# Roadmap atual

Ciclo ativo: **0008 — Plugins**. Os ciclos fechados estão em
[`README.md`](README.md), nesta mesma pasta.

## Sessões

| Sessão | Entrega | Estado |
|---|---|---|
| S13 | Plugins I — contrato e extração segura | [x] |
| S14 | Plugins II — área, carregamento e guia | [ ] |
| — | Seletor de arquivos integrado à UI | sem sessão |
| — | Drive sem consentimento repetido | sem sessão |

Ordem definida pelo dono: **primeira release → plugins → investigações
pesadas**.

## S13 — concluída

Contrato no ADR 0023, pacote `.tar.xz` com `tarfile`/`lzma`, validação pura,
instalação atômica em `%LOCALAPPDATA%/xl_utils/plugins/`, sidecar SHA-256 e
limites contra zip bomb. O CLI `scripts/plugin_cli.py` empacota, confere,
instala, lista e remove sem executar código. O contrato do autor está em
`docs/plugins/`. Ver a [spec](../sessions/S13-plugins-contrato.md).

## S14 — próxima

Área “Plugins” na navegação com lista, instalar e remover pela tela, carregar
`run(request)` isolado e o primeiro exemplo público. Completar o guia do autor
com `primeiro-plugin.md`, `empacotar-testar.md` e `exemplos/`, incluindo o fluxo
do repo privado/CI. O plugin continua no mesmo processo, com permissões
declarativas e sem sandbox. Ver a [spec](../sessions/S14-plugins-ui.md).

## Backlog

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
webview/PySide6; medir antes.

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
- [x] S12b — devolver os ciclos fechados a `docs/roadmap/` (ADR 0022).

## Gatilhos (não são backlog)

- Suporte a macOS/Linux — só entra quando houver máquina para testar.
- Internacionalização — só entra se aparecer usuário fora do PT-BR.
- Drag & drop real de arquivos — só entra se migrar para PySide6 ou houver hook
  Windows-only.
- Auto-update e assinatura de código — só entram se o SmartScreen incomodar
  usuários de verdade.

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
