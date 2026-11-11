# S13 — Plugins I: contrato e instalação segura

## Objetivo

Definir o contrato de plugins no ADR 0023 e entregar a validação e a instalação
segura de um pacote `.tar.xz` em `%LOCALAPPDATA%/xl_utils/plugins/`, sem UI e
sem carregar código do plugin. Inclui o CLI de autoria `scripts/plugin_cli.py`.

## Fora de escopo

- Área “Plugins”, lista, instalar/remover pela tela, carregamento/execução e o
  primeiro exemplo público — ficam na S14.
- Guia prático (`primeiro-plugin.md`, `empacotar-testar.md`, `exemplos/`) — S14.
- Plugins reais, marketplace, download automático, assinatura de código e
  sandbox/subprocesso.
- Mudar como as cinco ferramentas atuais são descobertas.
- UI de erro; nesta sessão a falha vira exceção/retorno testável.

## Tarefas

1. Atualizar spec/roadmap e escrever o ADR 0023: manifesto, API, ciclo de vida,
   permissões, limites, versionamento e a comparação `.tar.xz` × `.7z` × `.zip`.
2. Registrar a decisão do formato: `.tar.xz` com `tarfile`/`lzma` da stdlib;
   sem dependência nova e sem impacto no instalador.
3. Implementar a validação pura em `core/plugins/`: caminho absoluto, `..`,
   symlink/hardlink, dispositivo, zip bomb, hash/tamanho, manifesto e
   compatibilidade de API.
4. Instalar em staging e promover com `os.replace`; recusar id duplicado;
   desinstalar removendo a pasta e os dados do plugin.
5. Entregar o CLI `scripts/plugin_cli.py` com `pack`, `check`, `install`,
   `list` e `uninstall`, sem executar código do plugin.
6. Cobrir com testes: pacote válido, manifesto inválido, traversal, symlink,
   zip bomb, hash errado, versão incompatível, id duplicado, desinstalação,
   “nada executa” e “nada escapa”.
7. Escrever o contrato em `docs/plugins/` (README, pacote, manifesto, API, UI,
   segurança, versionamento), atualizar `CHANGELOG.md`, `CURRENT.md` e a spec
   da S14.

## Aceite

- [x] ADR 0023 aceito, com alternativas e riscos (mesmo processo × subprocesso).
- [x] Pacote `.tar.xz` válido instala e desinstala em
      `%LOCALAPPDATA%/xl_utils/plugins/`.
- [x] Pacote malicioso (traversal, symlink, zip bomb) é recusado sem escrever
      fora da pasta e sem executar nada.
- [x] Formato medido; instalador sem dependência nova.
- [x] CLI `pack/check/install/list/uninstall` funciona com pacote real.
- [x] `docs/plugins/` cobre o contrato e o check de docs passa.
- [x] `ruff`, `pytest` e `node scripts/check-docs.mjs` verdes.

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `CURRENT.md`, esta spec e o ADR 0023. Abrir `shared/`,
`core/plugins/` e os scripts de build só ao editar; não reler o core das
ferramentas — a sessão não muda regra de negócio existente.

## Arquivos prováveis

- `docs/adr/0023-*.md`, `docs/adr/README.md`, `docs/plugins/`
- `src/xl_utils/core/plugins/`, `src/xl_utils/shared/plugins/`
- `scripts/plugin_cli.py`, `scripts/pack_plugin.py` (se necessário)
- `tests/`, `CHANGELOG.md`, `docs/state/CURRENT.md`, `docs/roadmap/main.md`

## Riscos

- `.tar.xz` é menos familiar que `.7z`: o CLI e a S14 documentam o fluxo.
- `tarfile` tem casos de borda (PAX, nomes longos, sparse, colisões de caixa):
  testar com arquivos reais, sem mock.
- `lzma` pode alocar memória demais: `memlimit` e corte por bytes.
- Sem sandbox: plugin em processo é código confiável; permissões são avisos.
- Atomicidade no Windows: staging no mesmo volume e falha injetada no teste.
- O instalador só embute o módulo quando a S14 ligar a UI; validar `_lzma`
  naquela sessão.

## Próximo depois desta

S14 — Plugins II: área “Plugins”, instalar/remover pela tela, carregamento
isolado, exemplo público e o guia prático em `docs/plugins/`.
