# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S9a3 — site público e política de privacidade
- **Próxima:** S9b — Drive II (link, seletor e escrita)
- **Ciclo:** 0006 — Backlog
- **Decisões:** comparação bruta; CNJ máscara ou 20 dígitos; `MIGRAÇÃO` é
  sentinela; config empacotada; ADRs 0014–0018; plugins em `.7z` privado; `id`,
  `link` e “vinculação” continuam. Drive: PKCE/`state`, `drive.file`, DPAPI.

## Pronto

- S9a3: site no GitHub Pages (`docs/index.html` e `privacy.html`) para a
  publicação no Google; docs internos ficam fora pelo `_config.yml`.
- S9a2: hamburger no canto superior direito; menu de perfis com ícone, conta
  ativa e sair; cartão do hub removido; 1º login pede o JSON uma vez.

## Próximo passo

Ler `docs/sessions/S9b-drive-planilha.md`. O navegador já tem teste offline; o
consentimento real fica com `scripts/check-drive-login.py`. A primeira decisão
da S9b é como chegar ao arquivo: `drive.file` não lê planilha antiga por link;
escolher Google Picker ou escopo `drive` em Testing antes de qualquer código.

## Arquivos-chave

- `shared/drive_auth.py`, `shared/accounts.py`, `ui/drive.py`
- `ui/components/top_menu.py`, `client_import.py`, `app.py`, `pages/home.py`
- `tests/test_drive_flow.py`, `scripts/check-drive-login.py`
- `configs/drive_client.json`, `configs/headers.json`, `shared/configs.py`
- `core/tools/link.py`, `ui/components/tool_layout.py`, `ui/theme.py`
- `docs/adr/0018-drive-autenticacao.md`, `docs/sessions/S9b-drive-planilha.md`
- `docs/index.html`, `docs/privacy.html`, `docs/_config.yml`

## Armadilhas

- `drive.file` só vê arquivo criado pelo app ou escolhido no Picker.
- Sem cliente, o 1º **Entrar com Google** pede o JSON uma vez; depois não pede.
- O JSON importado é validado; `token_uri` fora do Google é recusado.
- Login não é ferramenta: não recriar cartão do Drive no hub.
- DPAPI é Windows-only; fora dele o store recusa gravar.
- Token e client secret nunca em log, diagnóstico ou `repr`.
- `drive_client.json` empacotado nasce vazio; teste impede credencial real.
- Sair apaga só a conta ativa; trocar exige ferramenta ociosa.
- Comparação bruta: CNJ mascarado × 20 dígitos crus não vincula.
- CNJ numérico no Excel perde precisão; a coluna deve ser texto.
- `PROCESSO ORIGINÁRIO` contém “PROCESSO”; o match é exato, nunca substring.
- `MIGRAÇÃO` na AGENDA dispara o pop-up; confirmar não reescreve.
- AGENDA sem PROCESSOS bloqueia tudo; só CLIENTES não valida CNJ.
- Flet não é thread-safe: login e execução rodam fora da UI thread.
- Plugins: `.7z` precisa recusar path traversal, symlink e zip bomb.
- Nunca `push --force` na `main`; `legacy` é somente leitura.
- Pages: ligar em `main` / `docs`; a URL precisa responder antes do Google.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check src tests` · `uv run pytest` · `node scripts/check-docs.mjs`
