# Testes

**O que responde:** como rodar e escrever testes. **O que não responde:** a
arquitetura (ver `reference/architecture.md`) nem o setup (ver `guide/setup.md`).

## Comandos

```bash
uv run pytest
uv run pytest tests/test_core.py -q
uv run pytest --cov=xl_utils --cov-report=term-missing
uv run ruff check src tests
```

## O que testar

- `core/` é o alvo principal: funções puras, sem Flet e sem diálogo.
- Use `tmp_path` para arquivos temporários e dados fictícios.
- Cubra o caminho feliz e uma borda por função: arquivo vazio, extensão errada,
  planilha sem abas, nome de aba inválido.
- A UI é validada por smoke manual: abrir o app e executar a ferramenta com um
  arquivo real. Testes de widget ficam para quando houver regressão recorrente.

## Exemplo

```python
from pathlib import Path

import pandas as pd

from xl_utils.core.io import read_workbook, save_workbook


def test_roundtrip(tmp_path: Path) -> None:
    source = tmp_path / "entrada.xlsx"
    pd.DataFrame({"nome": ["Ana"]}).to_excel(source, index=False)

    sheets = read_workbook(source, dtype=str)
    saved = save_workbook(sheets, tmp_path / "saida.xlsx")

    assert read_workbook(saved, dtype=str)["Sheet1"]["nome"].tolist() == ["Ana"]
```

## Base fictícia

`tests/test_all_str_bulk.py` gera 1.000 linhas inventadas em memória, com zeros
à esquerda, texto no formato CNJ (ano 0000, inválido de propósito), emojis e
quebras de linha. Nenhum dado de teste é versionado. O teste roda o pipeline
completo em CSV e XLSX e confere que nada disso se perde.

`tests/conftest.py` monta as mesmas linhas fictícias em `.xlsx`, `.csv` e
`.html` dentro de `tmp_path` e copia `tests/fixtures/minimo.xls`. O `.xls` é o
único binário versionado; foi gerado uma vez com `uv run --with xlwt` e contém
três linhas inventadas. `tests/test_formats.py` cobre leitura, abas, cabeçalhos
e reparo; `tests/test_integration.py` roda as quatro ferramentas nos quatro
formatos. Para criar uma amostra local em `samples/` (fora do Git):

```bash
uv run python scripts/make_fixture.py
```

## Convenções

- Um arquivo de teste por módulo de core: `tests/test_all_str.py`, etc.
- Nome do teste descreve o comportamento, não o método.
- Não use dados reais, CPF, CNPJ ou nomes de clientes.
- Fixtures compartilhadas só quando houver repetição real.
