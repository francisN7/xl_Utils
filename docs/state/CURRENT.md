# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** auditoria pública, endurecimento e backlog de plugins
- **Próxima:** S9a — Drive I (ADR, OAuth, contas e shell)
- **Ciclo:** 0006 — Backlog
- **Decisões:** comparação bruta; CNJ máscara ou 20 dígitos; `MIGRAÇÃO` é
  sentinela; config empacotada em `src/xl_utils/configs/headers.json`;
  ADRs 0014–0017; plugins em `.7z` com repositório privado e contrato público
  (ADR 0018 pendente). O `id`, os módulos `link` e “vinculação” continuam.

## Pronto

- Auditoria pública: sem segredos/PII; `.gitignore`, `SECURITY.md`, licença
  explícita, CI com `contents: read` e actions pinadas; secret scanning, push
  protection, PVR e Dependabot de alertas ligados; `main`, `legacy` e tag
  protegidas; histórico reescrito e repositório recriado sem refs antigas.
- S8: tela cheia do merge; grupos, seleção e ordem sobrevivem. Confirmado no
  app.
- S7d/S7c/S7a/S7b: vinculação completa; S6: tema ao vivo e `ORIGEM`.

## Próximo passo

Ler `docs/sessions/S9a-drive-autenticacao.md` e escrever o ADR 0018 antes de
qualquer código de Drive. O backlog de plugins está em `roadmap/main.md` e
também exige ADR antes do código.

## Arquivos-chave

- `ui/components/tool_layout.py`, `ui/pages/merge.py`, `ui/pages/link.py`
- `ui/state.py`, `ui/pages/registry.py`, `ui/theme.py`
- `core/tools/link.py`, `controllers/link.py`
- `shared/configs.py`, `src/xl_utils/configs/headers.json`
- `SECURITY.md`, `.github/workflows/ci.yml`
- `docs/roadmap/main.md`, `docs/sessions/S9a-drive-autenticacao.md`

## Armadilhas

- A tela cheia cobre só o conteúdo; a sidebar continua clicável.
- O painel é montado uma vez: não recriar grupos ao maximizar/restaurar.
- Comparação bruta: CNJ mascarado × 20 dígitos crus não vincula.
- CNJ numérico no Excel perde precisão antes da leitura; a coluna deve ser texto.
- `PROCESSO ORIGINÁRIO` contém “PROCESSO”; o match é exato, nunca substring.
- Cabeçalho dobra caixa/acento e remove espaços; valor de célula não é tocado.
- Nome de PROCESSOS com `;` é dividido cru: `"A; B"` produz `" B"`.
- `MIGRAÇÃO` na AGENDA dispara o pop-up; confirmar não reescreve o protocolo.
- AGENDA sem PROCESSOS bloqueia tudo, mesmo com FINANCEIRO e CLIENTES.
- Só CLIENTES: não valida CNJ e não cria nem altera `VINCULA?`.
- Config empacotada via `importlib.resources`; override em `%LOCALAPPDATA%`.
- Flet não é thread-safe: `pre_run` roda em thread e só devolve texto.
- Cancelar não interrompe pandas; `.xls` sem leitor alternativo falha no calamine.
- Plugins: `.7z` precisa recusar path traversal, symlink e zip bomb.
- Nunca `push --force` na `main`; `legacy` é somente leitura.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check src tests` · `uv run pytest` · `node scripts/check-docs.mjs`
