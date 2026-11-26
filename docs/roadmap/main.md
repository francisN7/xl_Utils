# Roadmap atual

Ciclo ativo: **0010 — Drive e ajuda no app**. Os ciclos fechados estão em
[`README.md`](README.md), nesta mesma pasta.

## Sessões

Estado: `[ ]` pendente · `[~]` em andamento · `[x]` concluída. Ao concluir,
a linha recebe entrega e aceite e a spec sai de `docs/sessions/`.

| Sessão | Entrega | Aceite | Estado |
|---|---|---|---|
| S24 | Picker JavaScript do Drive no navegador, com o token do login (ADR 0026) | — | [ ] |

A S24 abre o ciclo
([spec](../sessions/S24-seletor-do-drive.md)). As próximas sessões saem do
backlog abaixo, na ordem que o dono definir.

## Backlog

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
