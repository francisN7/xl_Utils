# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
Uma entrada por **versão**; o detalhe por sessão está no roadmap numerado e as
decisões nos ADRs.

## [Unreleased]

### Added

- Fundação do aplicativo desktop em Flet, com estrutura MVC híbrida em
  `src/xl_utils/`, ambiente uv no Python 3.15 e navegação entre as quatro
  ferramentas.
- UI base no tema Dracula: sidebar de 240 px com Início, quatro cartões
  alinhados à esquerda, entrada de arquivo clicável, barra de ação e painel de
  resultado com log e prévia de até 100 linhas.
- Cache de estado por ferramenta: navegar preserva a seleção; trocar o arquivo
  reseta opções e resultado.
- Helpers compartilhados de leitura/escrita de planilhas, detecção real de
  formato com `puremagic`, nomes de saída únicos e remoção de emojis.
- Leitura segura por padrão: `dtype=str`, preservação de zeros/CNJ/CPF e
  quebras de linha intactas.
- Tratamento de Texto funcional: `prepare_workbook` remove emojis de todas as
  abas, repara leitura com um fallback por formato e grava em `output/`.
- Erro tipado `WorkbookReadError` quando a planilha não pode ser lida nem
  reparada, substituindo o antigo `xlsx2csv` via `shell=True`.
- Teste funcional de 1.000 linhas fictícias geradas em memória, em CSV e XLSX,
  sem versionar dados de teste; amostra local opcional em `samples/`.
- Extração de CNJs funcional: aceita formato pontuado ou 20 dígitos,
  padroniza, remove duplicatas e grava `PROCESSOS` em `output/`.
- Recorte de planilhas funcional: divide cada aba em blocos de N linhas, com
  campo editável na página, nomes `_Recorte_NNN` e saída em `output/`.
- Estrutura de contexto entre sessões (`AGENTS.md`, `CURRENT.md`, mapa em
  `docs/README.md`, roadmap `main` + histórico, specs, ADRs e check de docs).

### Removed

- `all_str.py`, `cnjs.py` e `cut.py` da raiz, substituídos por core +
  controller + página.
- Branch `cli-app` e a tentativa de interface por linha de comando.
- Ferramentas `convert`, `quick_replace` e `remove_emoji` (emojis passam para o
  pipeline do `all_str`).
- Dependências `demoji`, `file-picker-py`, `xlsx2csv` e `click`.

## v0.1.0 — 2026-11-04

### Added

- Primeira versão em desenvolvimento: shell do app e utilitários em migração.
