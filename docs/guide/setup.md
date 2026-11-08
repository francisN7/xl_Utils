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

## Comando global (opcional)

Para chamar `xl-utils` de qualquer pasta, instale o entry point como ferramenta
do uv:

```bash
uv tool install --editable .
xl-utils
```

`--editable` faz o comando apontar para este checkout: mudanças no código valem
sem reinstalar. O diretório de ferramentas do uv (`~/.local/bin` no Windows)
precisa estar no PATH; `uv tool update-shell` atualiza o perfil do shell. Para
remover: `uv tool uninstall xl-utils`. Em Windows, o entry point é um
`gui-script`: abre a janela sem console.

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

Não há Dependabot de PR automático: as vulnerabilidades aparecem como alerta na
aba **Security** e a atualização é manual. Rode `uv lock --upgrade`, revise o
diff e valide com lint, testes e check de docs antes de commitar.

## Google Drive (opcional)

Todo app com “Entrar com Google” tem um cliente OAuth registrado no Google
Cloud — é ele que o Google usa para identificar o app. O xl_Utils não traz um
cliente embutido (o repositório é público), então o **primeiro** login pede o
arquivo uma única vez:

1. No Google Cloud Console, crie um projeto e ative a **Google Drive API**.
2. Em **Credenciais**, crie um cliente **App para computador** e baixe o JSON.
3. No app, clique no menu hamburger do canto superior direito → **Entrar com
   Google** e selecione o JSON baixado.

Depois disso o fluxo é sempre o mesmo: menu → **Entrar com Google** → navegador
→ pronto. Não há cartão nem item de configuração na tela; o pedido do arquivo
só aparece se ainda não houver cliente.

O app valida o arquivo (tamanho, UTF-8, HTTPS, domínio do Google), guarda só os
campos que usa em `%LOCALAPPDATA%/xl_utils/drive_client.json` e nunca copia o
JSON original. As contas ficam em `%LOCALAPPDATA%/xl_utils/drive/`, com o
`refresh_token` protegido por DPAPI. O repositório é público: nunca faça commit
do JSON do cliente — o `.gitignore` cobre os nomes usuais, mas o caminho certo é
o `%LOCALAPPDATA%`.

### Testar o login

O fluxo inteiro roda offline nos testes automatizados, com um Google falso em
`127.0.0.1` que confere PKCE e `state`:

```bash
uv run pytest tests/test_drive_flow.py -q
```

Para exercitar o consentimento real do Google uma vez, com o navegador:

```bash
uv run python scripts/check-drive-login.py
```

O script imprime só e-mail, nome, escopos e a presença do refresh token; não
grava conta nem mostra token. Depois disso, use o app para entrar de verdade.

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
- **Check de docs quebrado:** o alvo do link provavelmente foi movido; corrija o
  caminho relativo ou remova o link morto.
- **Login do Drive falha:** rode `uv run python scripts/check-drive-login.py`
  para ver a mensagem sem a UI. Se o cliente não estiver configurado, o menu
  **Entrar com Google** pede o JSON baixado do Google Cloud uma única vez; ele
  precisa ser do tipo “App para computador”.
