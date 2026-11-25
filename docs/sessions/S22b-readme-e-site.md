# S22b — README e site com banner, badges e screenshots

## Objetivo

Quem abre o repositório ou o site vê, sem ler nada, o que o app faz e como ele
é nos dois temas.

## Fora de escopo

- Texto dos guias e auditoria (feitos na S22a).
- Mudança de código ou de comportamento do app.
- Release, build e notas da 0.4.0 (S23).

## Tarefas

1. Banner com tagline animada em SVG local (`assets/`, animação CSS), sem
   serviço externo de imagem.
2. Badges shields.io no topo do README: CI, Pages, última release,
   Python 3.15 e “todos os direitos reservados”.
3. Screenshots do Início e de Extrair CNJs com prévia, em Dracula e Alucard,
   por spike em `artifacts/spike_s22b/` (fora do Git) com `ft.Screenshot`
   (Flet 1.1.2): `LOCALAPPDATA` numa pasta temporária, sem conta logada,
   dados de `scripts/make_fixture.py`. Plano B: o dono captura no desktop.
4. README com `<picture>` por tema (`prefers-color-scheme`).
5. Site `docs/index.html` com banner e capturas.

## Aceite

- [ ] README com banner, badges e screenshots dos dois temas.
- [ ] Nenhuma imagem com e-mail, nome ou planilha real.
- [ ] Site com banner e capturas; publica só se o HTML mudar (ADR 0019).
- [ ] `ruff`, `pytest` e `uv run python scripts/check_docs.py` verdes.

## Orçamento de contexto (≤90 linhas)

`README.md` (topo), `docs/index.html`, `.github/workflows/pages.yml`; do app,
só o que o spike precisa (`app.main`, `ui/theme.py`, `shared/settings.py`).

## Arquivos prováveis

- `README.md`, `docs/index.html`
- `assets/banner.svg`, `assets/screenshots/` (ou dentro de `docs/`, se o
  Pages só publicar essa pasta)
- `artifacts/spike_s22b/shots.py` (não commitado)

## Riscos

- O tema gravado pelo app é a preferência real do dono: o spike precisa de
  `LOCALAPPDATA` temporário, senão troca o tema dele.
- `ft.Screenshot` captura o controle, não a janela: conferir se cabeçalho e
  sidebar entram na imagem.
- `pages.yml` só dispara com `docs/*.html`: imagem do site precisa estar no
  que o workflow publica.
- PNG grande pesa no clone: reduzir antes de commitar.

## Próximo depois desta

S23 — Release 0.4.0 e fechamento do ciclo 0009.
