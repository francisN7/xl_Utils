# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S2e — saída escolhida
- **Próxima:** S3a — promover a UI a `main` (`docs/sessions/S3a-publicacao.md`)
- **Ciclo:** 0002 — Fase 2 — Consolidação
- **Retorno:** `core/save.py`, `result_panel.py`, `tool_layout.py`, `test_save.py`
- **Decisões abertas:** nenhuma

## Pronto

- Ambiente uv/Python 3.15, Flet desktop e pandas 3.1; MVC híbrido e tema Dracula.
- `prepare_workbook` lê como texto, remove emojis, repara e falha como
  `WorkbookReadError`.
- Texto, CNJ, recorte e merge devolvem `SaveItem` em memória; nada é gravado
  até a escolha do usuário.
- `core/save.py` grava arquivo único, lote em pasta ou atalho `output/`; nomes
  livres via `unique_path` e falha tipada `SaveError`.
- Painel “Pronto para salvar” com prévia, **Salvar**, **Salvar em output/** e
  cancelamento sem efeito; após gravar, caminho real e “Abrir pasta”.
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

S3a: confirmar que `main` é ancestral de `feat/ui`, criar `legacy` no commit
antigo e avançar `main` para a versão com UI.

## Arquivos-chave

- `core/save.py` (`SaveItem`, `save_chosen`, `save_to_output`, `SaveError`),
  `ui/components/result_panel.py`, `ui/components/tool_layout.py` e
  `tests/test_save.py`.

## Armadilhas

- Flet 1.0 não suporta drop do SO; o merge usa `Draggable`/`DragTarget`.
- `FilePicker` fica em `page.services`; salvar/cancelar é assíncrono e `None`.
- Uma aba contribui com no máximo uma coluna por saída; cabeçalhos repetidos
  ganham sufixo `_2`.
- `puremagic` pode dar `.txt`; a extensão suportada vence e o gate só bloqueia
  quando não há formato suportado nenhum.
- `.xls` é lido com o engine `calamine` (`python-calamine`); `xlrd` saiu.
- `read_html` não aceita `dtype`; a segunda passada com converters é necessária.
- O card “2. Opções” depende de `options` declaradas, não do conteúdo do painel.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run pytest` ·
`node scripts/check-docs.mjs`
