"""Inspeção, validação, extração e empacotamento de plugins ``.tar.xz``.

Entrada: caminho do pacote ou da pasta de origem.
Saída: ``PackageInfo``, arquivos extraídos ou pacote + sidecar.
Erros: ``PackageError`` (e ``ManifestError``) com código estável.
Nenhum código do plugin é importado.
"""

from __future__ import annotations

import hashlib
import hmac
import io
import lzma
import re
import tarfile
import unicodedata
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import BinaryIO

from xl_utils.core.plugins.errors import ManifestError, PackageError
from xl_utils.core.plugins.manifest import (
    MAX_MANIFEST_BYTES,
    PluginManifest,
    entrypoint_parts,
    parse_manifest,
)

MAX_ARCHIVE_BYTES = 100 * 1024 * 1024
MAX_EXTRACTED_BYTES = 500 * 1024 * 1024
MAX_ENTRIES = 10_000
MAX_FILE_BYTES = 200 * 1024 * 1024
MAX_RATIO = 500
MAX_NAME_LENGTH = 180
MAX_PATH_LENGTH = 250
XZ_MEMORY_LIMIT = 256 * 1024 * 1024
READ_CHUNK = 64 * 1024
COPY_CHUNK = 1024 * 1024

_FORBIDDEN_SUFFIXES = frozenset(
    {
        ".bat",
        ".cmd",
        ".com",
        ".cpl",
        ".dll",
        ".dylib",
        ".exe",
        ".jar",
        ".js",
        ".jse",
        ".lnk",
        ".msi",
        ".pyd",
        ".pyw",
        ".pyz",
        ".ps1",
        ".reg",
        ".scr",
        ".sh",
        ".so",
        ".vbs",
        ".wsf",
    }
)
_INVALID_CHARS = frozenset('<>:"|?*')
_WINDOWS_RESERVED = frozenset(
    {
        "aux",
        "com1",
        "com2",
        "com3",
        "com4",
        "com5",
        "com6",
        "com7",
        "com8",
        "com9",
        "con",
        "lpt1",
        "lpt2",
        "lpt3",
        "lpt4",
        "lpt5",
        "lpt6",
        "lpt7",
        "lpt8",
        "lpt9",
        "nul",
        "prn",
    }
)
_EXCLUDED_PARTS = frozenset(
    {
        "__pycache__",
        ".git",
        ".hg",
        ".pytest_cache",
        ".ruff_cache",
        ".svn",
        ".venv",
        "node_modules",
    }
)
_EXCLUDED_NAMES = frozenset({".DS_Store", "Thumbs.db"})


@dataclass(frozen=True, slots=True)
class PackageLimits:
    """Tetos configuráveis; os testes usam valores menores."""

    max_archive_bytes: int = MAX_ARCHIVE_BYTES
    max_extracted_bytes: int = MAX_EXTRACTED_BYTES
    max_entries: int = MAX_ENTRIES
    max_file_bytes: int = MAX_FILE_BYTES
    max_ratio: int = MAX_RATIO
    max_name_length: int = MAX_NAME_LENGTH
    max_path_length: int = MAX_PATH_LENGTH
    xz_memory_limit: int = XZ_MEMORY_LIMIT


DEFAULT_LIMITS = PackageLimits()


@dataclass(frozen=True, slots=True)
class Entry:
    """Uma entrada validada do tar."""

    name: str
    size: int
    is_dir: bool


@dataclass(frozen=True, slots=True)
class PackageInfo:
    """Resultado da inspeção de um pacote."""

    entries: tuple[Entry, ...]
    manifest: PluginManifest
    total_size: int
    archive_size: int

    @property
    def files(self) -> tuple[Entry, ...]:
        """Devolve só as entradas de arquivo regular."""
        return tuple(entry for entry in self.entries if not entry.is_dir)


def sidecar_path(archive: Path) -> Path:
    """Devolve ``<pacote>.tar.xz.sha256``."""
    return archive.with_name(f"{archive.name}.sha256")


def sha256_file(path: Path) -> str:
    """Calcula o SHA-256 em streaming."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(COPY_CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def write_sidecar(
    archive: Path,
    *,
    digest: str | None = None,
    filename: str | None = None,
) -> Path:
    """Grava o sidecar no formato ``hash  nome`` e devolve o caminho."""
    target = sidecar_path(archive)
    value = digest or sha256_file(archive)
    name = filename or archive.name
    target.write_text(f"{value}  {name}\n", encoding="utf-8")
    return target


def verify_sidecar(archive: Path, sidecar: Path | None = None) -> str:
    """Confere o SHA-256 do pacote contra o sidecar e devolve o hash."""
    archive = Path(archive)
    if not archive.is_file():
        raise PackageError("archive_missing", f"Pacote não encontrado: {archive}.")
    target = Path(sidecar) if sidecar is not None else sidecar_path(archive)
    if not target.is_file():
        raise PackageError("digest_missing", f"Sidecar ausente: {target}.")
    try:
        text = target.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise PackageError(
            "digest_invalid",
            f"Sidecar inválido: {target}: {error}",
        ) from error

    expected = _read_digest(text, archive.name, target)
    actual = sha256_file(archive)
    if not hmac.compare_digest(expected, actual):
        raise PackageError(
            "digest_invalid",
            f"SHA-256 não confere para {archive.name}.",
        )
    return actual


def _read_digest(text: str, archive_name: str, sidecar: Path) -> str:
    found: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            raise PackageError(
                "digest_invalid",
                f"Linha inválida em {sidecar.name}: {raw_line!r}.",
            )
        digest, filename = parts
        filename = filename.lstrip("*").replace("\\", "/").rsplit("/", 1)[-1]
        if filename.casefold() != archive_name.casefold():
            continue
        if found is not None:
            raise PackageError(
                "digest_invalid",
                f"Mais de um hash para {archive_name} em {sidecar.name}.",
            )
        if not re.fullmatch(r"[0-9A-Fa-f]{64}", digest):
            raise PackageError(
                "digest_invalid",
                f"Hash inválido para {archive_name} em {sidecar.name}.",
            )
        found = digest.lower()
    if found is None:
        raise PackageError(
            "digest_invalid",
            f"{sidecar.name} não tem hash para {archive_name}.",
        )
    return found


def inspect_package(
    archive: Path,
    *,
    limits: PackageLimits = DEFAULT_LIMITS,
    app_version: str | None = None,
) -> PackageInfo:
    """Inspeciona o tar e valida manifesto, caminhos e limites."""
    archive = Path(archive)
    if not archive.is_file():
        raise PackageError("archive_missing", f"Pacote não encontrado: {archive}.")
    if not archive.name.lower().endswith(".tar.xz"):
        raise PackageError(
            "archive_type",
            f"Pacote deve terminar em .tar.xz: {archive.name}.",
        )
    archive_size = archive.stat().st_size
    if archive_size > limits.max_archive_bytes:
        raise PackageError(
            "archive_too_large",
            f"Pacote com {archive_size} bytes passa do limite "
            f"de {limits.max_archive_bytes}.",
        )

    entries: list[Entry] = []
    manifest_raw: bytes | None = None
    total = 0
    try:
        with archive.open("rb") as raw:
            reader = _XzReader(
                raw,
                memlimit=limits.xz_memory_limit,
                max_bytes=limits.max_extracted_bytes + 64 * 1024 * 1024,
            )
            with tarfile.open(fileobj=reader, mode="r|") as tar:
                for member, entry in _iter_members(tar, limits):
                    entries.append(entry)
                    if entry.name == "plugin.toml":
                        if entry.is_dir:
                            raise PackageError(
                                "manifest_invalid",
                                "plugin.toml não pode ser diretório.",
                            )
                        source = tar.extractfile(member)
                        if source is None:
                            raise PackageError(
                                "manifest_invalid",
                                "plugin.toml não pôde ser lido.",
                            )
                        data = source.read(MAX_MANIFEST_BYTES + 1)
                        if len(data) > MAX_MANIFEST_BYTES:
                            raise ManifestError(
                                "manifest_too_large",
                                f"plugin.toml passa de {MAX_MANIFEST_BYTES} bytes.",
                            )
                        manifest_raw = data
                    if not entry.is_dir:
                        total += entry.size
    except (tarfile.TarError, lzma.LZMAError, EOFError, OSError) as error:
        raise PackageError(
            "archive_corrupt",
            f"Pacote corrompido ou truncado: {error}",
        ) from error

    if manifest_raw is None:
        raise PackageError("manifest_missing", "Falta plugin.toml na raiz do pacote.")
    manifest = parse_manifest(
        manifest_raw,
        source="plugin.toml",
        app_version=app_version,
    )
    _check_entrypoint(manifest, entries)
    if archive_size > 0 and total > archive_size * limits.max_ratio:
        raise PackageError(
            "ratio_exceeded",
            f"Conteúdo extraído ({total} bytes) passa da razão "
            f"{limits.max_ratio}:1 do pacote.",
        )
    return PackageInfo(
        entries=tuple(entries),
        manifest=manifest,
        total_size=total,
        archive_size=archive_size,
    )


def extract_package(
    archive: Path,
    destination: Path,
    info: PackageInfo,
    *,
    limits: PackageLimits = DEFAULT_LIMITS,
) -> None:
    """Extrai o pacote já inspecionado, sem symlink e sem sobrescrever."""
    archive = Path(archive)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    expected = {entry.name: entry for entry in info.entries}
    written: set[str] = set()
    total = 0
    root = destination.resolve()
    try:
        with archive.open("rb") as raw:
            reader = _XzReader(
                raw,
                memlimit=limits.xz_memory_limit,
                max_bytes=limits.max_extracted_bytes + 64 * 1024 * 1024,
            )
            with tarfile.open(fileobj=reader, mode="r|") as tar:
                for member, entry in _iter_members(tar, limits):
                    if entry.name not in expected:
                        raise PackageError(
                            "archive_corrupt",
                            f"Entrada inesperada na extração: {entry.name}.",
                        )
                    target = destination.joinpath(*PurePosixPath(entry.name).parts)
                    if not target.resolve().is_relative_to(root):
                        raise PackageError(
                            "entry_unsafe",
                            f"Destino fora da pasta do plugin: {entry.name}.",
                        )
                    if entry.is_dir:
                        target.mkdir(parents=True, exist_ok=True)
                    else:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        source = tar.extractfile(member)
                        if source is None:
                            raise PackageError(
                                "archive_corrupt",
                                f"Falha ao ler {entry.name}.",
                            )
                        remaining = entry.size
                        with target.open("xb") as output:
                            while remaining:
                                chunk = source.read(min(COPY_CHUNK, remaining))
                                if not chunk:
                                    raise PackageError(
                                        "archive_corrupt",
                                        f"Arquivo truncado: {entry.name}.",
                                    )
                                output.write(chunk)
                                remaining -= len(chunk)
                                total += len(chunk)
                                if total > limits.max_extracted_bytes:
                                    raise PackageError(
                                        "extracted_too_large",
                                        "Conteúdo extraído passa do limite.",
                                    )
                            if source.read(1):
                                raise PackageError(
                                    "archive_corrupt",
                                    f"Arquivo maior que o declarado: {entry.name}.",
                                )
                    written.add(entry.name)
    except (tarfile.TarError, lzma.LZMAError, EOFError, OSError) as error:
        raise PackageError(
            "archive_corrupt",
            f"Pacote corrompido ou truncado: {error}",
        ) from error

    if written != set(expected):
        raise PackageError(
            "archive_corrupt",
            "A extração não entregou todas as entradas inspecionadas.",
        )


def build_package(
    source: Path,
    output: Path,
    *,
    limits: PackageLimits = DEFAULT_LIMITS,
) -> Path:
    """Empacota uma pasta em ``.tar.xz`` determinístico e grava o sidecar."""
    source = Path(source)
    output = Path(output)
    if not source.is_dir():
        raise PackageError("source_missing", f"Pasta de origem ausente: {source}.")
    if not output.name.lower().endswith(".tar.xz"):
        raise PackageError("archive_type", "A saída deve terminar em .tar.xz.")

    manifest_path = source / "plugin.toml"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ManifestError("manifest_missing", "Falta plugin.toml na raiz da pasta.")
    parse_manifest(manifest_path.read_bytes(), source="plugin.toml")

    output.parent.mkdir(parents=True, exist_ok=True)
    output_resolved = output.resolve()
    sidecar_resolved = sidecar_path(output).resolve()
    files: list[tuple[str, Path]] = []
    total = 0
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise PackageError("entry_type", f"Symlink recusado: {path}.")
        if path.is_dir():
            continue
        resolved = path.resolve()
        if resolved in (output_resolved, sidecar_resolved):
            continue
        relative = path.relative_to(source).as_posix()
        if _is_excluded(relative):
            continue
        name = _validate_name(relative, limits)
        _check_content(name, is_dir=False)
        size = path.stat().st_size
        if size > limits.max_file_bytes:
            raise PackageError(
                "entry_too_large",
                f"{name} passa do limite de {limits.max_file_bytes} bytes.",
            )
        total += size
        if total > limits.max_extracted_bytes:
            raise PackageError(
                "extracted_too_large",
                "Conteúdo extraído passa do limite.",
            )
        files.append((name, path))
    if len(files) > limits.max_entries:
        raise PackageError("too_many_entries", "Entradas demais no pacote.")

    try:
        with tarfile.open(
            output,
            "w:xz",
            preset=9 | lzma.PRESET_EXTREME,
        ) as tar:
            for name, path in files:
                info = tar.gettarinfo(str(path), arcname=name)
                info.mtime = 0
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
                info.mode = 0o644
                info.pax_headers = {}
                with path.open("rb") as stream:
                    tar.addfile(info, stream)
    except OSError as error:
        raise PackageError(
            "archive_corrupt",
            f"Não foi possível gerar o pacote: {error}",
        ) from error

    inspect_package(output, limits=limits)
    write_sidecar(output)
    return output


def _iter_members(
    tar: tarfile.TarFile,
    limits: PackageLimits,
) -> Iterator[tuple[tarfile.TarInfo, Entry]]:
    seen: dict[str, str] = {}
    total = 0
    for count, member in enumerate(tar, start=1):
        if count > limits.max_entries:
            raise PackageError(
                "too_many_entries",
                f"O pacote passa de {limits.max_entries} entradas.",
            )
        if member.type == tarfile.GNUTYPE_SPARSE or member.sparse is not None:
            raise PackageError("entry_type", f"Arquivo sparse recusado: {member.name}.")
        if member.isdir():
            is_dir = True
            size = 0
        elif member.isreg():
            is_dir = False
            size = member.size
        else:
            raise PackageError(
                "entry_type",
                f"Tipo de entrada recusado: {member.name}.",
            )
        name = _validate_name(member.name, limits)
        if name == "plugin.toml" and is_dir:
            raise PackageError(
                "manifest_invalid",
                "plugin.toml não pode ser diretório.",
            )
        key = name.casefold()
        if key in seen:
            raise PackageError(
                "entry_duplicate",
                f"Entrada duplicada ou com caixa repetida: {name}.",
            )
        seen[key] = name
        _check_content(name, is_dir)

        if not is_dir:
            if size < 0:
                raise PackageError("archive_corrupt", f"Tamanho inválido em {name}.")
            if size > limits.max_file_bytes:
                raise PackageError(
                    "entry_too_large",
                    f"{name} passa do limite de {limits.max_file_bytes} bytes.",
                )
            total += size
            if total > limits.max_extracted_bytes:
                raise PackageError(
                    "extracted_too_large",
                    "Conteúdo extraído passa do limite.",
                )
        yield member, Entry(name=name, size=size, is_dir=is_dir)


def _validate_name(name: str, limits: PackageLimits) -> str:
    if not name or name in (".", "./"):
        raise PackageError("entry_unsafe", "Nome de entrada vazio.")
    if "\x00" in name or any(ord(char) < 32 or ord(char) == 127 for char in name):
        raise PackageError("entry_unsafe", "Nome de entrada com controle.")
    if "\\" in name:
        raise PackageError("entry_unsafe", "Barra invertida recusada no pacote.")
    if name.startswith("/"):
        raise PackageError("entry_unsafe", f"Caminho absoluto recusado: {name}.")
    if re.match(r"^[A-Za-z]:", name):
        raise PackageError("entry_unsafe", f"Caminho com unidade recusado: {name}.")
    try:
        if not unicodedata.is_normalized("NFC", name):
            raise PackageError("entry_unsafe", f"Nome fora de NFC: {name}.")
        windows_length = len(name.encode("utf-16-le")) // 2
    except UnicodeEncodeError as error:
        raise PackageError("entry_unsafe", f"Nome Unicode inválido: {name}.") from error
    if windows_length > limits.max_name_length:
        raise PackageError(
            "entry_unsafe",
            f"Nome com {windows_length} caracteres passa do limite "
            f"de {limits.max_name_length}.",
        )

    pure = PurePosixPath(name)
    if pure.is_absolute() or not pure.parts:
        raise PackageError("entry_unsafe", f"Caminho inválido: {name}.")
    for part in pure.parts:
        if part in (".", "..") or not part:
            raise PackageError("entry_unsafe", f"Componente inválido: {name}.")
        if part != part.rstrip(" ."):
            raise PackageError(
                "entry_unsafe",
                f"Nome com ponto ou espaço no fim: {part!r}.",
            )
        if any(char in _INVALID_CHARS for char in part):
            raise PackageError("entry_unsafe", f"Caractere inválido em {part!r}.")
        if part.casefold().split(".", 1)[0] in _WINDOWS_RESERVED:
            raise PackageError("entry_unsafe", f"Nome reservado do Windows: {part}.")
    return "/".join(pure.parts)


def _check_content(name: str, is_dir: bool) -> None:
    parts = PurePosixPath(name).parts
    if any(part.casefold() == "__pycache__" for part in parts):
        raise PackageError("forbidden_content", f"__pycache__ recusado: {name}.")
    if name == "plugin.toml":
        if is_dir:
            raise PackageError("manifest_invalid", "plugin.toml é arquivo.")
        return
    if name.rsplit("/", 1)[-1] == "plugin.toml":
        raise PackageError("manifest_nested", f"plugin.toml aninhado: {name}.")
    if name == "data" or name.startswith("data/"):
        raise PackageError("reserved_path", f"'data/' é criado pelo host: {name}.")
    if name.rsplit("/", 1)[-1] == "install.json":
        raise PackageError("reserved_path", f"install.json é do host: {name}.")
    if name == "lib" and not is_dir:
        raise PackageError("forbidden_content", "lib deve ser diretório.")
    suffix = PurePosixPath(name).suffix.casefold()
    if suffix == ".pyc":
        raise PackageError("forbidden_content", f".pyc recusado: {name}.")
    if suffix == ".py" and not name.startswith("lib/"):
        raise PackageError("forbidden_content", f".py fora de lib/: {name}.")
    if suffix in _FORBIDDEN_SUFFIXES:
        raise PackageError(
            "forbidden_content",
            f"Executável ou binário recusado: {name}.",
        )


def _check_entrypoint(manifest: PluginManifest, entries: list[Entry]) -> None:
    module, _function = entrypoint_parts(manifest.entrypoint)
    relative = module.replace(".", "/")
    files = {entry.name for entry in entries if not entry.is_dir}
    candidates = {f"lib/{relative}.py", f"lib/{relative}/__init__.py"}
    if not candidates & files:
        raise PackageError(
            "entrypoint_missing",
            f"Entrypoint sem arquivo em lib/: {manifest.entrypoint}.",
        )


def _is_excluded(relative: str) -> bool:
    parts = PurePosixPath(relative).parts
    if any(part.casefold() in _EXCLUDED_PARTS for part in parts):
        return True
    return bool(parts) and parts[-1] in _EXCLUDED_NAMES


class _XzReader(io.RawIOBase):
    """Lê o xz em streaming, com limite de memória e de bytes."""

    def __init__(self, stream: BinaryIO, *, memlimit: int, max_bytes: int) -> None:
        super().__init__()
        self._stream = stream
        self._decompressor = lzma.LZMADecompressor(
            format=lzma.FORMAT_XZ,
            memlimit=memlimit,
        )
        self._buffer = b""
        self._eof = False
        self._total = 0
        self._max = max_bytes

    def readable(self) -> bool:
        """Este leitor só lê."""
        return True

    def read(self, size: int = -1) -> bytes:
        """Devolve até ``size`` bytes descomprimidos."""
        if size is None or size < 0:
            chunks: list[bytes] = []
            while chunk := self.read(COPY_CHUNK):
                chunks.append(chunk)
            return b"".join(chunks)
        if size == 0:
            return b""
        while len(self._buffer) < size and not self._eof:
            self._fill()
        data = self._buffer[:size]
        self._buffer = self._buffer[size:]
        self._total += len(data)
        if self._total > self._max:
            raise PackageError(
                "extracted_too_large",
                "Conteúdo descomprimido passa do limite de segurança.",
            )
        return data

    def _fill(self) -> None:
        if self._decompressor.needs_input:
            chunk = self._stream.read(READ_CHUNK)
            if not chunk:
                self._eof = True
                return
            output = self._decompressor.decompress(chunk, max_length=COPY_CHUNK)
        else:
            output = self._decompressor.decompress(b"", max_length=COPY_CHUNK)
        if output:
            self._buffer += output
        if self._decompressor.eof:
            self._eof = True
