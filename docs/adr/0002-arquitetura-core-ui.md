# ADR 0002 — Arquitetura core/controllers/ui

- **Status:** aceita
- **Data:** 2026-11-04

## Contexto

Os scripts originais repetiam leitura de Excel, limpeza de terminal, seleção de
arquivo e salvamento. A lógica de negócio ficava misturada com `print` e
diálogo, o que impedia testar sem abrir uma janela.

## Decisão

Adotar um **MVC híbrido** em `src/xl_utils/`:

- `core/`: funções puras, tipadas, sem Flet, sem diálogo e sem `print`.
- `core/tools/`: um módulo por ferramenta.
- `controllers/`: orquestração, threading, progresso e tradução de erro.
- `ui/`: páginas Flet e componentes reutilizáveis.
- `shared/`: logging, configuração e clipboard.

O core recebe caminhos e devolve DataFrames/resultados; a página só coleta
entrada e apresenta saída.

## Consequências

- Regras testáveis com `pytest` e `tmp_path`, sem GUI.
- Duplicação de leitura/escrita concentrada em `core/io.py`, `core/mime.py`,
  `core/paths.py` e `core/text.py`.
- A UI pode mudar sem reescrever regra de negócio.
- Exige disciplina: nada de `print` no core e nada de pandas na página.

## Alternativas

- **Feature-first** (`features/<ferramenta>/`): boa para times grandes, mas
  pulveriza os helpers compartilhados neste projeto pequeno.
- **Camadas clássicas** (`models/`, `services/`, `views/`): mais cerimônia e
  menos direta que core/controllers/ui.
- **Manter scripts monolíticos:** impossibilita teste e perpetua a duplicação.
