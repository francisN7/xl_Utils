"""Contrato puro de plugins: manifesto, pacote e empacotamento."""

from xl_utils.core.plugins.errors import (
    InstallError,
    ManifestError,
    PackageError,
    PluginError,
)
from xl_utils.core.plugins.manifest import (
    API_VERSION,
    SUPPORTED_API_VERSIONS,
    InputSpec,
    OptionSpec,
    Permissions,
    PluginManifest,
    UiSpec,
    parse_manifest,
    validate_id,
)
from xl_utils.core.plugins.package import (
    DEFAULT_LIMITS,
    PackageInfo,
    PackageLimits,
    build_package,
    extract_package,
    inspect_package,
    sha256_file,
    sidecar_path,
    verify_sidecar,
    write_sidecar,
)

__all__ = [
    "API_VERSION",
    "DEFAULT_LIMITS",
    "SUPPORTED_API_VERSIONS",
    "InputSpec",
    "InstallError",
    "ManifestError",
    "OptionSpec",
    "PackageError",
    "PackageInfo",
    "PackageLimits",
    "Permissions",
    "PluginError",
    "PluginManifest",
    "UiSpec",
    "build_package",
    "extract_package",
    "inspect_package",
    "parse_manifest",
    "sha256_file",
    "sidecar_path",
    "validate_id",
    "verify_sidecar",
    "write_sidecar",
]
