# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S10 — fechamento do ciclo 0006 e arquivo do histórico
- **Próxima:** S11 — versão 0.2.0 e polimento de UI
- **Ciclo:** 0007 — Versão e distribuição
- **Decisões:** comparação bruta; CNJ máscara ou 20 dígitos; `MIGRAÇÃO` é
  sentinela; config empacotada; ADRs 0014–0019; plugins em `.7z` privado.
  Drive: PKCE/`state`, `drive.file`, DPAPI, Picker desktop sem API key, pasta
  concedida por conta, raiz como fallback e nomes livres `_001`. Histórico em
  texto, uma página por ciclo, sem arquivo comprimido (ADR 0020).

## Pronto

- S10: ciclo 0006 arquivado em `docs/history/0006-backlog.md`; páginas 0001–0006
  em `docs/history/`; 14 specs fechadas fora do working tree; ciclo 0007 aberto.
- S9c: “Salvar no Drive” na pasta de origem, `drive/folders.json`, upload
  multipart, nomes `_001` e fallback para a raiz. Validado no app em 2026-11-08.
- S9a–S9b: OAuth por DPAPI, menu de perfis, Picker de desktop e leitura do Drive.

## Próximo passo

Ler `docs/sessions/S11-versao-0.2.0-e-polimento.md`: marcar 0.2.0 em
`pyproject.toml`, `uv.lock`, `__version__`, diagnóstico e docs; corrigir o
estouro dos cartões em largura estreita (Início e Verificar Vínculos) e truncar
o e-mail do menu de perfis com tooltip atrasado. Sem mudança de regra de
negócio.

## Arquivos-chave

- `src/xl_utils/ui/pages/home.py`, `registry.py`, `ui/components/top_menu.py`
- `pyproject.toml`, `src/xl_utils/__init__.py`, `uv.lock`
- `docs/history/README.md`, `docs/roadmap/main.md`, `docs/adr/0020-*.md`
- `scripts/check-docs.mjs` (ignora links de `docs/history/`)
- `docs/sessions/S11-versao-0.2.0-e-polimento.md`

## Armadilhas

- Ciclo fechado não volta ao working tree: o texto vive no Git e o resumo em
  `docs/history/`; não criar `.7z`/`.zip` de docs.
- Flet não é thread-safe: login, Picker, gravação e execução fora da UI thread.
- Tooltip do Flet pode não ter atraso nativo; medir antes de assumir `Timer`.
- `uv lock` pode subir dependências: conferir o diff e rodar a suíte.
- Páginas: push de código não publica; use Actions → Pages → Run workflow.
- Nunca `push --force` na `main`; `legacy` é somente leitura.
- `drive.file` só vê arquivo criado/escolhido; a pasta precisa ser concedida.
- Nunca sobrescrever: `free_name` escolhe `_001`.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check src tests` · `uv run pytest` · `node scripts/check-docs.mjs`
