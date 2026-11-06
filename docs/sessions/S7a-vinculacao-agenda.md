# S7a — Vinculação I: AGENDA × PROCESSOS

## Objetivo

Gerar a AGENDA com a coluna `VINCULA?` preenchida a partir de PROCESSOS e
preservar o protocolo sem vínculo na descrição, sem alterar o original.

## Fora de escopo

- FINANCEIRO, CLIENTES e `VINCULA (POR NOME)?` — ficam para a S7b.
- Opção “manter apenas um campo vinculante” — fica para a S7c.
- Normalizar CNJ, PASTA, PROTOCOLO ou nome; a comparação é bruta.
- Google Drive e o alinhamento em tela cheia.

## Tarefas

1. Criar `src/xl_utils/configs/headers.json` com as quatro planilhas padrão,
   os campos usados e o separador de descrição; carregar por
   `importlib.resources` com override em `%LOCALAPPDATA%/xl_utils/headers.json`.
2. Implementar o motor puro em `core/tools/link.py`: casar cabeçalho dobrando
   caixa/acento/espaço, validar CNJ, prioridade CNJ → PASTA → PROTOCOLO,
   `VINCULA?`, `MIGRAÇÃO` e `PROTOCOLO: <valor>` na descrição.
3. Criar controller e página com duas entradas rotuladas (AGENDA e PROCESSOS),
   sem seletor de abas; detectar a aba pelo bloco padrão.
4. Registrar a ferramenta no `registry.py` e no Início.
5. Pop-up de reexecução quando o protocolo da AGENDA já contém `MIGRAÇÃO`;
   se confirmar, recalcular `VINCULA?` sem repetir o protocolo na descrição.
6. Gravar `output/<stem> - vinculado.xlsx` ou escolher a pasta; preservar todas
   as colunas e as outras abas da AGENDA.
7. Testes, ADRs 0014 e 0015 e atualização dos docs.

## Aceite

- [x] AGENDA com CNJ válido gera `VINCULA POR CNJ`; PASTA e PROTOCOLO seguem a
  mesma prioridade.
- [x] CNJ mascarado × CNJ cru não vincula, mas é aceito (comparação bruta).
- [x] CNJ fora do padrão para tudo, lista os casos e não grava nada.
- [x] Sem vínculo grava `NÃO vincula, apenas processo consultivo`, preserva
  `PROTOCOLO: <valor>` na descrição e troca o campo por `MIGRAÇÃO`; protocolo
  vazio também vira `MIGRAÇÃO`.
- [x] `VINCULA?` entra depois do bloco padrão e antes das extras; se já
  existir, é sobrescrita no lugar.
- [x] Reexecução avisa e, se confirmada, não duplica a linha do protocolo.
- [x] Original intocado; lint, testes e docs verdes.

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `CURRENT.md` e esta spec. Consultar pontualmente
`core/tools/all_str.py`, `core/save.py`, `ui/components/tool_layout.py`,
`ui/state.py` e `shared/settings.py`. Não abrir os demais controllers.

## Arquivos prováveis

- `src/xl_utils/configs/headers.json`, `src/xl_utils/shared/configs.py`
- `src/xl_utils/core/tools/link.py`, `src/xl_utils/controllers/link.py`
- `src/xl_utils/ui/pages/link.py`, `ui/pages/registry.py`,
  `ui/components/tool_layout.py`, `ui/state.py`
- `tests/test_link.py`, `tests/test_configs.py`
- `docs/adr/0014-*.md`, `docs/adr/0015-*.md`

## Riscos

- CNJ numérico no Excel perde precisão antes da leitura; a ferramenta só pode
  avisar pelos contadores de mascarado/cru. A coluna deve ser texto.
- Cabeçalho repetido ou extra com o mesmo nome dobrado: vale a primeira
  ocorrência, e o match é exato para não pegar `PROCESSO ORIGINÁRIO`.
- Sobrescrever `VINCULA?` no lugar mantém o rótulo que o usuário já tinha.
- O pop-up lê a AGENDA duas vezes (conferência e execução); aceitável para o
  tamanho das planilhas e o original nunca é alterado.

## Próximo depois desta

S7b — acrescentar FINANCEIRO e CLIENTES, `VINCULA (POR NOME)?` e a opção de
nome na descrição.
