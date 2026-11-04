# S2c — Opções reais ou nada

## Objetivo

Texto e CNJ deixam de mostrar checkboxes desabilitados: o comportamento fixo
vira uma frase na entrada, e o card “2. Opções” só existe quando há algo
editável (linhas do recorte, colunas do merge).

## Fora de escopo

Criar novas opções funcionais; redesenhar o quadro do merge; testar widgets do
Flet; mudar o pipeline de leitura.

## Tarefas

1. Remover `_check` e a fábrica `options` de `ui/pages/all_str.py` e
   `ui/pages/cnj.py`.
2. Passar uma frase fixa por `note` ao `ToolLayout`: texto remove emojis e
   preserva quebras; CNJ padroniza e remove duplicados.
3. `ToolLayout` ganha `note: str = ""`, exibida no card “1. Entrada” abaixo das
   abas; não cria o card “2. Opções” quando `options is None` e descarta
   `_empty_options`.
4. Manter o card em recorte (`rows_per_file`) e merge (quadro de colunas),
   sem tocar nos controles.
5. Teste leve em `tests/test_layout.py`: `ToolLayout` sem opções não contém o
   título “2. Opções”; com opções contém; `note` aparece uma vez.
6. Atualizar `reference/ui.md` (Entrada, Componentes e Estados), `CURRENT.md`,
   roadmap e `CHANGELOG.md`.

## Aceite

- [x] Texto e CNJ sem checkboxes desabilitados
- [x] card “2. Opções” ausente nas duas ferramentas e presente em recorte/merge
- [x] frase de comportamento visível na entrada
- [x] `ruff`, `pytest` e `docs:check` verdes

## Orçamento de contexto (≤90 linhas)

Ler `AGENTS.md`, `docs/state/CURRENT.md`, esta spec,
`ui/components/tool_layout.py` inteiro, as quatro páginas só pela montagem de
opções e `reference/ui.md` (Componentes, Resultado e Estados). Não abrir
controllers, core ou testes antigos.

## Arquivos prováveis

- `src/xl_utils/ui/components/tool_layout.py`
- `src/xl_utils/ui/pages/{all_str,cnj,cut,merge}.py`
- `tests/test_layout.py`
- `docs/reference/ui.md`

## Riscos

- O card escondido não pode deixar buraco na coluna esquerda nem perder o
  `_options_refresh` do recorte/merge.
- `note` não deve virar segunda descrição repetida no cabeçalho da página.
- O teste de layout não pode depender de uma página Flet montada; só construir
  o controle e procurar títulos.

## Próximo depois desta

S2d — tipo real x extensão: indicador na entrada, gate quando a detecção falhar
e testes com extensões trocadas.
