"""Pacotes .tar.xz sintéticos para os testes de plugins."""

from __future__ import annotations

import hashlib
import io
import tarfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from xl_utils.shared.plugins.install import InstalledPlugin, scan_installed

VALID_MANIFEST = """\
[plugin]
id = "autor.teste"
name = "Plugin de Teste"
version = "1.0.0"
api_version = 1
entrypoint = "main:run"
description = "Plugin usado nos testes."
authors = ["Teste"]

[permissions]
network = false
filesystem = "read"
subprocess = false

[ui]
multiple_files = true
default_all_sheets = true

[[options]]
key = "modo"
label = "Modo"
type = "choice"
default = "a"
choices = ["a", "b"]
"""

MAIN_PY = "def run(request):\n    return None\n"


@contextmanager
def tar_writer(path: Path, *, preset: int = 1) -> Iterator[tarfile.TarFile]:
    """Abre um tar.xz de teste para escrita."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(path, "w:xz", preset=preset) as tar:
        yield tar


def add_file(tar: tarfile.TarFile, name: str, data: bytes = b"") -> None:
    """Acrescenta um arquivo regular."""
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mode = 0o644
    tar.addfile(info, io.BytesIO(data))


def add_dir(tar: tarfile.TarFile, name: str) -> None:
    """Acrescenta um diretório explícito."""
    info = tarfile.TarInfo(name)
    info.type = tarfile.DIRTYPE
    info.mode = 0o755
    tar.addfile(info)


def add_member(
    tar: tarfile.TarFile,
    name: str,
    *,
    kind: str = "sym",
    linkname: str = "",
) -> None:
    """Acrescenta uma entrada especial (symlink, hardlink, fifo ou device)."""
    info = tarfile.TarInfo(name)
    info.mode = 0o777
    if kind == "sym":
        info.type = tarfile.SYMTYPE
        info.linkname = linkname
    elif kind == "hard":
        info.type = tarfile.LNKTYPE
        info.linkname = linkname
    elif kind == "fifo":
        info.type = tarfile.FIFOTYPE
    elif kind == "chr":
        info.type = tarfile.CHRTYPE
        info.devmajor = 1
        info.devminor = 3
    elif kind == "blk":
        info.type = tarfile.BLKTYPE
        info.devmajor = 8
        info.devminor = 0
    else:
        raise ValueError(f"tipo desconhecido: {kind}")
    tar.addfile(info)


def valid_package(
    path: Path,
    *,
    manifest: str = VALID_MANIFEST,
    extra: dict[str, bytes] | None = None,
) -> Path:
    """Cria um pacote válido com manifesto, código e um asset."""
    with tar_writer(path) as tar:
        add_file(tar, "plugin.toml", manifest.encode("utf-8"))
        add_file(tar, "lib/main.py", MAIN_PY.encode("utf-8"))
        add_file(tar, "assets/logo.txt", b"logo")
        for name, data in (extra or {}).items():
            add_file(tar, name, data)
    return path


def write_sidecar(
    package: Path,
    *,
    digest: str | None = None,
    filename: str | None = None,
) -> Path:
    """Grava o sidecar SHA-256 do pacote."""
    value = digest or hashlib.sha256(package.read_bytes()).hexdigest()
    name = filename or package.name
    target = package.with_name(f"{package.name}.sha256")
    target.write_text(f"{value}  {name}\n", encoding="utf-8")
    return target


def installed_plugin(
    root: Path,
    *,
    plugin_id: str = "autor.teste",
    manifest: str = VALID_MANIFEST,
    files: dict[str, str] | None = None,
) -> InstalledPlugin:
    """Cria a pasta instalada sem empacotar, como a descoberta a encontraria."""
    path = root / plugin_id
    (path / "lib").mkdir(parents=True)
    (path / "data").mkdir()
    text = manifest.replace('id = "autor.teste"', f'id = "{plugin_id}"')
    (path / "plugin.toml").write_text(text, encoding="utf-8")
    sources = files or {"main.py": "def run(request):\n    return None\n"}
    for name, source in sources.items():
        target = path / "lib" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding="utf-8")
    valid = scan_installed(root=root).valid
    return next(item for item in valid if item.id == plugin_id)
