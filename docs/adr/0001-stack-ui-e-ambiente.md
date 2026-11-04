# ADR 0001 — Stack, ambiente e fim do CLI

- **Status:** aceita
- **Data:** 2026-11-04

## Contexto

O projeto nasceu como sete scripts Python independentes na raiz. A tentativa de
unificá-los em uma CLI com `click` (branch `cli-app`) foi rejeitada. A interface
precisa ser desktop, o ambiente precisa ser reproduzível e as bibliotecas devem
ficar nas versões mais recentes.

## Decisão

- **Python 3.15**, fixado em `.python-version` e gerenciado pelo **uv**.
- **Flet 1.x com `flet[desktop]`** para a interface.
- **Apagar a branch `cli-app`**, local e remota; nada dela é reaproveitado.
- **`puremagic`** para detectar formato real, sem depender de `libmagic`.
- **`emoji`** no lugar de `demoji`.
- Dependências declaradas e atualizadas **somente via uv** (`uv add`, `uv lock
  --upgrade`).

## Consequências

- Um único ambiente reproduzível; `uv sync` recria o `.venv`.
- O app abre como janela desktop e pode ser empacotado depois.
- `demoji` fica fora: a versão 2.0 declara `requires-python <3.15` e a API
  `download_codes()` foi removida desde a 1.0. `emoji.replace_emoji()` cobre o
  caso sem dependência nativa.
- `file-picker-py` e `xlsx2csv` também saem: o Flet tem seletor nativo e o
  reparo passa a ser feito com `openpyxl`/pandas.

## Alternativas

- **PySide6/Qt:** mais maduro, porém mais pesado e mais código para o mesmo
  formulário.
- **Textual:** interface no terminal, não atende ao pedido de app desktop.
- **NiceGUI:** exigiria navegador/servidor local.
- **Tkinter:** sem dependências, mas visual datado e fraco para tabelas.
- **Manter a CLI:** rejeitada pelo dono do projeto.
- **Python 3.14:** permitiria `demoji`, mas foi preterido em favor do 3.15.
