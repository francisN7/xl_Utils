"""Instalação, descoberta e desinstalação de plugins locais.

Entrada: pacote ``.tar.xz`` validado e raiz de plugins.
Saída: ``InstalledPlugin``, ``ScanResult`` ou pasta removida.
Erros: ``PluginError`` com código estável. Nada do plugin é importado.
"""

from __future__ import annotations

import hmac
import importlib.metadata as metadata
import json
import os
import shutil
import stat
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

from xl_utils import __version__
from xl_utils.core.plugins.errors import (
    InstallError,
    ManifestError,
    PackageError,
    PluginError,
)
from xl_utils.core.plugins.manifest import (
    MAX_MANIFEST_BYTES,
    PluginManifest,
    entrypoint_parts,
    parse_manifest,
    validate_id,
)
from xl_utils.core.plugins.package import (
    DEFAULT_LIMITS,
    PackageInfo,
    PackageLimits,
    extract_package,
    inspect_package,
    sha256_file,
    verify_sidecar,
)
from xl_utils.shared.settings import APP_DIR

STAGING_DIR = ".staging"
STAGING_MAX_AGE = 24 * 60 * 60
FREE_SPACE_MARGIN = 32 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class InstalledPlugin:
    """Plugin descoberto em disco, sem código carregado."""

    id: str
    name: str
    version: str
    api_version: int
    path: Path
    data_dir: Path
    manifest: PluginManifest | None = None


@dataclass(frozen=True, slots=True)
class InvalidPlugin:
    """Pasta de plugin que não passou na validação do manifesto."""

    path: Path
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class ScanResult:
    """Separa plugins válidos dos inválidos, sem derrubar a descoberta."""

    valid: tuple[InstalledPlugin, ...]
    invalid: tuple[InvalidPlugin, ...]


def plugins_root() -> Path:
    """Devolve ``%LOCALAPPDATA%/xl_utils/plugins`` ou o equivalente em casa."""
    local = os.environ.get("LOCALAPPDATA")
    base = Path(local) / APP_DIR if local else Path.home() / f".{APP_DIR}"
    return base / "plugins"


def install_package(
    archive: Path,
    *,
    root: Path | None = None,
    sidecar: Path | None = None,
    limits: PackageLimits = DEFAULT_LIMITS,
    app_version: str | None = None,
) -> InstalledPlugin:
    """Valida, extrai e promove um plugin para ``plugins/<id>/``."""
    archive = Path(archive)
    base = Path(root) if root is not None else plugins_root()
    try:
        base.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise InstallError(
            "install_failed",
            f"Não foi possível criar a raiz de plugins: {error}",
        ) from error
    _cleanup_staging(base)

    if not archive.is_file():
        raise PackageError("archive_missing", f"Pacote não encontrado: {archive}.")
    if archive.stat().st_size > limits.max_archive_bytes:
        raise PackageError(
            "archive_too_large",
            f"Pacote com {archive.stat().st_size} bytes passa do limite "
            f"de {limits.max_archive_bytes}.",
        )
    expected = verify_sidecar(archive, sidecar)
    version = app_version or __version__
    info = inspect_package(archive, limits=limits, app_version=version)
    _check_dependencies(info.manifest)

    target = base / info.manifest.id
    if os.path.lexists(target):
        raise InstallError(
            "plugin_duplicate",
            f"Já existe um plugin instalado com id {info.manifest.id}.",
        )
    _check_path_lengths(target, info, limits)

    staging = base / STAGING_DIR / f"{info.manifest.id}-{uuid.uuid4().hex}"
    try:
        staging.mkdir(parents=True, exist_ok=True)
        copied = staging / ".package.tar.xz"
        shutil.copyfile(archive, copied)
        if not hmac.compare_digest(sha256_file(copied), expected):
            raise PackageError(
                "digest_invalid",
                "A cópia do pacote não tem o mesmo SHA-256.",
            )
        _ensure_space(staging, info.total_size)
        extract_package(copied, staging, info, limits=limits)
        (staging / "data").mkdir()
        _write_record(staging, info, expected, archive.name)
        copied.unlink()
        _promote(staging, target)
        _prune_staging(base)
    except FileExistsError as error:
        shutil.rmtree(staging, ignore_errors=True)
        raise InstallError(
            "plugin_duplicate",
            f"Já existe um plugin em {target}.",
        ) from error
    except OSError as error:
        shutil.rmtree(staging, ignore_errors=True)
        raise InstallError(
            "install_failed",
            f"Falha ao instalar {info.manifest.id}: {error}",
        ) from error
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise

    return InstalledPlugin(
        id=info.manifest.id,
        name=info.manifest.name,
        version=info.manifest.version,
        api_version=info.manifest.api_version,
        path=target,
        data_dir=target / "data",
        manifest=info.manifest,
    )


def uninstall_plugin(plugin_id: str, *, root: Path | None = None) -> None:
    """Remove a pasta do plugin, inclusive os dados; não segue link."""
    validate_id(plugin_id, source="plugin")
    base = Path(root) if root is not None else plugins_root()
    target = base / plugin_id
    if target.is_symlink() or _is_junction(target):
        if target.is_symlink() and not target.is_dir():
            os.unlink(target)
        else:
            os.rmdir(target)
        return
    if not target.exists():
        raise InstallError("not_installed", f"Plugin não instalado: {plugin_id}.")
    if not target.is_dir() or target.resolve().parent != base.resolve():
        raise InstallError(
            "entry_unsafe",
            f"Destino de desinstalação inválido: {target}.",
        )
    try:
        shutil.rmtree(target, onexc=_remove_readonly)
    except OSError as error:
        raise InstallError(
            "install_failed",
            f"Falha ao remover {plugin_id}: {error}",
        ) from error


def scan_installed(
    *,
    root: Path | None = None,
    app_version: str | None = None,
) -> ScanResult:
    """Lê os manifestos instalados sem importar código do plugin."""
    base = Path(root) if root is not None else plugins_root()
    valid: list[InstalledPlugin] = []
    invalid: list[InvalidPlugin] = []
    if not base.is_dir():
        return ScanResult((), ())
    version = app_version or __version__
    for path in sorted(base.iterdir(), key=lambda item: item.name.casefold()):
        if path.name == STAGING_DIR or not path.is_dir():
            continue
        if path.is_symlink() or _is_junction(path):
            invalid.append(
                InvalidPlugin(
                    path=path,
                    code="entry_type",
                    message="Pasta de plugin é link ou junction.",
                )
            )
            continue
        manifest_path = path / "plugin.toml"
        try:
            if not manifest_path.is_file():
                raise ManifestError(
                    "manifest_missing",
                    f"Falta plugin.toml em {path.name}.",
                )
            if manifest_path.stat().st_size > MAX_MANIFEST_BYTES:
                raise ManifestError(
                    "manifest_too_large",
                    f"plugin.toml em {path.name} passa de {MAX_MANIFEST_BYTES} bytes.",
                )
            manifest = parse_manifest(
                manifest_path.read_bytes(),
                source=f"{path.name}/plugin.toml",
                app_version=version,
            )
            if manifest.id != path.name:
                raise ManifestError(
                    "invalid_id",
                    f"ID {manifest.id} não confere com a pasta {path.name}.",
                )
            _check_entrypoint_exists(path, manifest)
        except PluginError as error:
            invalid.append(
                InvalidPlugin(
                    path=path,
                    code=error.code,
                    message=str(error),
                )
            )
            continue
        except OSError as error:
            invalid.append(
                InvalidPlugin(
                    path=path,
                    code="io",
                    message=str(error),
                )
            )
            continue
        valid.append(_installed(path, manifest))
    return ScanResult(tuple(valid), tuple(invalid))


def list_installed(*, root: Path | None = None) -> tuple[InstalledPlugin, ...]:
    """Devolve só os plugins válidos."""
    return scan_installed(root=root).valid


def _check_path_lengths(
    target: Path,
    info: PackageInfo,
    limits: PackageLimits,
) -> None:
    for entry in info.entries:
        final = target.joinpath(*PurePosixPath(entry.name).parts)
        if _windows_length(str(final)) > limits.max_path_length:
            raise PackageError(
                "entry_unsafe",
                f"Caminho final passa de {limits.max_path_length} caracteres: "
                f"{entry.name}.",
            )


def _windows_length(value: str) -> int:
    return len(value.encode("utf-16-le")) // 2


def _check_entrypoint_exists(path: Path, manifest: PluginManifest) -> None:
    module, _function = entrypoint_parts(manifest.entrypoint)
    relative = path / "lib" / Path(*module.split("."))
    if (
        not relative.with_suffix(".py").is_file()
        and not (relative / "__init__.py").is_file()
    ):
        raise ManifestError(
            "entrypoint_missing",
            f"Entrypoint sem arquivo em {path.name}/lib: {manifest.entrypoint}.",
        )


def _installed(path: Path, manifest: PluginManifest) -> InstalledPlugin:
    return InstalledPlugin(
        id=manifest.id,
        name=manifest.name,
        version=manifest.version,
        api_version=manifest.api_version,
        path=path,
        data_dir=path / "data",
        manifest=manifest,
    )


def _check_dependencies(manifest: PluginManifest) -> None:
    for dependency in manifest.dependencies:
        try:
            metadata.version(dependency)
        except metadata.PackageNotFoundError as error:
            raise InstallError(
                "missing_dependency",
                f"Dependência ausente: {dependency}.",
            ) from error


def _ensure_space(staging: Path, required: int) -> None:
    free = shutil.disk_usage(staging).free
    if free < required + FREE_SPACE_MARGIN:
        raise InstallError(
            "no_space",
            f"Espaço insuficiente: {free} bytes livres, "
            f"{required + FREE_SPACE_MARGIN} necessários.",
        )


def _write_record(
    staging: Path,
    info: PackageInfo,
    digest: str,
    source: str,
) -> None:
    record = {
        "id": info.manifest.id,
        "version": info.manifest.version,
        "api_version": info.manifest.api_version,
        "sha256": digest,
        "archive_size": info.archive_size,
        "installed_at": datetime.now(UTC).isoformat(),
        "source": source,
    }
    (staging / "install.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _promote(staging: Path, target: Path) -> None:
    """Ponto único de promoção para permitir teste de falha atômica."""
    os.replace(staging, target)


def _cleanup_staging(base: Path) -> None:
    staging = base / STAGING_DIR
    if not staging.is_dir():
        return
    cutoff = time.time() - STAGING_MAX_AGE
    for path in staging.iterdir():
        try:
            if path.is_dir() and path.stat().st_mtime < cutoff:
                shutil.rmtree(path, ignore_errors=True)
        except OSError:
            continue
    _prune_staging(base)


def _prune_staging(base: Path) -> None:
    try:
        (base / STAGING_DIR).rmdir()
    except OSError:
        return


def _is_junction(path: Path) -> bool:
    checker = getattr(path, "is_junction", None)
    return bool(checker()) if checker is not None else False


def _remove_readonly(
    function: Callable[..., object],
    path: str,
    error: BaseException,
) -> None:
    if isinstance(error, PermissionError):
        os.chmod(path, stat.S_IWRITE)
        function(path)
        return
    raise error
