# Release Linux

Como gerar, validar e publicar o AppImage do xl_Utils. O build é local, em
Linux x86_64. Não precisa de Flutter, de FUSE nem de root.

## Pré-requisitos

- `uv` e Python 3.15, `curl` e `sha256sum` na máquina de build.
- Ícone em `assets/icon.png`, o mesmo do Windows.
- Rede no primeiro build: `appimagetool` 1.9.1 e o runtime type2 `20251108` vêm
  do GitHub da organização AppImage. Versão e SHA-256 estão fixos em
  `scripts/build_linux.sh` e o script confere o hash antes de executar.
  Os dois ficam em cache em `artifacts/tools/`.

## Build

```bash
uv run ruff check src tests
uv run pytest
uv run python scripts/check_docs.py
bash scripts/build_linux.sh
```

O script limpa `artifacts/linux/` e gera o wheel. Em seguida cria
`artifacts/linux/venv`, instala o wheel com o PyInstaller e o `flet-cli` nas
versões do `uv.lock` e empacota com `flet pack` em modo onedir. Antes de montar o AppDir, confere no
bundle:

- `_lzma`, que no Python do uv é built-in;
- `assets/icon.png`;
- o cliente Flet embutido;
- a metadata e os backends do `keyring` (Secret Service e KWallet), junto com
  `secretstorage`, `jeepney` e `cryptography`.

Depois monta o AppDir com os arquivos de `packaging/linux/` (`AppRun` e
`xl_utils.desktop`). Saídas:

- `artifacts/linux/app/xl_Utils/xl_Utils`: o bundle, que roda sem AppImage;
- `artifacts/linux/dist/xl_Utils-<versão>-x86_64.AppImage`;
- `artifacts/linux/dist/SHA256SUMS.txt`.

`--skip-appimage` para no bundle. O build não usa `.venv`, `output/` nem o
cache do Drive.

## Build no CI

`.github/workflows/release.yml` gera o mesmo AppImage num runner
`ubuntu-24.04`, que define o piso de glibc 2.39, junto com o instalador
Windows. Ele só roda por disparo manual: **Actions → Release → Run workflow**,
com o campo `confirmar` igual a `build`. Com qualquer outro texto, o job
`guarda` falha e nada é compilado. Push, tag e PR não disparam o workflow.

O job roda `scripts/build_linux.sh` e, para o smoke test, instala `xvfb` e as
bibliotecas da seção abaixo. Depois abre o AppImage num `Xvfb` com
`APPIMAGE_EXTRACT_AND_RUN=1` (o runner não tem FUSE) e GL por software. O app e
o cliente Flet (processo `flet`) precisam ficar vivos por 10 s, sem `Traceback`
no log. O artefato `xl_Utils-<versão>-linux` traz o AppImage e o
`SHA256SUMS.txt` e fica 7 dias no run. O workflow não publica release.

## Requisitos do sistema

- **glibc ≥ 2.39**: Ubuntu 24.04, Fedora 40, Debian 13 ou mais novos. O
  cliente Flet embutido é o `ubuntu24.04-light`. Numa glibc mais velha, o Flet
  procura outro cliente e tenta baixá-lo do GitHub, e o `libstdc++` embutido
  já exige 2.38.
- Bibliotecas que qualquer desktop GNOME ou KDE já tem. Num sistema mínimo,
  instale-as (nomes do Ubuntu 24.04):
  `libgtk-3-0t64 libepoxy0 libsecret-1-0 libgl1 libegl1 libgles2 libgl1-mesa-dri`.
- Login do Drive: Secret Service (GNOME Keyring, KeePassXC) ou KWallet ativo
  e desbloqueado (ADR 0030).
- Sem FUSE: `./xl_Utils-<versão>-x86_64.AppImage --appimage-extract-and-run`.

Na primeira execução, o cliente Flet é extraído em `~/.flet/client/`. Os dados
do app ficam em `~/.xl_utils/`, como no `uv run`.

## Validação

1. Na máquina de build (KDE/GNOME), conferir o hash com
   `sha256sum -c SHA256SUMS.txt` e abrir o AppImage. Conferir o título
   `xl_Utils`, o ícone na janela e na barra de tarefas, e o tema e as contas
   de `~/.xl_utils/`.
2. Rodar Extrair CNJs com uma planilha fictícia e conferir a pasta `output/` ao
   lado dela.
3. Entrar com Google e conferir o token no chaveiro (KWalletManager ou Seahorse).
4. Distro limpa com Podman (Ubuntu 24.04, janela no X/XWayland do host):

```bash
podman run --rm -it --ipc=host --security-opt label=disable \
  -e DISPLAY="$DISPLAY" -e XAUTHORITY=/xauth -v "$XAUTHORITY":/xauth:ro \
  -v /tmp/.X11-unix:/tmp/.X11-unix:ro -v "$PWD/artifacts/linux/dist":/w:ro \
  docker.io/library/ubuntu:24.04 bash
# dentro do contêiner:
apt-get update && apt-get install -y --no-install-recommends \
  libgtk-3-0t64 libepoxy0 libsecret-1-0 libgl1 libegl1 libgles2 libgl1-mesa-dri
cp /w/*.AppImage /tmp/a && /tmp/a --appimage-extract-and-run
```

## Limites conhecidos

- O `--web` não existe no executável: o `flet_web` não entra no bundle, e no
  Windows é igual.
- A janela se identifica como `com.appveyor.flet`, porque o cliente Flet 1.1.x
  ignora o `FLET_APP_ID` do `flet pack`. Por isso o `StartupWMClass` do
  `.desktop` aponta para esse nome.
- O AppImage não é assinado e não traz informação de atualização (zsync).

## Publicação

O AppImage entra na mesma release do instalador Windows. Publique os dois
`SHA256SUMS.txt` ou junte os dois num só. Os arquivos podem vir do build local
ou do artefato do workflow (**Build no CI**), como na 0.4.0.

```bash
gh release upload v<versão> \
  artifacts/linux/dist/xl_Utils-<versão>-x86_64.AppImage \
  artifacts/linux/dist/SHA256SUMS.txt
```

As notas trazem o piso de glibc, o comando `chmod +x` e o SHA-256.
