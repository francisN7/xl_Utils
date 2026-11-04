# Setup e execução

**O que responde:** como preparar o ambiente, rodar o app e adicionar
dependências. **O que não responde:** por que Flet/uv (ver ADR 0001) nem como o
código é organizado (ver `reference/architecture.md`).

## Pré-requisitos

- [uv](https://docs.astral.sh/uv/) instalado.
- Node.js apenas para `node scripts/check-docs.mjs`.
- Nenhum Python global necessário: o uv baixa o 3.15 definido em
  `.python-version`.

## Rodando

```bash
uv sync
uv run xl-utils
```

Sem o entry point:

```bash
uv run python -m xl_utils
```

## Dependências

O `pyproject.toml` é gerenciado pelo uv. Não edite `[project.dependencies]` nem
`[dependency-groups]` à mão:

```bash
uv add pandas          # runtime
uv add --dev pytest    # desenvolvimento
uv remove <pacote>
uv lock --upgrade      # atualiza o lock
uv sync                # aplica o lock ao .venv
```

Campos manuais permitidos: `description`, `readme`, `authors`,
`[project.gui-scripts]`, `[build-system]`, `[tool.ruff]` e
`[tool.pytest.ini_options]`.

## Verificações

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest
node scripts/check-docs.mjs
```

## Problemas comuns

- **A janela não abre:** confirme `flet[desktop]` no `pyproject.toml`. Só
  `flet` instala o runtime web, não o cliente desktop.
- **Python errado:** rode `uv python pin 3.15` e `uv sync` para recriar o
  `.venv`.
- **Lock dessincronizado:** `uv sync --locked`; se falhar, `uv lock` e revise o
  diff.
- **`docs:check` quebrado:** o alvo do link provavelmente foi movido; corrija o
  caminho relativo ou remova o link morto.
