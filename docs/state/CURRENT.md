# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S2c — opções reais ou nada
- **Próxima:** S2d — tipo real x extensão (`docs/sessions/S2d-tipo-real.md`)
- **Ciclo:** 0002 — Fase 2 — Consolidação
- **Retorno:** `tool_layout.py`, `registry.py`, `pages/` e `test_layout.py`
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
- `RunLog` grava `(nível, texto)`, itera como linhas e alimenta o `ToolState.log`.
- `ToolLayout._run` separa leitura, seleção e falha inesperada; guarda traceback
  em `error_detail` e mostra a mensagem original.
- “Copiar diagnóstico” traz versões (fallback “desconhecida”), arquivos, abas,
  opções, causa e traceback.
- Texto e CNJ usam `note`; o card “2. Opções” só aparece para recorte e merge.

## Próximo passo

S2d: conferir o tipo detectado por conteúdo contra a extensão, mostrar o tipo
real na entrada e bloquear quando a detecção falhar.

## Arquivos-chave

- `ui/components/tool_layout.py` (`note`, card condicional) e `ui/pages/registry.py`.
- `shared/log.py` (`RunLog`, `build_diagnostics`) e `ui/components/result_panel.py`.
- `tests/test_layout.py`, `test_log.py` e `test_integration.py`.

## Armadilhas

- Flet 1.0 não suporta drop de arquivos do SO; o merge usa
  `Draggable`/`DragTarget` para o quadro de colunas.
- Uma aba contribui com no máximo uma coluna por saída; cabeçalhos repetidos
  ganham sufixo `_2`.
- `puremagic` lê HTML como `.txt`; `resolve_suffix` usa a extensão original.
- `.xls` é lido com o engine `calamine` (`python-calamine`); `xlrd` saiu.
- HTML sem `<meta charset>` pode perder acentos; as fixtures declaram UTF-8.
- `read_html` não aceita `dtype`; a segunda passada com converters é necessária.
- `merge` marca só a primeira aba por arquivo quando há vários.
- Log não pode carregar valores de célula; só passos, contagens e caminhos.
- O card “2. Opções” depende de `options` declaradas, não do conteúdo do painel.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run pytest` ·
`node scripts/check-docs.mjs`
