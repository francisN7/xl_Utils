# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S1e — mesclagem de planilhas
- **Próxima:** S2a — integração do fluxo (`docs/sessions/S2a-integracao.md`)
- **Ciclo:** 0002 — Fase 1 concluída; início da Fase 2 — Consolidação
- **Retorno:** `core/tools/merge.py`, `controllers/merge.py`, `ui/pages/merge.py`
- **Decisões abertas:** nenhuma; alinhamento do merge por dropdown (ADR 0005)

## Pronto

- Ambiente uv/Python 3.15, Flet desktop e pandas 3.1; MVC híbrido e tema Dracula.
- `prepare_workbook` lê tudo como texto, remove emojis, preserva quebras e tenta
  reparo; falha vira `WorkbookReadError`.
- Texto, CNJ, recorte e merge prontos e salvando em `output/`; as três primeiras
  aceitam lote e processam cada origem separadamente.
- `list_sheets` lista abas pelo tipo real; `read_headers` lê só os cabeçalhos;
  `filter_sheets` aplica a seleção e `default_selection` marca todas no lote e a
  primeira de cada no merge.
- Merge concatena as abas selecionadas na ordem, com `ORIGEM`
  (`arquivo - aba - linha`) e alinhamento por dropdown; exige duas abas úteis.
- Seletor de chips com “Todas”/“Limpar”, contador e spinner; tipografia mínima
  de 12 px; colunas rolam sem barra, log de 160 px e prévia de 240 px.

## Próximo passo

S2a: fixtures fictícias para `.xlsx`, `.xls`, `.csv` e `.html`, testes de
`prepare_workbook`/`read_headers` e de reparo (CSV cp1252 e arquivo inválido),
mais um teste integrado por ferramenta.

## Arquivos-chave

- `core/tools/merge.py`, `controllers/merge.py`, `ui/pages/merge.py`.
- `core/io.py` (`read_headers`), `core/tools/sheets.py` e `tool_layout.py`
  (painéis de opções com `refresh()`).

## Armadilhas

- Flet 1.0 não suporta drop de arquivos do SO nem drag de colunas; o dropzone é
  clicável e o alinhamento é por dropdown.
- Flet 1.0 usa `Dropdown.on_select`, não `on_change`.
- `puremagic` lê HTML como `.txt`; `resolve_suffix` usa a extensão original.
- `merge` marca só a primeira aba de cada arquivo quando há vários; com um único
  arquivo, marca todas (ADR 0005/0006).
- Uma coluna de origem chamada `ORIGEM` vira `ORIGEM_original` na saída.
- `read_headers` roda ao trocar a seleção; é só cabeçalho, mas HTML é inteiro.
- `cut` usa o nome da aba no arquivo só com mais de uma aba processada.

## Como rodar

```bash
uv run xl-utils
uv run ruff check src tests
uv run pytest
node scripts/check-docs.mjs
```
