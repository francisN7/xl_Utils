# Backlog — o que foi entregue (2026-11-08)

Ciclo 0006 fechado. O detalhe completo está no Git; as decisões ficam nos ADRs.
O ciclo anterior está em [`0005-polimento.md`](0005-polimento.md); o próximo
começa em [`main.md`](../roadmap/main.md).

| Sessão | Entrega | Estado |
|---|---|---|
| S7a | Vinculação I — motor + AGENDA × PROCESSOS | [x] |
| S7b | Trocar o nome de “Vincular Planilhas” para “Verificar Vínculos” | [x] |
| S7c | Vinculação II — FINANCEIRO, CLIENTES e opções | [x] |
| S7d | Vinculação III — log e acabamento | [x] |
| S8 | Alinhamento de colunas em tela cheia no merge | [x] |
| S9a | Drive I — ADR, OAuth, contas e shell | [x] |
| S9a1 | Drive I.1 — teste do login e importação do cliente | [x] |
| S9a2 | Drive I.2 — menu de perfis no canto superior direito | [x] |
| S9a3 | Site público e política de privacidade | [x] |
| S9a4 | Segredo do cliente OAuth protegido por DPAPI | [x] |
| S9a5 | Login com escopo de e-mail canônico | [x] |
| S9a6 | Janela abre na tela primária | [x] |
| S9b | Drive II — Picker, leitura e botão na entrada | [x] |
| S9c | Drive III — gravação na pasta, exportação e acabamento | [x] |
| S10 | Fechar o ciclo e revisar o backlog | [x] |

Ordem definida pelo dono: **vinculação → tela cheia → Drive**. O Drive ficou por
último porque muda o caminho de saída de todas as ferramentas.

## S7a — entregue

Motor puro em `core/tools/link.py`, duas entradas rotuladas (AGENDA e
PROCESSOS), `VINCULA?` e preservação do protocolo na descrição com
`MIGRAÇÃO`. A config empacotada nasceu em `src/xl_utils/configs/headers.json`
e o override por máquina em `%LOCALAPPDATA%/xl_utils/headers.json`. Detalhes na
spec S7a (histórico no Git) e nos ADRs 0014 e 0015.

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
desligadas. `MIGRAÇÃO` é sentinela e o cabeçalho casa sem espaços. Ver a spec
S7c (histórico no Git) e o ADR 0016.

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
recolore o painel escondido. Ver a spec S8 (histórico no Git) e o ADR 0017.

## S9 — Google Drive

Duas entradas: link da planilha ou seletor de arquivos do Drive. Login pelo
navegador (OAuth), múltiplas contas e “sair” no menu de perfis, com hamburger
no canto superior direito. S9a entregou só a autenticação; S9b, a transferência;
S9c, a exportação nas demais ferramentas e o destino da saída.

## S9a — entregue

ADR 0018 aceito: `google-auth-oauthlib` com PKCE e `state` automáticos,
`drive.file`, loopback em `127.0.0.1` com porta efêmera e timeout, cliente
OAuth empacotado com override em `%LOCALAPPDATA%`, contas por e-mail em
`%LOCALAPPDATA%/xl_utils/drive/` com `refresh_token` cifrado por DPAPI e
gravação atômica. Menu hamburger e cartão do Drive no hub (substituídos na
S9a2 pelo menu de perfis no canto superior direito); o login roda fora da UI
thread. Ver a spec S9a (histórico no Git) e o ADR 0018.

Achado que abriu a S9b: `drive.file` não lê planilha antiga por link colado — só
arquivo criado pelo app ou escolhido no Picker. A S9b resolveu pelo Picker de
desktop, sem API key nem webview; ver a seção da S9b.

## S9a1 — entregue

Fecha a pendência do login: o JSON do cliente OAuth entra pelo seletor nativo
no primeiro clique em **Entrar com Google**, é validado (64 KB, UTF-8, HTTPS em
domínio do Google) e gravado de forma atômica em `%LOCALAPPDATA%`; o dono não
edita arquivo. O fluxo de navegador ganhou teste offline de ponta a ponta com um
Google falso em `127.0.0.1` que confere PKCE e `state`, além de acesso negado,
`state` estranho e timeout. `scripts/check-drive-login.py` cobre o consentimento
real sem imprimir token. O JSON empacotado continua vazio, com teste de guarda.
Ver a spec S9a1 (histórico no Git) e o adendo ao ADR 0018.

## S9a2 — entregue

Ajuste de produto pedido pelo dono: o login deixa de ser um cartão grande no
hub e vira uma ação do menu. O hamburger foi para o canto superior direito da
área de conteúdo, fora da sidebar; o menu lista os perfis com ícone de perfil,
marca a conta ativa, permite adicionar outra e sair. Sem conta, mostra
**Entrar com Google**; se o cliente OAuth ainda não existir, o primeiro clique
pede o JSON uma única vez e segue para o navegador. O cartão `drive_status` foi
removido. Ver a spec S9a2 (histórico no Git).

## S9a3 — entregue

Site estático no GitHub Pages (`docs/`) com a página inicial do xl_Utils e a
política de privacidade, para atender ao modo “Em produção” do Google Auth
Platform. O `_config.yml` mantém ADRs, guias, roadmap, sessões e estado fora do
site. Endereços: `https://francisn7.github.io/xl_Utils/` e
`https://francisn7.github.io/xl_Utils/privacy.html`. Ver a spec S9a3 (histórico
no Git).

## S9a4 — entregue

O cliente OAuth baixado foi instalado em `%LOCALAPPDATA%` e o segredo passou a
ser gravado cifrado por DPAPI no campo `client_secret_dpapi`; em texto ele só
existe em memória durante o login. Fora do Windows, o campo `client_secret`
continua em texto (segredo de app desktop não é confidencial). O download
original foi sobrescrito e apagado, e o `ClientConfig` não expõe mais o segredo
em `repr`. Ver a spec S9a4 (histórico no Git).

## S9a5 — entregue

O login real falhava com `Warning: Scope has changed`: o Google devolve
`https://www.googleapis.com/auth/userinfo.email` mesmo quando o pedido usa o
atalho `email`, e o `oauthlib` trata a diferença como exceção. O app passou a
pedir o escopo canônico; o consentimento real foi validado com `refresh_token`,
`id_token` e os três escopos. Ver a spec S9a5 (histórico no Git).

## S9a6 — entregue

O comando global `xl-utils` voltou a abrir: o ambiente do `uv tool` foi
reinstalado com as dependências do Google. A posição da janela é escolhida pelo
usuário — o monitor secundário é intencional — e não é mais fixada. O Flet fica
sem teto de versão; o lock, o `.venv` e o tool estão em 1.1.2, e a suíte passa
nessa versão. Ver a spec S9a6 (histórico no Git).

## S9b — entregue

O Drive deixou de ser só login: a planilha escolhida no Picker entra no mesmo
pipeline dos arquivos locais. O Picker usado é o de **apps desktop** — OAuth com
`trigger_onepick=true`, retorno em `127.0.0.1`, sem API key, JavaScript ou
webview. Como essa requisição aceita só `drive.file`, a escolha faz uma segunda
autorização curta, sem acesso offline, para não acumular refresh tokens; as
contas da S9a continuam válidas.

`shared/drive_pick.py` escuta uma única resposta, confere `state` e PKCE e
devolve os IDs (um ou vários). `shared/drive.py` lê metadados, baixa binários por
`alt=media`, exporta planilha nativa por `files.export` e renova o token uma vez
em 401, com mensagens em PT-BR. O download vira uma cópia temporária com o nome
real em `%LOCALAPPDATA%/xl_utils/drive/cache/`.

Na entrada, o botão quadrado do Drive fica na mesma linha da dropzone enquanto
houver conta: uma conta abre o Picker direto, duas ou mais perguntam qual. Ler
da pasta de origem e gravar de volta ficou para a S9c, porque `drive.file`
concede arquivo por arquivo. No acabamento, a página **Verificar Vínculos**
voltou a abrir (a fábrica de opções não aceitava o overlay), o botão do Drive
ficou com 44 px no topo da linha e `login_hint` pré-seleciona a conta no
navegador. Ver a spec S9b (histórico no Git) e o adendo ao ADR 0018.

## S9c — entregue

O resultado passou a ser salvo no Drive, na pasta da planilha de origem, sem
passar por `output/`. Quando a entrada veio do Drive, o painel troca “Salvar em
output/” por **Salvar no Drive**; o botão abre o Picker de pasta na primeira
gravação, guarda a concessão por conta em `drive/folders.json` e não pergunta
de novo. A pasta escolhida vale para as próximas gravações; se o usuário
recusar, o arquivo vai para a raiz do Meu Drive com aviso.

O teste real confirmou que a concessão de pasta sobrevive ao token persistido
da conta. O Picker não tem “somente pastas”, então o app soma
`mimetypes=application/vnd.google-apps.folder` e recusa um arquivo se ele
escapar. A conta do navegador precisa ser a mesma do app: `login_hint`
pré-seleciona, mas não força; 403/404 viram `FolderPermissionError` e reabrem a
concessão com a conta certa.

Nada é sobrescrito: o app procura o nome livre e grava `Nome.xlsx`,
`Nome_001.xlsx`... O `.xlsx` é gerado em memória por `core/io.dump_workbook`, o
upload é multipart e o painel mostra “Abrir no Drive”. Com origens em pastas
diferentes, o usuário escolhe uma pasta uma vez. Ver a spec S9c (histórico no
Git) e o adendo ao ADR 0018.

## S10 — entregue

Fechou o ciclo 0006: validou a gravação no Drive com o dono, revisou o backlog,
moveu as páginas fechadas para `docs/history/`, tirou as 14 specs do working
tree e abriu o ciclo 0007. Nenhuma mudança de código. A decisão de manter o
histórico em texto, por ciclo, está no [ADR 0020](../adr/0020-arquivo-do-historico.md).

## Auditoria pública — entregue

Auditoria de segurança e privacidade em 2026-11-07: repositório sem segredos ou
PII, `.gitignore` ampliado, `SECURITY.md`, licença explícita, CI com
`contents: read` e actions pinadas, secret scanning/push protection, PVR,
Dependabot só de alertas, ruleset da `main`, histórico reescrito e repositório
recriado.

## Backlog do ciclo

Revisado pelo dono em 2026-11-08 (S10): versão e polimento → primeira release →
plugins → investigações pesadas. A lista viva está em
[`../roadmap/main.md`](../roadmap/main.md) e abriu o ciclo 0007.
