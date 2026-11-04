# Roadmap atual

Ciclo ativo: **0005 — Polimento**. O ciclo anterior está em
[`0004-execucao-e-robustez.md`](0004-execucao-e-robustez.md).

## Fase 1 — Aparência

Objetivo: permitir leitura confortável em ambiente claro sem mudar o layout nem
o fluxo das ferramentas.

- [ ] **S6a — Tema claro opcional.** Tokenizar as cores hoje constantes,
  alternar entre Dracula e claro e manter a preferência do usuário. Preservar
  contraste, estados de erro/sucesso e a legibilidade do log e da prévia.
  Custo M. Ver spec.

## Backlog

Sem itens no momento; o tema claro está na Fase 1 deste ciclo.

## Manutenção

- Rodar `uv lock --upgrade` no início do ciclo e validar pandas/Flet — critério:
  testes verdes e app abrindo.
- Revisar `docs:check` no CI a cada mudança de documentação.
- Atualizar o code tour quando um módulo do core mudar de papel.

## Gatilhos (não são backlog)

- Suporte a macOS/Linux — só entra quando houver máquina para testar.
- Empacotamento, instalador e release — só entram quando o dono decidir
  distribuir.
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

## Notas do ciclo

- O ciclo 0004 fechou com execução fora da UI, log ao vivo/cancelamento, CNJ em
  texto sujo e recorte por quantidade.
- O tema claro é o único item que veio do backlog do ciclo anterior; as cores
  são constantes importadas por todos os componentes, daí o custo M.
