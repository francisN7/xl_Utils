# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S9a — Drive I (ADR, OAuth, contas e shell)
- **Próxima:** S9b — Drive II (link, seletor e escrita)
- **Ciclo:** 0006 — Backlog
- **Decisões:** comparação bruta; CNJ máscara ou 20 dígitos; `MIGRAÇÃO` é
  sentinela; config empacotada; ADRs 0014–0018; plugins em `.7z` com repositório
  privado (ADR pendente). O `id`, os módulos `link` e “vinculação” continuam.
  Drive: `google-auth-oauthlib` 1.5 com PKCE e `state` automáticos, `drive.file`,
  contas por e-mail com DPAPI, destino da saída adiado para a S9c.

## Pronto

- S9a: ADR 0018; login pelo navegador com loopback efêmero e timeout, menu
  hamburger na sidebar, cartão do Drive no hub (entrar, trocar, sair), store
  com DPAPI e escrita atômica, testes offline. Ver a spec e o ADR 0018.
- S8: tela cheia do merge; S7d/S7c/S7a/S7b: vinculação completa.
- Auditoria pública e backlog de plugins registrados no roadmap.

## Próximo passo

Ler `docs/sessions/S9b-drive-planilha.md`. Antes, exercitar o login real com o
`drive_client.json` do dono (a S9a só foi testada com transporte falso). A
primeira decisão da S9b é como chegar ao arquivo: `drive.file` não lê planilha
antiga por link; escolher Google Picker ou escopo `drive` em Testing antes de
qualquer código.

## Arquivos-chave

- `shared/drive_auth.py`, `shared/accounts.py`, `ui/drive.py`
- `ui/components/top_menu.py`, `ui/components/drive_status.py`, `app.py`
- `configs/drive_client.json`, `configs/headers.json`, `shared/configs.py`
- `core/tools/link.py`, `ui/components/tool_layout.py`, `ui/theme.py`
- `docs/adr/0018-drive-autenticacao.md`, `docs/sessions/S9b-drive-planilha.md`

## Armadilhas

- `drive.file` só vê arquivo criado pelo app ou escolhido no Picker.
- DPAPI é Windows-only; fora dele o store recusa gravar.
- Token e client secret nunca em log, diagnóstico ou `repr`.
- `drive_client.json` empacotado nasce vazio: sem client_id o app explica.
- Timeout do login é 180 s; negar no navegador vira erro tratado.
- Sair apaga só a conta ativa; trocar exige ferramenta ociosa.
- A tela cheia cobre só o conteúdo; a sidebar continua clicável.
- Comparação bruta: CNJ mascarado × 20 dígitos crus não vincula.
- CNJ numérico no Excel perde precisão; a coluna deve ser texto.
- `PROCESSO ORIGINÁRIO` contém “PROCESSO”; o match é exato, nunca substring.
- `MIGRAÇÃO` na AGENDA dispara o pop-up; confirmar não reescreve.
- AGENDA sem PROCESSOS bloqueia tudo; só CLIENTES não valida CNJ.
- Flet não é thread-safe: login e execução rodam fora da UI thread.
- Plugins: `.7z` precisa recusar path traversal, symlink e zip bomb.
- Nunca `push --force` na `main`; `legacy` é somente leitura.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check src tests` · `uv run pytest` · `node scripts/check-docs.mjs`
