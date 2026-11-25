# S23a — Versão Linux em AppImage

## Objetivo

Gerar na máquina do dono um `xl_Utils-<versão>-x86_64.AppImage` que abre o app,
lê e grava planilhas e faz login no Drive guardando o token no chaveiro.

## Fora de escopo

- Workflow de CI (S23b) e release 0.4.0 (S23c).
- `.deb`, Flatpak, `flet build linux` e assinatura do AppImage.
- Mudança de UI ou de comportamento do app.

## Tarefas

1. `scripts/build_linux.sh`, espelho do `build_windows.ps1`: venv limpo com o
   wheel + `pyinstaller` + `flet[cli]`; `flet pack` onedir com
   `scripts/pack_entry.py`, `--add-data` de `configs/` e `assets/`; nada de
   `.venv`, `output/` ou cache do Drive.
2. Conferir no bundle o que o Windows já exige (`_lzma`, módulos do
   `cryptography`) e os backends do `keyring` (Secret Service/`jeepney`,
   KWallet), com `--hidden-import` se faltar.
3. AppDir com `AppRun`, `xl_utils.desktop` e `assets/icon.png`; `appimagetool`
   baixado com versão e SHA-256 fixos, verificados antes de rodar.
4. Gerar `SHA256SUMS.txt` ao lado do AppImage, em `artifacts/` (fora do Git).
5. Guia `docs/guide/release-linux.md` (pré-requisitos, build, validação,
   publicação) e linha no mapa `docs/README.md`.
6. ADR 0032: AppImage como formato Linux, com as alternativas descartadas.

## Aceite

- [ ] AppImage abre no CachyOS (desktop KDE) com ícone e título certos.
- [ ] Abre numa distro limpa (contêiner/VM Ubuntu LTS ou Fedora) ou o guia
      lista as libs do sistema que faltam.
- [ ] Extrair CNJs com a fixture fictícia salva o resultado em `output/`.
- [ ] Login do Drive grava no chaveiro (dono, com conta real).
- [ ] Tema e contas em `~/.xl_utils/`, como no `uv run`.
- [ ] `ruff`, `pytest` e `uv run python scripts/check_docs.py` verdes.

## Orçamento de contexto (≤90 linhas)

`scripts/build_windows.ps1` (como modelo), `scripts/pack_entry.py`,
`src/xl_utils/ui/assets.py`, `src/xl_utils/shared/accounts.py` (só o cofre do
chaveiro), `docs/guide/release-windows.md` (estrutura do guia).

## Arquivos prováveis

- `scripts/build_linux.sh`, `packaging/linux/{AppRun,xl_utils.desktop}`
- `docs/guide/release-linux.md`, `docs/adr/0032-appimage-linux.md`
- `docs/reference/architecture.md` só se surgir módulo novo em `src/`

## Riscos

- O cliente Flet precisa de GTK 3 e de libs do sistema; o AppImage pode abrir
  no CachyOS e falhar numa distro limpa. Testar cedo.
- O `keyring` congelado pode perder os backends: o login some em silêncio, como
  antes da ADR 0030.
- O Python 3.15 free-threaded pode repetir as armadilhas do Windows
  (`python3t`, `_lzma`).
- O `flet pack` apaga `build/`: saída em `artifacts/`.
- O `appimagetool` vem da rede: versão e hash fixos.

## Próximo depois desta

S23b — workflow de release no GitHub Actions, só por disparo manual.
