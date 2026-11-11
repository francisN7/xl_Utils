# ADR 0024 — Plugin carregado só na primeira execução

**Status:** aceita · **Data:** 2026-11-11 · **Contexto:** ciclo 0008, S14

## Contexto

A S13 garantia que instalar e listar não importassem `lib/`. Mas abrir a área
“Plugins” também não precisa de código: identidade, UI e opções vivem no
`plugin.toml`. Importar todos os plugins na abertura custaria tempo de startup,
poderia disparar efeitos colaterais e faria um plugin quebrado derrubar o app
antes de o usuário escolher o que rodar.

## Decisão

- Descoberta, lista e montagem da página usam só o manifesto já lido por
  `scan_installed`; `InstalledPlugin` carrega o `PluginManifest` em memória.
- O `lib/` é importado em `PluginLoader.load`, chamado no primeiro **Executar**
  daquela ferramenta.
- O plugin vira um pacote sintético `xl_utils_plugin_<id>_<hash>` em
  `sys.modules`, com `__path__` apontando para `lib/`. Imports entre arquivos do
  plugin são relativos (`from .helper import x`); o `sys.path` do app não muda.
- Na primeira importação, o host confere que a função do entrypoint existe, é
  chamável e recebe exatamente um parâmetro posicional.
- O módulo fica em cache por id, versão e pasta. Instalar ou remover chama
  `forget`, que descarta o cache e os módulos sintéticos; import parcial é
  limpo em caso de erro.
- Erro de import, função ausente ou assinatura errada vira `PluginLoadError`
  (`plugin_import_failed`, `run_missing`, `run_signature`) e aparece na página,
  no log e no diagnóstico. A lista continua mostrando o plugin como válido,
  porque o manifesto está correto.

## Consequências

- Abrir o app, navegar e listar não dependem do código dos plugins; há teste
  provando que nenhum módulo sintético entra em `sys.modules` nesse caminho.
- Um plugin que só quebra no import se revela no primeiro Executar, não na
  lista. Aceito: o CLI `check` também não executa código.
- Imports absolutos entre arquivos do plugin não funcionam; a documentação do
  autor passa a exigir imports relativos.
- Continua sem sandbox: exceções são isoladas, crash duro (segfault,
  `os._exit`) não é.
- O bundle precisa de `_lzma` e de `shared/plugins` porque a UI os importa; o
  script de build confere `_lzma.pyd` e o exe é aberto sem plugin instalado.

## Alternativas

- **Importar tudo na abertura:** startup caro, risco de efeito colateral e de
  derrubar o app por um plugin malformado.
- **Subprocesso/sandbox desde já:** contrato diferente e fora da API 1; ver ADR
  0023.
- **Inserir `lib/` no `sys.path` durante o import:** nomes genéricos como
  `main` colidem entre plugins e com o app.
