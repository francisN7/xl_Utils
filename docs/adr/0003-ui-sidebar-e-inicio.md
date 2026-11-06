# ADR 0003 — Sidebar com Início e anatomia de ferramenta

- **Status:** aceita
- **Data:** 2026-11-04

## Contexto

Com quatro ferramentas e uso recorrente, era preciso escolher entre velocidade
(sidebar), descoberta (hub), múltiplas tarefas (abas) e segurança (wizard). O
dono também pediu tema **Dracula dark**.

## Decisão

- **Sidebar fixa + item “Início”** com hub de cartões.
- **Estado por ferramenta preservado** ao navegar; **reset ao trocar o
  arquivo**.
- **Prévia da planilha sempre visível** no painel de resultado.
- **Dropzone clicável + seletor nativo** na entrada. O Flet 1.0 não expõe
  drop de arquivos do sistema operacional; o visual de dropzone abre o seletor
  ao clique.
- **Tema Dracula dark único**, sem tema claro no escopo inicial.
- Anatomia comum: cabeçalho, entrada/opções, resultado e barra de ação.

## Consequências

- Troca de ferramenta em um clique e descoberta no “Início”.
- O usuário vê o efeito da operação sem abrir o Excel.
- A prévia precisa ser paginada/limitada para não travar com arquivos grandes.
- O reset ao trocar de arquivo evita resultado velho associado a outro arquivo.
- Sem tema claro, o contraste precisa ser validado só sobre o Dracula.

## Alternativas

- **Hub puro:** mais simples, porém um clique extra em todo uso.
- **Abas:** úteis para execuções simultâneas, mas complexidade desproporcional.
- **Wizard:** bom para casos complexos, ruim para repetição.
- **Só log/caminho:** menos útil para conferir o resultado.
- **Drag & drop real:** exigiria PySide6/Qt ou um hook Windows-only; fica para
  uma melhoria separada.
- **Tema claro também:** fica para o backlog.

> **Adendo (2026-11-06):** o tema claro deixou o backlog e foi entregue como
> opção salva, aplicada ao reabrir; ver [ADR 0013](0013-tema-claro-e-preferencia.md).
