# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S2d — tipo real x extensão
- **Próxima:** S2e — saída escolhida (`docs/sessions/S2e-saida-escolhida.md`)
- **Ciclo:** 0002 — Fase 2 — Consolidação
- **Retorno:** `result_panel.py`, `tool_layout.py`, controllers e `test_save.py`
- **Decisões abertas:** nenhuma

## Pronto

- Ambiente uv/Python 3.15, Flet desktop e pandas 3.1; MVC híbrido e tema Dracula.
- `prepare_workbook` lê como texto, remove emojis, repara e falha como
  `WorkbookReadError`.
- Texto, CNJ, recorte e merge salvam em `output/`; os três primeiros aceitam
  lote e processam cada origem separadamente.
- Seleção de abas por chips e `default_selection` por ferramenta; merge com
  `ORIGEM` e quadro de colunas arrastáveis (chips).
- Integração cobre os quatro formatos; `.xls` usa `tests/fixtures/minimo.xls`;
  HTML preserva zeros e o reparo cp1252 é testado.
- `RunLog` grava eventos e o diagnóstico traz arquivos, formato, abas, opções,
  causa e traceback; `ToolLayout._run` separa leitura, seleção e falha.
- `FormatCheck`/`check_format` mostram o tipo real, avisam a divergência e
  bloqueiam a execução quando nada é identificável.
- Texto e CNJ usam `note`; o card “2. Opções” só aparece para recorte e merge.

## Próximo passo

S2e: executar sem gravar, mostrar a prévia e salvar só ao clicar, com arquivo
único, pasta para o lote e atalho para `output/`.

## Arquivos-chave

- `ui/components/tool_layout.py` (`_check_formats`, `_block_formats`) e
  `ui/pages/registry.py`.
- `core/mime.py` (`FormatCheck`), `shared/log.py` e `result_panel.py`.
- `tests/test_format_check.py`, `test_layout.py`, `test_log.py` e
  `test_integration.py`.

## Armadilhas

- Flet 1.0 não suporta drop do SO; o merge usa `Draggable`/`DragTarget`.
- Uma aba contribui com no máximo uma coluna por saída; cabeçalhos repetidos
  ganham sufixo `_2`.
- `puremagic` pode devolver `.txt`; a extensão suportada vence e não conta como
  divergência. O gate só bloqueia quando não há formato suportado nenhum.
- `.xls` é lido com o engine `calamine` (`python-calamine`); `xlrd` saiu.
- HTML sem `<meta charset>` pode perder acentos; as fixtures declaram UTF-8.
- `read_html` não aceita `dtype`; a segunda passada com converters é necessária.
- Log e diagnóstico não carregam valores de célula; só passos, contagens,
  caminhos e formato.
- O card “2. Opções” depende de `options` declaradas, não do conteúdo do painel.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run pytest` ·
`node scripts/check-docs.mjs`
