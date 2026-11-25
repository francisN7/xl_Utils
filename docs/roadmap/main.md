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
| S19 | Verificar Vínculos saiu do app (core, controller, página, `shared/configs.py`, `headers.json`, testes) junto com o `pre_run` e as exceções da vinculação no `ToolLayout`; ADR 0027 (0014/0016 substituídas, adendo no 0015); repo privado `xl_U-Plugins` com `uv init`, estrutura de contexto, `_molde/`, guia e `link/referencia/` | grep sem `link`/Vínculos em `src/` e `tests/`; teste headless de quatro cartões e Plugins só no rodapé; `_molde` passa no `check`; ruff, pytest e docs verdes; app aberto no Linux | [x] |
| S20 | API 2 dos plugins: `request.reader` (`shared/plugins/reader.py`) lê pelo `prepare_workbook` só as abas marcadas (`all_sheets=True` traz todas), com cache por execução, `ReadError` e etapa/log por arquivo; API 1 aposentada com motivo; exemplos 2.0.0 e docs `docs/plugins/`; ADR 0028; `_molde` do `xl_U-Plugins` na API 2 | Reader igual às nativas em xlsx/xls/csv/html e no cache do Drive; API 1 inválida com motivo na área Plugins (conferida no `--web`), no `list` e no `check`; `_molde` passa no `check`; execução no app com arquivo real fica com o dono; ruff, pytest e docs verdes | [x] |
| S21a | Avatar + nome da conta selecionada no lugar do hambúrguer; painel (`MenuBar` + `SubmenuButton`) com cabeçalho, “Outras contas” retrátil, “Adicionar conta” e “Sair” fixos; Sair seleciona a próxima; “Abrir do Drive” abre direto na selecionada; “Salvar no Drive” só na conta de origem, com tooltip e aviso; ADR 0029 | Spike no `--web` com contas falsas nos dois temas (abrir, expandir, trocar, sair, adicionar, cabeçalhos sem sobreposição); `tests/test_top_menu.py` novo e testes de sessão, entrada e gravação; conferência no desktop e com conta real do Google fica com o dono; ruff, pytest e docs verdes | [x] |
| S21c | Login do Drive no Linux: fora do Windows o `refresh_token` vai para o chaveiro do sistema (`keyring`, Secret Service/KWallet), Windows segue no DPAPI; Sair apaga o segredo; versão Linux sai dos gatilhos para o backlog; ADR 0030. Feita antes da S21b, a pedido do dono | Gravar, ler e apagar um token falso no chaveiro real do KDE; testes do cofre em memória (o `conftest` isola o chaveiro real); login com conta real do Google no Linux fica com o dono; ruff, pytest e docs verdes | [x] |
| S21b | Engrenagem da conta: foto e apelido. Engrenagem (`MenuItemButton`) no cabeçalho do painel abre o diálogo “Configurar conta” (`ui/components/account_settings.py`) com prévia, Escolher/Remover foto e apelido (≤16); `shared/profiles.py` recorta no centro, reduz a PNG 256 px (Pillow) e grava em `drive/profiles/` pelo hash da conta (`accounts.account_key`), de forma atômica; apelido no topo, no painel e no tooltip de “Abrir do Drive”; foto no avatar com as iniciais de reserva; Sair apaga o perfil da conta; ADR 0031 | Questionário: diálogo, Pillow 256 px, centro automático; spike no `--web` com contas falsas em raiz temporária nos dois temas (engrenagem fecha o painel e abre o diálogo, apelido no topo e no painel, foto no avatar, Remover + Cancelar não grava); testes de perfil, menu, diálogo e tooltip; escolher foto real no desktop e build Windows com Pillow ficam com o dono; ruff, pytest e docs verdes | [x] |
| S21d | Correção urgente: resultado acima do limite do Excel. `core/save.py` ganha `ROW_LIMIT = 1_000_000` e `split_item`; `save_item`, `save_to_output`, `save_chosen` e `DriveSession._save_sync` gravam um arquivo por parte (`_parte1`, `_parte2`…), com cabeçalho; limite redondo por escolha do dono, para margem | Merge fictício de 1.240.948 × 12 salvo em `Merge_parte1.xlsx` (33 MB) e `Merge_parte2.xlsx` (8 MB) em cerca de 5 min; testes de divisão em `output/`, arquivo escolhido e Drive; a planilha real fica com o dono; ruff, pytest e docs verdes | [x] |
| S22 | Auditoria dos docs, documentação completa para quem chega e README com badges e screenshots | — | [ ] |
| S23 | Release 0.4.0 e fechamento do ciclo | — | [ ] |

Ordem definida pelo dono: **S15 → S16 → S17 → S18 → S19 → S20 → S21a → S21c →
S21b → S21d → S22 → S23** (a S21c entrou antes da S21b e a S21d antes da S22,
por urgência). A release 0.4.0 entra depois dos ajustes de UI, da limpeza do Verificar
Vínculos e da API 2 dos plugins. Plugins foram entregues no ciclo 0008.

## S18–S23 — próximas

- **S18:** tirar **Plugins** do Início e fixar o item no rodapé da sidebar,
  acima de `uv · Python 3.15`, sem quebrar o índice de navegação.
- **S19:** remover Verificar Vínculos (código, config, testes, docs e site) e
  criar o esqueleto do repo privado `xl_U-Plugins`, com o código atual como
  referência e o guia reutilizável de criação de plugins.
- **S20:** `PluginRequest.reader` para ler com o pipeline do host, incluindo
  arquivos do cache do Drive; API 2 sem compatibilidade com a 1.
- **S21a:** painel de perfil no topo (avatar + nome), outras contas numa
  lista retrátil, “Adicionar conta” e “Sair” fixos; “Abrir do Drive” abre
  direto na conta selecionada. Salvar no Drive continua na conta de origem e
  avisa quando ela saiu.
- **S21b:** engrenagem no painel abre a configuração da conta: foto escolhida
  do disco (sem foto, a inicial) e apelido no lugar do e-mail; os dois somem
  no “Sair”.
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

### Picker do Drive só com planilhas

Hoje o Picker de abrir aceita qualquer arquivo (vídeo, `.rar`, `.zip`…). Ele
deve mostrar e deixar escolher só planilhas (`.xlsx`, `.xls`, `.csv` e Planilha
Google), com as pastas visíveis para navegar. O Picker de desktop
(`shared/drive_pick.py`) já usa o parâmetro `mimetypes` na escolha de pasta;
falta passar a lista de MIME de planilha na escolha de arquivo e conferir que
as pastas continuam navegáveis. No Picker JS (S24) o equivalente é
`DocsView.setMimeTypes`. Rede de segurança: rejeitar com aviso o arquivo
escolhido que não for planilha, antes de baixar.

### Credenciais do Google no build

O build não embute o cliente OAuth: quem recebe o instalador teria de importar
o JSON. Embutir cliente, API key e número do projeto no build, sem commitar
nada, antes de distribuir para terceiros (ADR 0026).

### Revisão completa do código

Revisar o repo inteiro atrás de bugs de lógica e execução, decisões ruins ou
contraditórias, código mal otimizado, funções que deveriam ser separadas e
reaproveitadas, nomes pouco intuitivos, código não idiomático ou fora de clean
code e trechos sem comentário ou explicação. Primeiro sai um relatório com
evidências; depois, sessões de correção.

### Sobre o app

Mostrar o número da versão, os créditos, a licença e o link para o repositório
no GitHub. O menu hambúrguer saiu na S21a; o lugar (painel de perfil ou rodapé
da sidebar) se decide na sessão.

### Versão Linux

O dono passou a usar só Linux. O app já roda no Linux pelo `uv run xl-utils`, e
o login do Drive guarda o token no chaveiro (ADR 0030). Falta a distribuição:
build e pacote para Linux (formato a decidir: AppImage, `.deb`, Flatpak ou
`flet build linux`), ícone e atalho, cliente OAuth no build e um roteiro de
release como o do Windows. O planejamento do próximo ciclo já considera as
versões Windows e Linux; o Windows só pode ser validado por quem tiver a
máquina.

### Ajuda ( i ) em cada ferramenta

Botão ( i ) em cada ferramenta que abre uma página web local explicando o uso
(a UI) e a lógica aplicada por trás. Tema Dracula e Alucard, acompanhando o
escuro e o claro do app, com animação de cara tecnológica e transições.

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

- Suporte a macOS — só entra quando houver máquina para testar.
- Internacionalização — só entra se aparecer usuário fora do PT-BR.
- Drag & drop real de arquivos — só entra se migrar para PySide6 ou houver hook
  Windows-only.
- Auto-update e assinatura de código — só entram se o SmartScreen incomodar
  usuários de verdade.
- Sandbox/subprocesso de plugin — só entra com uma API nova e um motivo real.
- Verificação do sistema de plugins com o plugin de Vínculo — só vira sessão
  quando o dono avisar que terminou o plugin no `xl_U-Plugins`.

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
