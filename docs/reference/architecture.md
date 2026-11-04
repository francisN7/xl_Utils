# Arquitetura

**O que responde:** camadas, fluxo de dados, leitura segura, detecção de
formato e convenções do core. **O que não responde:** a interface (ver
`ui.md`) nem o porquê das decisões (ver `../adr/`).

## Camadas

| Camada | Pasta | Regra |
|---|---|---|
| Core | `src/xl_utils/core/` | Regra pura, sem Flet, sem diálogo, sem `print`. |
| Controllers | `src/xl_utils/controllers/` | Orquestra core + threading + progresso. |
| UI | `src/xl_utils/ui/` | Coleta entrada e exibe resultado; não contém regra. |
| Shared | `src/xl_utils/shared/` | Logging, config e clipboard. |

Uma ferramenta = um módulo em `core/tools/` + um controller + uma página.

## Fluxo de dados

```text
arquivo escolhido
  → controller
  → all_str.prepare_workbook (leitura segura + emojis)
  → regra da ferramenta em core/tools/
  → save_workbook / resultado em memória
  → result panel (status, caminho, log e prévia)
```

## Leitura segura

Toda ferramenta começa pelo pipeline do `all_str`, sempre antes da regra
específica:

1. lê todas as abas com `dtype=str`;
2. remove emojis com `emoji.replace_emoji`;
3. preserva o texto da célula, inclusive quebras de linha;
4. só tenta reparo quando a leitura falha, sem `shell=True`.

O objetivo é não perder zeros à esquerda, CNJ/CPF e valores que o Excel
converteria em notação científica. A ferramenta “Tratamento de texto” também
expõe esse pipeline sozinha, para conversão e reparo explícitos.

## Detecção de formato

`core/mime.py` usa `puremagic` no conteúdo e nunca renomeia o arquivo do
usuário. Quando o detectado é genérico (`.txt`) e a extensão original é
suportada, a extensão original vence. Formatos: `.xlsx`, `.xlsm`, `.xls`,
`.csv`, `.html` e `.htm`.

## Saída

`core/paths.py` cria a pasta e devolve um nome livre (`saida_001.xlsx`).
`core/io.py` grava todas as abas em um `.xlsx` com nomes saneados (limite de 31
caracteres e caracteres inválidos do Excel). O arquivo de origem nunca é
alterado.

## Ferramentas

| Ferramenta | Módulo planejado | Estado |
|---|---|---|
| Tratamento de texto | `core/tools/all_str.py` | a migrar |
| Extrair CNJs | `core/tools/cnj.py` | a migrar |
| Recortar planilha | `core/tools/cut.py` | a migrar |
| Mesclar planilhas | `core/tools/merge.py` | a migrar |

## Testes

O core é testado com `pytest` e `tmp_path`; a UI é validada por smoke manual
enquanto não houver regressão que justifique teste de widget.

## Decisões

- [ADR 0001](../adr/0001-stack-ui-e-ambiente.md) — stack, uv e Flet.
- [ADR 0002](../adr/0002-arquitetura-core-ui.md) — camadas.
- [ADR 0004](../adr/0004-leitura-segura-e-emojis.md) — leitura segura e emojis.
