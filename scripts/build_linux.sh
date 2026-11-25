#!/usr/bin/env bash
# Gera o AppImage Linux a partir do wheel da versão corrente.
#
# Uso:
#   bash scripts/build_linux.sh
#   bash scripts/build_linux.sh --skip-appimage   # só o bundle do flet pack
#
# Requisitos: uv, curl, sha256sum e o ícone em assets/icon.png.
# O build usa um venv limpo em artifacts/linux/venv, instala o wheel e empacota
# com flet pack + PyInstaller. Nada de .venv, output/ ou cache do Drive entra.
# artifacts/ fica fora de build/ porque o flet pack apaga a pasta build/.
# appimagetool e o runtime type2 vêm do GitHub com versão e SHA-256 fixos e são
# conferidos antes de qualquer execução.

set -euo pipefail

skip_appimage=0
for arg in "$@"; do
    case "$arg" in
        --skip-appimage) skip_appimage=1 ;;
        *) echo "Opção desconhecida: $arg" >&2; exit 2 ;;
    esac
done

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

die() { echo "ERRO: $*" >&2; exit 1; }

[ "$(uname -m)" = "x86_64" ] || die "só x86_64 é suportado."
version="$(uv version --short | tr -d '[:space:]')"
[ -n "$version" ] || die "não foi possível ler a versão do pyproject.toml."
[ -f assets/icon.png ] || die "assets/icon.png não existe; gere com scripts/make_icons.py --pick N."

work="$root/artifacts/linux"
venv="$work/venv"
app="$work/app"
wheel_dir="$work/wheel"
appdir="$work/AppDir"
dist="$work/dist"
tools="$root/artifacts/tools"

# Ferramentas fixadas: trocar versão exige trocar o hash junto.
appimagetool_version="1.9.1"
appimagetool_url="https://github.com/AppImage/appimagetool/releases/download/${appimagetool_version}/appimagetool-x86_64.AppImage"
appimagetool_sha256="ed4ce84f0d9caff66f50bcca6ff6f35aae54ce8135408b3fa33abfc3cb384eb0"
runtime_version="20251108"
runtime_url="https://github.com/AppImage/type2-runtime/releases/download/${runtime_version}/runtime-x86_64"
runtime_sha256="2fca8b443c92510f1483a883f60061ad09b46b978b2631c807cd873a47ec260d"

echo "== Limpando artefatos =="
rm -rf "$venv" "$app" "$wheel_dir" "$appdir" "$dist"

echo "== Gerando o wheel $version =="
uv build --wheel --out-dir "$wheel_dir"
wheel="$(find "$wheel_dir" -maxdepth 1 -name '*.whl' | head -n 1)"
[ -n "$wheel" ] || die "uv build não gerou wheel."

echo "== Criando venv limpo e instalando o wheel =="
uv venv --python 3.15 "$venv"
# Versões travadas no uv.lock: sem isso o venv pega o Flet/PyInstaller mais
# novo do PyPI. O flet-cli não está no lock; segue a versão do flet.
constraints="$wheel_dir/constraints.txt"
uv export --frozen --no-hashes --no-emit-project --all-groups --output-file "$constraints" >/dev/null
flet_version="$(sed -nE 's/^flet==([^[:space:];]+).*/\1/p' "$constraints" | head -n 1)"
[ -n "$flet_version" ] || die "flet não está no uv.lock."
uv pip install --python "$venv/bin/python" -c "$constraints" "$wheel" pyinstaller "flet-cli==$flet_version"
echo "Flet $flet_version (uv.lock)"

echo "== Empacotando com flet pack (onedir) =="
configs="$("$venv/bin/python" -c 'import pathlib, xl_utils; print(pathlib.Path(xl_utils.__file__).parent / "configs")')"
[ -d "$configs" ] || die "configs/ não está no wheel ($configs)."
# Os ícones da sidebar e da janela são lidos de assets/ ao lado do bundle
# (sys._MEIPASS/assets). Sem --bundle-id: o cliente Flet 1.1.x ignora a
# identidade e a janela sai como com.appveyor.flet (ver packaging/linux).
# O keyring acha os backends (Secret Service, KWallet) por entry points:
# sem a metadata e os submódulos, o login no Drive falha (ADR 0030).
"$venv/bin/flet" pack scripts/pack_entry.py \
    -n "xl_Utils" \
    -D \
    --distpath "$app" \
    --icon "assets/icon.png" \
    --add-data "$configs:xl_utils/configs" \
    --add-data "$root/assets:assets" \
    --product-name "xl_Utils" \
    --file-description "Utilitários de planilha" \
    --product-version "$version" \
    --file-version "$version" \
    --company-name "francisN7" \
    -y \
    -- --copy-metadata xl-utils --copy-metadata flet --copy-metadata pandas \
       --copy-metadata keyring --collect-submodules keyring.backends \
       --hidden-import secretstorage --hidden-import jeepney

bundle="$app/xl_Utils"
exe="$bundle/xl_Utils"
[ -x "$exe" ] || die "o executável não foi gerado em $exe."

echo "== Conferindo o bundle =="
# A área de plugins usa tarfile + lzma no mesmo processo. No Python do uv
# para Linux o _lzma é built-in (vai dentro do libpython); senão, é um .so.
if "$venv/bin/python" -c 'import sys; sys.exit("_lzma" not in sys.builtin_module_names)'; then
    echo "Módulo lzma: built-in do libpython"
else
    lzma="$(find "$bundle" -name '_lzma*.so' | head -n 1)"
    [ -n "$lzma" ] || die "módulo _lzma não foi embutido no bundle."
    echo "Módulo lzma: $lzma"
fi
icon="$(find "$bundle" -path '*/assets/icon.png' | head -n 1)"
[ -n "$icon" ] || die "assets/icon.png não foi embutido no bundle."
echo "Ícone da sidebar: $icon"
find "$bundle" -path '*keyring-*.dist-info/entry_points.txt' | grep -q . \
    || die "metadata do keyring (entry points) não foi embutida."
client="$(find "$bundle" -path '*flet_desktop/app/flet-linux-*.tar.gz' | head -n 1)"
[ -n "$client" ] || die "cliente Flet não foi embutido em flet_desktop/app."
echo "Cliente Flet: $(basename "$client")"
"$venv/bin/python" - "$exe" <<'PY'
import sys
from PyInstaller.archive.readers import CArchiveReader

archive = CArchiveReader(sys.argv[1])
pyz_name = next(name for name in archive.toc if name.endswith(".pyz"))
names = set(archive.open_embedded_archive(pyz_name).toc)
needed = [
    "keyring.backends.SecretService",
    "keyring.backends.kwallet",
    "secretstorage",
    "jeepney",
    "cryptography",
]
missing = [name for name in needed if name not in names]
if missing:
    sys.exit(f"ERRO: módulos fora do bundle: {', '.join(missing)}")
print("Backends do keyring: ok")
PY

if [ "$skip_appimage" = 1 ]; then
    echo "Build pronto: $exe"
    exit 0
fi

fetch() {  # fetch <url> <destino> <sha256>
    local url="$1" dest="$2" sha="$3"
    if [ ! -f "$dest" ] || ! echo "$sha  $dest" | sha256sum -c --status; then
        echo "Baixando $(basename "$dest")..."
        curl -fL --proto '=https' --tlsv1.2 -o "$dest.part" "$url"
        mv "$dest.part" "$dest"
    fi
    echo "$sha  $dest" | sha256sum -c --quiet || { rm -f "$dest"; die "SHA-256 inválido: $dest"; }
}

echo "== Conferindo appimagetool $appimagetool_version e runtime $runtime_version =="
mkdir -p "$tools"
appimagetool="$tools/appimagetool-${appimagetool_version}-x86_64.AppImage"
runtime="$tools/runtime-${runtime_version}-x86_64"
fetch "$appimagetool_url" "$appimagetool" "$appimagetool_sha256"
fetch "$runtime_url" "$runtime" "$runtime_sha256"
chmod +x "$appimagetool"

echo "== Montando o AppDir =="
mkdir -p "$appdir/usr/lib"
cp -a "$bundle" "$appdir/usr/lib/xl_Utils"
install -m 755 packaging/linux/AppRun "$appdir/AppRun"
install -m 644 packaging/linux/xl_utils.desktop "$appdir/xl_utils.desktop"
install -m 644 assets/icon.png "$appdir/xl_utils.png"
ln -s xl_utils.png "$appdir/.DirIcon"

echo "== Gerando o AppImage =="
mkdir -p "$dist"
image="$dist/xl_Utils-${version}-x86_64.AppImage"
# Extrair e rodar dispensa FUSE na máquina de build (CI, contêiner).
APPIMAGE_EXTRACT_AND_RUN=1 ARCH=x86_64 "$appimagetool" \
    --no-appstream \
    --runtime-file "$runtime" \
    "$appdir" "$image"
[ -f "$image" ] || die "o AppImage não foi gerado."

(cd "$dist" && sha256sum "$(basename "$image")" > SHA256SUMS.txt)
echo "AppImage: $image"
echo "Tamanho: $(du -m "$image" | cut -f1) MB"
echo "SHA-256: $(cut -d' ' -f1 "$dist/SHA256SUMS.txt")"
