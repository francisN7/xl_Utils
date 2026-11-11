# Ciclo 0008 — Plugins

Fechado em 2026-11-11. Ciclo anterior:
[`0007-versoes-e-distribuicao.md`](0007-versoes-e-distribuicao.md).

## Sessões

| Sessão | Entrega | Estado |
|---|---|---|
| S13 | Plugins I — contrato e extração segura | [x] |
| S14 | Plugins II — área, carregamento e guia | [x] |

Ordem definida pelo dono: **primeira release → plugins → investigações
pesadas**.

## S13 — concluída

Contrato no ADR 0023, pacote `.tar.xz` com `tarfile`/`lzma`, validação pura,
instalação atômica em `%LOCALAPPDATA%/xl_utils/plugins/`, sidecar SHA-256 e
limites contra zip bomb. O CLI empacota, confere, instala, lista e remove sem
executar código. O contrato do autor está em `docs/plugins/`.

## S14 — concluída

Área “Plugins” na navegação com lista de válidos e inválidos, instalação pelo
seletor com confirmação de permissões, remoção com aviso sobre `data/` e
abertura da ferramenta. O `lib/` só é importado no primeiro Executar, em pacote
sintético, com cache por id/versão/pasta (ADR 0024) — abrir o app, listar ou
montar a página não importa código de plugin.

A página é montada de `[ui]`/`[[options]]` com os quatro tipos de opção, slots
nomeados, log, progresso e cancelamento; erro de import vira diagnóstico sem
derrubar o app. O CLI passou a ser instalado como `xl-utils-plugin` e o guia do
autor ganhou `primeiro-plugin.md`, `empacotar-testar.md` e `exemplos/hello` +
`exemplos/com-opcoes`, validados no pytest. Build com `_lzma` conferido no
bundle.

## Descartados neste ciclo

- Sandbox, subprocesso, marketplace, download automático, atualização,
  assinatura de código e catálogo confiável — fora da API 1; ver ADR 0023.
- Tratar o SHA-256 como prova de autoria — o sidecar é integridade; ver ADR
  0023.
- Importar todos os plugins na abertura — decisão contrária no ADR 0024.
