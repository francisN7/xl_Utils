# S14 — Plugins II: área, carregamento e guia prático

## Objetivo

Levar o contrato da S13 até a UI: área “Plugins” na navegação, lista, instalar
e remover pela tela, carregamento isolado de `run(request)` e o primeiro exemplo
público. Completar `docs/plugins/` com o guia prático que roda de verdade.

## Fora de escopo

- Marketplace, download automático, atualização, assinatura de código e
  catálogo confiável.
- Sandbox/subprocesso: o plugin continua no mesmo processo.
- Dependências nativas ou instalação de pacotes com `pip`.
- Mudar as cinco ferramentas atuais ou o formato `.tar.xz`.

## Tarefas

1. Área “Plugins” na sidebar, com lista de válidos e inválidos, nome, versão,
   API, permissões e caminho; botão para abrir a pasta.
2. Instalar pelo seletor de arquivo, conferir sidecar/manifesto pela API da S13,
   recusar duplicado e mostrar erro sem derrubar o app.
3. Remover com confirmação e aviso de que `data/` também será apagado.
4. Carregar o plugin sem poluir `sys.path`: importar `lib/<modulo>.py` com nome
   sintético, conferir `run` e a assinatura, isolar `ImportError`/exceções e
   registrar no diagnóstico.
5. Montar a página a partir de `[ui]` e `[[options]]`: seletor genérico ou
   `[[ui.inputs]]`, opções tipadas, resultado em `frames`, log, progresso e
   cancelamento; executar fora da UI thread.
6. Publicar `exemplos/hello` e `exemplos/com-opcoes`, e escrever
   `primeiro-plugin.md` e `empacotar-testar.md` com o CLI, instalação,
   desinstalação, códigos de erro e o fluxo do repo privado/CI.
7. Cobrir com testes: página declarativa, carregamento, falha de import,
   assinatura errada, execução, instalar/remover pela UI, “nada executa” na
   descoberta e exemplo dos docs validado/empacotado.

## Aceite

- [ ] “Plugins” aparece na navegação e lista válidos e inválidos.
- [ ] Instalar e remover pela tela funcionam com pacote real.
- [ ] Plugin válido carrega e executa pela UI; plugin quebrado isola o erro.
- [ ] Entradas nomeadas, opções, resultado, log, progresso e cancelamento
      funcionam como no manifesto.
- [ ] `docs/plugins/primeiro-plugin.md`, `empacotar-testar.md` e `exemplos/`
      permitem criar, empacotar e instalar um plugin de ponta a ponta.
- [ ] `ruff`, `pytest`, `node scripts/check-docs.mjs` e build verdes; o bundle
      inclui `_lzma` e abre sem plugin instalado.

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `CURRENT.md`, esta spec, o ADR 0023 e `docs/plugins/README.md`.
Abrir `app.py`, `ui/pages/registry.py`, `ui/components/tool_layout.py`,
`shared/plugins/` e os testes só ao editar. Não reler o core das ferramentas.

## Arquivos prováveis

- `src/xl_utils/ui/pages/plugins.py`, `ui/components/`, `app.py`
- `src/xl_utils/shared/plugins/loader.py`, `api.py`, `install.py`
- `docs/plugins/primeiro-plugin.md`, `empacotar-testar.md`, `exemplos/`
- `tests/test_plugins_ui.py`, `tests/test_plugin_loader.py`
- `CHANGELOG.md`, `CURRENT.md`, `docs/roadmap/main.md`

## Riscos

- Flet não é thread-safe: carregar e executar fora da UI thread, como os
  controllers atuais; nunca atualizar controle dentro de `run`.
- Importar plugin no processo é confiar no código; a UI precisa mostrar as
  permissões e não prometer sandbox.
- Nome sintético de módulo e isolamento de `sys.path` são fáceis de errar;
  testar dois plugins com `main.py` e pacotes diferentes.
- Plugin pode travar a UI ou o processo; falhas de import e exceções são
  isoladas, crash duro não é.
- Instalar/remover com página aberta: invalidar cache de páginas e recarregar.
- O PyInstaller só passa a incluir `shared/plugins` quando a UI importar o
  módulo; conferir `_lzma` e um plugin real no bundle.

## Próximo depois desta

Fechar o ciclo 0008, atualizar a página do ciclo e planejar a release 0.4.0 com
o contrato de plugins e o guia do autor.
