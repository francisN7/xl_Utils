# Roadmap atual

Ciclo ativo: **0008 — Plugins**. Os ciclos fechados estão em
[`README.md`](README.md), nesta mesma pasta.

## Sessões

| Sessão | Entrega | Estado |
|---|---|---|
| S13 | Plugins I — contrato e extração segura | [ ] |
| — | Plugins II — área de Plugins na UI | sem sessão |
| — | Seletor de arquivos integrado à UI | sem sessão |
| — | Drive sem consentimento repetido | sem sessão |

Ordem definida pelo dono: **primeira release → plugins → investigações
pesadas**.

## S13 — próxima

Sistema de plugins começa pelo contrato, não pela tela: ADR com manifesto,
API de UI, ciclo de vida, permissões e versionamento; extração segura do pacote
`.7z` em `%LOCALAPPDATA%/xl_utils/plugins/`, com recusa de caminho absoluto,
`..`, symlink e zip bomb, hash/tamanho conferidos e nada executado durante a
extração. A área “Plugins” na navegação e o primeiro plugin de exemplo ficam na
sessão seguinte. Ver a [spec](../sessions/S13-plugins-contrato.md).

## Backlog

### Plugins II — área de Plugins na UI

Área “Plugins” na navegação com lista, instalar, remover e um botão de
informação que abre a documentação pública: estrutura do `.7z`, manifesto, API,
exemplo mínimo e checklist de segurança. Ferramentas opcionais deixam de vir no
app e passam a ser instaladas por um `.7z`; o que é seguro pode virar padrão, o
que é arriscado fica num repositório privado do dono. Nada é baixado sozinho:
instalar é ato explícito.

- **Pacote:** `.7z` com manifesto, código e assets, validado antes de instalar
  em `%LOCALAPPDATA%/xl_utils/plugins/` — nunca no repositório.
- **Pendências:** dependências declaradas pelo plugin, assinatura/hash e modo
  seguro para iniciar sem plugins.

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
