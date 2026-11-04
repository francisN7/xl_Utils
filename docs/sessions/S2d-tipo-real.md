# S2d — Tipo real x extensão

## Objetivo

A entrada mostra o tipo real detectado pelo conteúdo; quando ele diverge da
extensão, o usuário vê o aviso, e uma detecção impossível bloqueia a execução
sem renomear o arquivo.

## Fora de escopo

Renomear, corrigir ou mover o arquivo do usuário; converter formatos; mudar
`resolve_suffix` para confiar só na extensão; detecção por assinatura própria.

## Tarefas

1. Em `core/mime.py`, expor um resumo puro por arquivo: detectado pelo conteúdo,
   extensão declarada, tipo efetivo de leitura e se há divergência ou falha.
   Reaproveitar `detect_suffix` e `resolve_suffix`; não duplicar a regra.
2. Mostrar o tipo na entrada: no card “1. Entrada”, uma linha discreta por
   arquivo quando o detectado divergir da extensão (ex.: “conteúdo: .xlsx ·
   nome: .xls”) e um aviso quando a detecção falhar.
3. Gate em `ToolLayout._run`: se qualquer arquivo não tiver tipo identificável,
   não executar; mostrar “Não foi possível identificar o formato” com a causa e
   registrar no log. A leitura continua usando o tipo real.
4. Testes em `tests/test_format_check.py` com fixtures renomeadas: conteúdo
   `.xlsx` chamado `.xls`, CSV chamado `.xlsx` e HTML chamado `.xlsx`. Cobrir
   leitura correta, aviso de divergência, bloqueio na falha e origem intacta
   (bytes iguais depois da execução).
5. Atualizar `reference/architecture.md` (Detecção de formato),
   `reference/ui.md` (Entrada e Estados), `CURRENT.md`, roadmap e `CHANGELOG.md`.

## Aceite

- [ ] tipo real visível quando diverge da extensão
- [ ] detecção falha bloqueia antes de ler e explica o motivo
- [ ] extensões trocadas são lidas pelo conteúdo, sem renomear a origem
- [ ] log e diagnóstico registram o tipo detectado e a divergência
- [ ] `ruff`, `pytest` e `docs:check` verdes

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec, `core/mime.py`,
`core/io.py` (só `read_workbook` e `list_sheets`), `ui/components/tool_layout.py`
(`_start_sheet_load` e `_run`), `ui/components/file_input.py` e
`reference/architecture.md` (Detecção de formato).

## Arquivos prováveis

- `src/xl_utils/core/mime.py`
- `src/xl_utils/ui/components/tool_layout.py`
- `src/xl_utils/ui/components/file_input.py`
- `tests/test_format_check.py`
- `docs/reference/{architecture,ui}.md`

## Riscos

- `puremagic` pode devolver `.txt` para CSV/HTML; a regra atual já cai para a
  extensão suportada. O gate só bloqueia quando não há tipo confiável nenhum.
- Bloquear CSV legítimo detectado como texto quebraria o fluxo; testar antes.
- A linha de tipo não pode virar poluição visual no caso comum (sem divergência).
- Não incluir conteúdo de célula no aviso, no log ou no diagnóstico.

## Próximo depois desta

S2e — saída escolhida: executar sem gravar, mostrar prévia e salvar só ao clicar,
com arquivo/pasta escolhidos e “Salvar em output/” como atalho.
