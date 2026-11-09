# Estado atual

> Handoff entre sessões. Atualizar no fim de toda sessão. Manter ≤60 linhas.

## Sessão

- **Última concluída:** S11 — versão 0.2.0 e polimento de UI
- **Próxima:** S12 — empacotar a primeira versão, 0.3.0
- **Ciclo:** 0007 — Versão e distribuição
- **Decisões:** comparação bruta; CNJ máscara ou 20 dígitos; `MIGRAÇÃO` é
  sentinela; config empacotada; ADRs 0014–0019; plugins em `.7z` privado.
  Drive: PKCE/`state`, `drive.file`, DPAPI, Picker desktop sem API key, pasta
  concedida por conta, raiz como fallback e nomes livres `_001`. Histórico em
  texto, uma página por ciclo (ADR 0020). E-mail longo usa `ft.Tooltip` com 3 s.

## Pronto

- S11: app marcado como `0.2.0` no pyproject, lock, `__version__` e diagnóstico;
  cartões do Início com nome em uma linha, descrição em duas com `…`/tooltip e
  recorte do conteúdo; e-mail truncado no menu de perfis e no seletor de conta,
  com valor completo em tooltip de 3 s. Testes headless em `tests/test_home.py`.
- S10: ciclo 0006 arquivado em `docs/history/0006-backlog.md`; ciclo 0007 aberto.
- S9c: “Salvar no Drive” na pasta de origem, concessão por conta e `_001`.

## Próximo passo

Ler `docs/sessions/S12-empacotar-0.3.0.md`: medir PyInstaller/Nuitka/MSIX e
registrar o ADR, montar o build a partir do wheel, gerar o instalador Windows com
Python embutido, marcar 0.3.0, validar sem Python e publicar a release `v0.3.0`.

## Arquivos-chave

- `docs/sessions/S12-empacotar-0.3.0.md`, `docs/roadmap/main.md`
- `pyproject.toml`, `src/xl_utils/__init__.py`, `uv.lock`, `src/xl_utils/app.py`
- `src/xl_utils/ui/pages/home.py`, `ui/components/account_label.py`, `top_menu.py`
- `scripts/`, `.github/workflows/`, assets/ícone

## Armadilhas

- Flet 1.1.2 no empacotador: validar um build mínimo que abra a janela antes de
  escrever o instalador; se falhar, trocar de ferramenta cedo.
- A versão vive em `pyproject.toml`, `uv.lock`, `__version__` e diagnóstico:
  conferir as quatro e rodar `uv lock` depois de editar.
- Flet não é thread-safe: login, Picker, gravação e execução fora da UI thread.
- Tooltip do Flet aceita `ft.Tooltip(wait_duration=…)`; não é preciso `Timer`.
- Páginas: push de código não publica; use Actions → Pages → Run workflow.
- Nunca `push --force` na `main`; `legacy` é somente leitura.
- `drive.file` só vê arquivo criado/escolhido; a pasta precisa ser concedida.
- Nunca sobrescrever: `free_name` escolhe `_001`.

## Como rodar

`uv run xl-utils` · `uv run ruff check src tests` · `uv run ruff format --check src tests` · `uv run pytest` · `node scripts/check-docs.mjs`
