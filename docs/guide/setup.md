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

1. No Google Cloud Console, crie um projeto e ative a **Google Drive API** e a
   **Google Picker API** — o seletor de arquivos do Drive usa as duas.
2. Em **Credenciais**, crie um cliente **App para computador** e baixe o JSON.
   No consentimento, os escopos são `openid`,
   `https://www.googleapis.com/auth/userinfo.email` e
   `https://www.googleapis.com/auth/drive.file`.
3. No app, clique no menu hamburger do canto superior direito → **Entrar com
   Google** e selecione o JSON baixado.

Depois disso o fluxo é sempre o mesmo: menu → **Entrar com Google** → navegador
→ pronto. Não há cartão nem item de configuração na tela; o pedido do arquivo
só aparece se ainda não houver cliente.

Ao abrir uma planilha do Drive, o app usa o **Picker de apps desktop**: uma
segunda autorização, só com `drive.file` e sem acesso offline, abre o seletor no
navegador e devolve o arquivo escolhido. Isso não muda o login nem as contas já
salvas; sem a Picker API ativa, o Google recusa o seletor. Cada escolha mostra o
consentimento de novo — exigência do Picker —, com a conta escolhida no app já
pré-selecionada (`login_hint`).

O app valida o arquivo (tamanho, UTF-8, HTTPS, domínio do Google), guarda só os
campos que usa em `%LOCALAPPDATA%/xl_utils/drive_client.json` e não move nem
altera o original. No Windows, o `client_secret` é gravado cifrado por DPAPI
(campo `client_secret_dpapi`); em texto ele só existe em memória durante o
login. As contas ficam em `%LOCALAPPDATA%/xl_utils/drive/`, com o
`refresh_token` também protegido por DPAPI. Depois de importar, apague o JSON
baixado. O repositório é público: nunca faça commit do JSON do cliente — o
`.gitignore` cobre os nomes usuais, mas o caminho certo é o `%LOCALAPPDATA%`.

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

Para testar o Picker com uma conta real, o script abaixo baixa a planilha
escolhida e imprime só nome, tipo e tamanho:

```bash
uv run python scripts/check-drive-picker.py
```

## Site público

`docs/index.html` e `docs/privacy.html` são publicados por
`.github/workflows/pages.yml`, que só roda quando um desses HTML muda — ou pelo
botão **Run workflow** em Actions → Pages. Em **Settings → Pages → Source**, a
origem precisa ser **GitHub Actions**; em “Deploy from a branch”, o GitHub
republica a cada push na `main` e o filtro de caminho não vale.

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
- **`xl-utils` digitado no terminal não faz nada:** o atalho global criado com
  `uv tool install --editable .` tem um ambiente próprio. Depois de mudar
  dependências, rode `uv tool install --editable . --force`; para o dia a dia,
  `uv run xl-utils` usa o `.venv` atualizado do projeto.
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
