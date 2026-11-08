# Roadmap atual

Ciclo ativo: **0006 — Backlog**. O ciclo anterior está em
[`0005-polimento.md`](0005-polimento.md).

## Sessões

| Sessão | Entrega | Estado |
|---|---|---|
| S7a | Vinculação I — motor + AGENDA × PROCESSOS | [x] |
| S7b | Trocar nome de "Vincular Planilhas" para "Verificar Vínculos". | [x] |
| S7c | Vinculação II — FINANCEIRO, CLIENTES e opções | [x] |
| S7d | Vinculação III — log e acabamento | [x] |
| S8 | Alinhamento de colunas em tela cheia no merge | [x] |
| S9a | Drive I — ADR, OAuth, contas e shell | [x] |
| S9a1 | Drive I.1 — teste do login e importação do cliente | [x] |
| S9a2 | Drive I.2 — menu de perfis no canto superior direito | [x] |
| S9a3 | Site público e política de privacidade | [x] |
| S9a4 | Segredo do cliente OAuth protegido por DPAPI | [x] |
| S9a5 | Login com escopo de e-mail canônico | [x] |
| S9b | Drive II — link/seletor e escrita do resultado | [ ] |
| S9c | Drive III — exportação nas demais e acabamento | [ ] |

Ordem definida pelo dono: **vinculação → tela cheia → Drive**. O Drive fica por
último porque muda o caminho de saída de todas as ferramentas; a S9 só vira
duas ou três sessões depois do ADR de autenticação.

## S7a — entregue

Motor puro em `core/tools/link.py`, duas entradas rotuladas (AGENDA e
PROCESSOS), `VINCULA?` e preservação do protocolo na descrição com
`MIGRAÇÃO`. A config empacotada nasceu em `src/xl_utils/configs/headers.json`
e o override por máquina em `%LOCALAPPDATA%/xl_utils/headers.json`. Detalhes na
[spec](../sessions/S7a-vinculacao-agenda.md) e nos ADRs 0014 e 0015.

## S7b — nome da ferramenta

“Vincular Planilhas” passa a se chamar **Verificar Vínculos** na sidebar, no
cabeçalho da página, no README e na referência. A descrição acompanha o novo
vocabulário. O `id` interno, os módulos e a regra de vinculação não mudam.

## S7c — entregue

Quatro entradas rotuladas, sem checkbox de fluxo: AGENDA e/ou FINANCEIRO
anexados definem o que roda. AGENDA exige PROCESSOS; FINANCEIRO exige
PROCESSOS ou CLIENTES. No FINANCEIRO, `VINCULA?` usa a mesma prioridade
CNJ → PASTA → PROTOCOLO; `VINCULA (POR NOME)?` recebe SIM/NÃO comparando o
nome com a lista de PROCESSOS (split cru por `;`) e CLIENTES. Só CLIENTES gera
apenas a coluna de nome. Duas opções: “nome sem vínculo na descrição” e
“manter apenas um campo vinculante” (AGENDA e/ou FINANCEIRO), ambas
desligadas. `MIGRAÇÃO` é sentinela e o cabeçalho casa sem espaços. Ver
[spec](../sessions/S7c-vinculacao-financeiro.md) e ADR 0016.

## S7d — entregue

Log por etapa nos dois fluxos, com leitura, planilha carregada, vinculação
concluída e totais de CNJ/PASTA/PROTOCOLO/nome, sem duplicar o nome do arquivo.
O cartão do Início e o cabeçalho citam as quatro planilhas e o fluxo definido
pelo anexo; textos e docs foram revisados. O grupo 1 dos exemplos confere com o
gabarito; o grupo 2 para no CNJ inválido como esperado.

## S8 — entregue

Botão de tela cheia ao lado de “Alinhamento de colunas”. O `OverlayHost` do
`ToolLayout` cobre o conteúdo da página e distribui os cards de 196 px com a
sobra como espaçamento; “CONFIRMAR” fica no canto inferior direito e o mesmo
ícone restaura. Grupos, seleção e ordem não são reconstruídos, e o tema
recolore o painel escondido. Ver a [spec](../sessions/S8-tela-cheia-merge.md)
e o ADR 0017.

## S9 — Google Drive

Duas entradas: link da planilha ou seletor de arquivos do Drive. Login pelo
navegador (OAuth), múltiplas contas e “sair” no menu de perfis, com hamburger
no canto superior direito. S9a entrega só a autenticação; S9b, a transferência;
S9c, a exportação nas demais ferramentas e o destino da saída.

## S9a — entregue

ADR 0018 aceito: `google-auth-oauthlib` com PKCE e `state` automáticos,
`drive.file`, loopback em `127.0.0.1` com porta efêmera e timeout, cliente
OAuth empacotado com override em `%LOCALAPPDATA%`, contas por e-mail em
`%LOCALAPPDATA%/xl_utils/drive/` com `refresh_token` cifrado por DPAPI e
gravação atômica. Menu hamburger e cartão do Drive no hub (substituídos na
S9a2 pelo menu de perfis no canto superior direito); o login roda fora da UI
thread. Ver a [spec](../sessions/S9a-drive-autenticacao.md) e o ADR 0018.

Achado para a S9b: `drive.file` não lê planilha antiga por link colado — só
arquivo criado pelo app ou escolhido no Google Picker. A S9b começa decidindo
entre Picker e escopo `drive` em modo Testing.

## S9a1 — entregue

Fecha a pendência do login: o JSON do cliente OAuth entra pelo seletor nativo
no primeiro clique em **Entrar com Google**, é validado (64 KB, UTF-8, HTTPS em
domínio do Google) e gravado de forma atômica em `%LOCALAPPDATA%`; o dono não
edita arquivo. O fluxo de navegador ganhou teste offline de ponta a ponta com um
Google falso em `127.0.0.1` que confere PKCE e `state`, além de acesso negado,
`state` estranho e timeout. `scripts/check-drive-login.py` cobre o consentimento
real sem imprimir token. O JSON empacotado continua vazio, com teste de guarda.
Ver a [spec](../sessions/S9a1-login-e-cliente.md) e o adendo ao ADR 0018.

## S9a2 — entregue

Ajuste de produto pedido pelo dono: o login deixa de ser um cartão grande no
hub e vira uma ação do menu. O hamburger foi para o canto superior direito da
área de conteúdo, fora da sidebar; o menu lista os perfis com ícone de perfil,
marca a conta ativa, permite adicionar outra e sair. Sem conta, mostra
**Entrar com Google**; se o cliente OAuth ainda não existir, o primeiro clique
pede o JSON uma única vez e segue para o navegador. O cartão `drive_status` foi
removido. Ver a [spec](../sessions/S9a2-menu-de-perfis.md).

## S9a3 — entregue

Site estático no GitHub Pages (`docs/`) com a página inicial do xl_Utils e a
política de privacidade, para atender ao modo “Em produção” do Google Auth
Platform. O `_config.yml` mantém ADRs, guias, roadmap, sessões e estado fora do
site. Endereços: `https://francisn7.github.io/xl_Utils/` e
`https://francisn7.github.io/xl_Utils/privacy.html`. Ver a
[spec](../sessions/S9a3-site-publico.md).

## S9a4 — entregue

O cliente OAuth baixado foi instalado em `%LOCALAPPDATA%` e o segredo passou a
ser gravado cifrado por DPAPI no campo `client_secret_dpapi`; em texto ele só
existe em memória durante o login. Fora do Windows, o campo `client_secret`
continua em texto (segredo de app desktop não é confidencial). O download
original foi sobrescrito e apagado, e o `ClientConfig` não expõe mais o segredo
em `repr`. Ver a [spec](../sessions/S9a4-segredo-protegido.md).

## S9a5 — entregue

O login real falhava com `Warning: Scope has changed`: o Google devolve
`https://www.googleapis.com/auth/userinfo.email` mesmo quando o pedido usa o
atalho `email`, e o `oauthlib` trata a diferença como exceção. O app passou a
pedir o escopo canônico; o consentimento real foi validado com `refresh_token`,
`id_token` e os três escopos. Ver a [spec](../sessions/S9a5-escopo-email.md).

## Auditoria pública — entregue

Auditoria de segurança e privacidade em 2026-11-07: repositório sem segredos ou
PII, `.gitignore` ampliado, `SECURITY.md`, licença explícita, CI com
`contents: read` e actions pinadas, secret scanning/push protection, PVR,
Dependabot só de alertas, ruleset da `main`, histórico reescrito e repositório
recriado. O backlog de plugins entrou em seguida.

## Backlog

- **Responsividade do Início e das ferramentas** — sem sessão marcada. Em
  largura reduzida, os títulos dos cartões quebram no meio das palavras e a
  descrição estoura o card, empurrando “Abrir ferramenta” para fora; em
  “Verificar Vínculos” o texto mais longo piora o quadro. A correção deve
  manter título, descrição e atalho dentro do cartão, truncar ou ocultar a
  descrição com reticências quando faltar espaço e revisar o Início e as
  páginas de ferramenta em larguras estreitas. Prioridade fica com o dono.
- **Sistema de plugins** — sem sessão marcada. Ferramentas opcionais deixam de
  vir no app e passam a ser instaladas por um arquivo `.7z`. O que é seguro
  pode virar padrão; o que é arriscado fica num repositório privado do dono, só
  de plugins. A área de plugins terá um botão de informação que abre a
  documentação pública no GitHub: como o plugin deve ser feito, como se integra
  à UI e o que o pacote precisa conter.

### Detalhe: plugins

**Objetivo.** Separar o núcleo estável das ferramentas pessoais ou arriscadas.
O app padrão carrega só o que é seguro; o resto é instalado sob demanda, sem
baixar nada sozinho.

**Pacote.** Um `.7z` com manifesto, código e assets. O app valida o manifesto,
mostra nome, versão, autor e descrição, e instala em
`%LOCALAPPDATA%/xl_utils/plugins/` — nunca dentro do repositório. Instalação e
remoção acontecem pela área de plugins, com confirmação e sem sobrescrever
versão em uso.

**Contrato do plugin.** Antes do código, um ADR define:

- o manifesto (nome, id, versão, compatibilidade, entrypoint e permissões);
- a API de UI (como a página declara entradas, opções, progresso, log e
  resultado sem importar o shell inteiro);
- o ciclo de vida (descoberta, carregamento, falha isolada e desinstalação);
- o que o plugin pode e não pode fazer (rede, filesystem, subprocesso);
- versionamento e compatibilidade com o app.

**Confiança.** O `.7z` vem de um repositório privado do dono; o app não baixa
plugin sozinho. Instalar é ato explícito. O manifesto pode exigir hash do
pacote e o app registra a origem. Plugin quebrado não derruba o núcleo.

**Segurança do pacote.** A extração recusa caminho absoluto, `..`, symlink e
zip bomb; o app confere hash e tamanho antes de instalar e nunca executa código
durante a extração. O plugin roda com o mesmo usuário do app, então a confiança
é explícita e reversível.

**UI.** Nova área “Plugins” na navegação, com lista, instalar, remover e um
botão de informação que abre a documentação pública: estrutura do `.7z`,
manifesto, API de UI, exemplo mínimo e checklist de segurança.

**Docs.** O contrato do plugin é público, mesmo que os plugins em si fiquem no
repositório privado. A página de informação da UI aponta para essa documentação.

**Pendências.** ADR do contrato; lib de `.7z`; se o plugin roda no mesmo
processo ou em subprocesso; como versionar a API; se plugins declaram
dependências; política de assinatura/hash; modo seguro para iniciar sem
plugins.

## Manutenção

- Rodar `uv lock --upgrade` no início do ciclo e validar pandas/Flet — critério:
  testes verdes e app abrindo.
- Revisar o check de docs no CI a cada mudança de documentação.
- Atualizar o code tour quando um módulo do core mudar de papel.

## Gatilhos (não são backlog)

- Suporte a macOS/Linux — só entra quando houver máquina para testar.
- Empacotamento, instalador e release — só entram quando o dono decidir
  distribuir. A config já nasce pronta para o wheel.
- Internacionalização — só entra se aparecer usuário fora do PT-BR.
- Drag & drop real de arquivos — só entra se migrar para PySide6 ou houver hook
  Windows-only.

## Descartados (não voltam sem decisão nova)

- Histórico de execuções — descartado pelo dono ao fechar o ciclo 0004.
- CLI com `click` — a branch `cli-app` foi apagada; ver ADR 0001.
- `demoji` — incompatível com Python 3.15 e API removida; ver ADR 0001.
- Ferramentas `convert` (JSON → planilha) e `quick_replace` (substituir
  nomes) — saem sem substituto, conforme decisão do dono.
- Página própria de `remove_emoji` — a remoção de emojis entra no pipeline do
  `all_str`; ver ADR 0004.
- Renomear o arquivo original do usuário para “corrigir” extensão — proibido
  por design; a leitura usa o tipo real sem tocar no arquivo.
- Normalizar quebras de linha automaticamente — rejeitado; preservar o texto.
