# Roadmap atual

Ciclo ativo: **0007 — Versão e distribuição**. Os ciclos fechados estão em
[`../history/`](../history/README.md).

## Sessões

| Sessão | Entrega | Estado |
|---|---|---|
| S11 | Versão 0.2.0 e polimento de UI | [ ] |
| S12 | Empacotar a primeira versão, 0.3.0 | [ ] |
| — | Sistema de plugins | sem sessão |
| — | Seletor de arquivos integrado à UI | sem sessão |
| — | Drive sem consentimento repetido | sem sessão |

Ordem revisada pelo dono em 2026-11-08: **versão e polimento → primeira
release → plugins → investigações pesadas**.

## S11 — próxima

Três frentes numa sessão só. Ver a
[spec](../sessions/S11-versao-0.2.0-e-polimento.md).

- **Versão 0.2.0:** alinhar `pyproject.toml`, `uv.lock` (depois de `uv lock`),
  `src/xl_utils/__init__.py` (`__version__`), o diagnóstico e onde mais a versão
  aparecer — hoje tudo marca `0.1.0`. É só a marcação; o instalador fica para a
  S12.
- **Responsividade:** em largura reduzida, os títulos dos cartões quebram no
  meio das palavras e a descrição estoura o card, empurrando “Abrir ferramenta”
  para fora; em “Verificar Vínculos” o texto longo piora o quadro. Manter
  título, descrição e atalho dentro do cartão, truncar a descrição com
  reticências e revisar o Início e as páginas em larguras estreitas.
- **E-mail longo no menu de perfis:** truncar com `…` e mostrar o e-mail
  completo em tooltip, com atraso de hover de alguns segundos. Vale para o item
  de perfil e qualquer outro ponto que exiba o e-mail.

## S12 — planejada

Gerar o instalador do Windows pronto para instalação, com Python e dependências
**embutidos**, a partir do wheel: entrada no menu Iniciar, atalho **opcional** na
área de trabalho, ícone do app, desinstalação limpa e publicação do artefato e
das notas na página de Releases do GitHub. Decidir a ferramenta (PyInstaller +
Inno Setup, NSIS ou MSIX) e o que entra no pacote (cliente OAuth, `configs/`,
documentação). A versão passa a 0.3.0 nesta sessão. ADR obrigatório para a
escolha do empacotador.

## Backlog

### Sistema de plugins

Ferramentas opcionais deixam de vir no app e passam a ser instaladas por um
arquivo `.7z`. O que é seguro pode virar padrão; o que é arriscado fica num
repositório privado do dono, só de plugins. Nada é baixado sozinho: instalar é
ato explícito.

- **Pacote:** `.7z` com manifesto, código e assets, validado antes de instalar
  em `%LOCALAPPDATA%/xl_utils/plugins/` — nunca no repositório. A extração
  recusa caminho absoluto, `..`, symlink e zip bomb; confere hash e tamanho e
  não executa código durante a extração.
- **Contrato (ADR antes do código):** manifesto (nome, id, versão,
  compatibilidade, entrypoint e permissões); API de UI (entradas, opções,
  progresso, log e resultado sem importar o shell); ciclo de vida (descoberta,
  carregamento, falha isolada, desinstalação); o que o plugin pode e não pode
  fazer (rede, filesystem, subprocesso); versionamento da API.
- **UI:** área “Plugins” na navegação com lista, instalar, remover e um botão de
  informação que abre a documentação pública: estrutura do `.7z`, manifesto,
  API, exemplo mínimo e checklist de segurança.
- **Pendências:** ADR do contrato, lib de `.7z`, mesmo processo ou subprocesso,
  dependências declaradas pelo plugin, assinatura/hash e modo seguro para
  iniciar sem plugins.

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
- Fechar o ciclo movendo esta página para `docs/history/NNNN-titulo.md` e
  limpando as specs do working tree.

## Gatilhos (não são backlog)

- Suporte a macOS/Linux — só entra quando houver máquina para testar.
- Internacionalização — só entra se aparecer usuário fora do PT-BR.
- Drag & drop real de arquivos — só entra se migrar para PySide6 ou houver hook
  Windows-only.
- **Nuitka no empacotamento da 0.3.0** — verificar viabilidade (tamanho, tempo
  de build e compatibilidade com o Flet) antes de fixar a ferramenta; se não
  servir, seguir com PyInstaller + Inno Setup.

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
