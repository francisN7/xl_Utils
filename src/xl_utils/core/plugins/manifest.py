"""Leitura e validação do ``plugin.toml``.

Entrada: bytes ou texto do manifesto.
Saída: ``PluginManifest`` tipado, sem importar código do plugin.
Erros: ``ManifestError`` com código estável.
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from typing import Any, Literal

from xl_utils.core.plugins.errors import ManifestError

API_VERSION = 1
SUPPORTED_API_VERSIONS = frozenset({API_VERSION})
MAX_MANIFEST_BYTES = 256 * 1024
MAX_OPTIONS = 20
MAX_INPUTS = 8
MAX_AUTHORS = 10
MAX_DEPENDENCIES = 20
MAX_TEXT_LENGTH = 500

FilesystemAccess = Literal["none", "read", "write"]
OptionKind = Literal["text", "int", "bool", "choice"]

_ID_RE = re.compile(r"^[a-z0-9](?:[a-z0-9._-]{1,62})[a-z0-9]$")
_SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
_ENTRYPOINT_RE = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*:"
    r"[A-Za-z_][A-Za-z0-9_]*$"
)
_KEY_RE = re.compile(r"^[a-z][a-z0-9_]{0,31}$")
_DIST_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

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

_PLUGIN_KEYS = frozenset(
    {
        "authors",
        "api_version",
        "dependencies",
        "description",
        "entrypoint",
        "homepage",
        "id",
        "license",
        "min_app_version",
        "name",
        "version",
    }
)
_TOP_KEYS = frozenset({"options", "permissions", "plugin", "ui"})
_PERMISSION_KEYS = frozenset({"filesystem", "network", "subprocess"})
_UI_KEYS = frozenset({"default_all_sheets", "inputs", "multiple_files", "note"})
_INPUT_KEYS = frozenset({"key", "label", "required"})
_OPTION_KEYS = frozenset(
    {"choices", "default", "help", "key", "label", "max", "min", "type"}
)


@dataclass(frozen=True, slots=True)
class OptionSpec:
    """Uma opção declarada na página da ferramenta."""

    key: str
    label: str
    kind: OptionKind
    default: str | int | bool
    choices: tuple[str, ...] = ()
    help: str = ""
    min: int | None = None
    max: int | None = None


@dataclass(frozen=True, slots=True)
class InputSpec:
    """Um slot nomeado de arquivo, como AGENDA ou FINANCEIRO."""

    key: str
    label: str
    required: bool = True


@dataclass(frozen=True, slots=True)
class Permissions:
    """Permissões declarativas; o host não as aplica como sandbox."""

    network: bool = False
    filesystem: FilesystemAccess = "none"
    subprocess: bool = False


@dataclass(frozen=True, slots=True)
class UiSpec:
    """Como o host monta a página declarativa."""

    multiple_files: bool = False
    default_all_sheets: bool = False
    note: str = ""
    inputs: tuple[InputSpec, ...] = ()


@dataclass(frozen=True, slots=True)
class PluginManifest:
    """Manifesto validado de um plugin."""

    id: str
    name: str
    version: str
    api_version: int
    entrypoint: str
    description: str
    authors: tuple[str, ...] = ()
    min_app_version: str | None = None
    dependencies: tuple[str, ...] = ()
    license: str = ""
    homepage: str = ""
    permissions: Permissions = field(default_factory=Permissions)
    ui: UiSpec = field(default_factory=UiSpec)
    options: tuple[OptionSpec, ...] = ()


def validate_id(value: str, *, source: str = "plugin.toml") -> str:
    """Valida o ID que também vira nome de pasta; devolve o próprio valor."""
    if not isinstance(value, str) or not _ID_RE.fullmatch(value):
        raise ManifestError(
            "invalid_id",
            f"{source}: id inválido: use autor.ferramenta em minúsculas.",
        )
    if ".." in value:
        raise ManifestError("invalid_id", f"{source}: id não pode conter '..'.")
    if value.casefold().split(".", 1)[0] in _WINDOWS_RESERVED:
        raise ManifestError(
            "invalid_id",
            f"{source}: id usa um nome reservado do Windows: {value}.",
        )
    return value


def entrypoint_parts(value: str) -> tuple[str, str]:
    """Separa ``modulo:funcao`` em módulo e função."""
    module, function = value.split(":", 1)
    return module, function


def parse_manifest(
    raw: str | bytes,
    *,
    source: str = "plugin.toml",
    app_version: str | None = None,
) -> PluginManifest:
    """Valida o TOML e devolve o manifesto tipado."""
    if isinstance(raw, bytes):
        if len(raw) > MAX_MANIFEST_BYTES:
            raise ManifestError(
                "manifest_too_large",
                f"{source}: manifesto maior que {MAX_MANIFEST_BYTES} bytes.",
            )
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ManifestError(
                "manifest_invalid",
                f"{source}: manifesto não é UTF-8: {error}",
            ) from error
    else:
        text = raw
        if len(text) > MAX_MANIFEST_BYTES:
            raise ManifestError(
                "manifest_too_large",
                f"{source}: manifesto maior que {MAX_MANIFEST_BYTES} bytes.",
            )

    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise ManifestError(
            "manifest_invalid",
            f"{source}: TOML inválido: {error}",
        ) from error
    if not isinstance(data, dict):
        raise ManifestError("manifest_invalid", f"{source}: raiz não é tabela.")
    return _build(data, source, app_version)


def _build(
    data: dict[str, Any],
    source: str,
    app_version: str | None,
) -> PluginManifest:
    _check_keys(data, _TOP_KEYS, "manifesto", source)
    plugin = _table(data.get("plugin"), "[plugin]", source, required=True)

    _check_keys(plugin, _PLUGIN_KEYS, "[plugin]", source)
    plugin_id = validate_id(
        _required_text(plugin, "id", source, max_len=64),
        source=source,
    )
    name = _required_text(plugin, "name", source, max_len=80)
    version = _required_text(plugin, "version", source, max_len=20)
    parse_semver(version, field="version", source=source)

    api_raw = plugin.get("api_version")
    if type(api_raw) is not int:
        raise ManifestError(
            "manifest_invalid",
            f"{source}: 'api_version' deve ser inteiro.",
        )
    if api_raw not in SUPPORTED_API_VERSIONS:
        raise ManifestError(
            "unsupported_api",
            f"{source}: api_version {api_raw} não é suportado; "
            f"aceito: {sorted(SUPPORTED_API_VERSIONS)}.",
        )

    entrypoint = _required_text(plugin, "entrypoint", source, max_len=200)
    if not _ENTRYPOINT_RE.fullmatch(entrypoint):
        raise ManifestError(
            "manifest_invalid",
            f"{source}: 'entrypoint' deve ser modulo:funcao.",
        )
    description = _required_text(plugin, "description", source, max_len=MAX_TEXT_LENGTH)
    authors = _text_list(
        plugin,
        "authors",
        source,
        section="[plugin]",
        max_items=MAX_AUTHORS,
        max_len=80,
    )
    dependencies = _dependency_list(plugin, source)
    license_text = _optional_text(plugin, "license", source, max_len=40)
    homepage = _optional_text(plugin, "homepage", source, max_len=200)
    if homepage and not homepage.startswith(("https://", "http://")):
        raise ManifestError(
            "manifest_invalid",
            f"{source}: 'homepage' deve começar com http(s)://.",
        )

    min_app_version = _optional_text(
        plugin,
        "min_app_version",
        source,
        max_len=20,
    )
    if min_app_version:
        minimum = parse_semver(
            min_app_version,
            field="min_app_version",
            source=source,
        )
        if app_version is not None:
            current = parse_semver(app_version, field="app_version", source=source)
            if minimum > current:
                raise ManifestError(
                    "app_too_old",
                    f"{source}: exige app {min_app_version} ou mais novo "
                    f"(atual {app_version}).",
                )

    permissions = _permissions(data.get("permissions"), source)
    ui = _ui(data.get("ui"), source)
    options = _options(data.get("options"), source)

    return PluginManifest(
        id=plugin_id,
        name=name,
        version=version,
        api_version=api_raw,
        entrypoint=entrypoint,
        description=description,
        authors=tuple(authors),
        min_app_version=min_app_version or None,
        dependencies=tuple(dependencies),
        license=license_text,
        homepage=homepage,
        permissions=permissions,
        ui=ui,
        options=tuple(options),
    )


def _permissions(raw: Any, source: str) -> Permissions:
    if raw is None:
        return Permissions()
    permissions = _table(raw, "[permissions]", source, required=False)
    _check_keys(permissions, _PERMISSION_KEYS, "[permissions]", source)
    network = _bool(permissions, "network", source, default=False)
    subprocess = _bool(permissions, "subprocess", source, default=False)
    filesystem = permissions.get("filesystem", "none")
    if filesystem not in ("none", "read", "write"):
        raise ManifestError(
            "manifest_invalid",
            f"{source}: 'filesystem' deve ser none, read ou write.",
        )
    return Permissions(
        network=network,
        filesystem=filesystem,
        subprocess=subprocess,
    )


def _ui(raw: Any, source: str) -> UiSpec:
    if raw is None:
        return UiSpec()
    ui = _table(raw, "[ui]", source, required=False)
    _check_keys(ui, _UI_KEYS, "[ui]", source)
    multiple_files = _bool(ui, "multiple_files", source, default=False)
    default_all_sheets = _bool(ui, "default_all_sheets", source, default=False)
    note = _optional_text(ui, "note", source, max_len=200)

    inputs_raw = ui.get("inputs", [])
    if not isinstance(inputs_raw, list):
        raise ManifestError("manifest_invalid", f"{source}: 'inputs' deve ser lista.")
    if len(inputs_raw) > MAX_INPUTS:
        raise ManifestError(
            "manifest_invalid",
            f"{source}: no máximo {MAX_INPUTS} entradas nomeadas.",
        )
    inputs: list[InputSpec] = []
    seen: set[str] = set()
    for index, item in enumerate(inputs_raw):
        entry = _table(item, f"[[ui.inputs]][{index}]", source, required=True)
        _check_keys(entry, _INPUT_KEYS, f"[[ui.inputs]][{index}]", source)
        key = _key(entry, "key", source, f"[[ui.inputs]][{index}]")
        if key in seen:
            raise ManifestError(
                "duplicate_option",
                f"{source}: chave de entrada repetida: {key}.",
            )
        seen.add(key)
        label = _required_text(entry, "label", source, max_len=40)
        inputs.append(
            InputSpec(
                key=key,
                label=label,
                required=_bool(entry, "required", source, default=True),
            )
        )
    if inputs and multiple_files:
        raise ManifestError(
            "manifest_invalid",
            f"{source}: use [[ui.inputs]] ou multiple_files, não os dois.",
        )
    return UiSpec(
        multiple_files=multiple_files,
        default_all_sheets=default_all_sheets,
        note=note,
        inputs=tuple(inputs),
    )


def _options(raw: Any, source: str) -> list[OptionSpec]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ManifestError("manifest_invalid", f"{source}: 'options' deve ser lista.")
    if len(raw) > MAX_OPTIONS:
        raise ManifestError(
            "manifest_invalid",
            f"{source}: no máximo {MAX_OPTIONS} opções.",
        )
    options: list[OptionSpec] = []
    seen: set[str] = set()
    for index, item in enumerate(raw):
        entry = _table(item, f"[[options]][{index}]", source, required=True)
        _check_keys(entry, _OPTION_KEYS, f"[[options]][{index}]", source)
        key = _key(entry, "key", source, f"[[options]][{index}]")
        if key in seen:
            raise ManifestError(
                "duplicate_option",
                f"{source}: chave de opção repetida: {key}.",
            )
        seen.add(key)
        label = _required_text(entry, "label", source, max_len=60)
        kind = _required_text(entry, "type", source, max_len=10)
        if kind not in ("text", "int", "bool", "choice"):
            raise ManifestError(
                "manifest_invalid",
                f"{source}: tipo desconhecido em '{key}': {kind}.",
            )
        help_text = _optional_text(entry, "help", source, max_len=200)

        if kind == "choice":
            choices = _choices(entry, source, key)
            if "default" not in entry:
                raise ManifestError(
                    "manifest_invalid",
                    f"{source}: '{key}' do tipo choice exige default.",
                )
            default = entry["default"]
            if not isinstance(default, str) or default not in choices:
                raise ManifestError(
                    "manifest_invalid",
                    f"{source}: default de '{key}' não está em choices.",
                )
            if "min" in entry or "max" in entry:
                raise ManifestError(
                    "manifest_invalid",
                    f"{source}: min/max só valem para int.",
                )
            options.append(
                OptionSpec(
                    key=key,
                    label=label,
                    kind="choice",
                    default=default,
                    choices=choices,
                    help=help_text,
                )
            )
            continue

        if "choices" in entry:
            raise ManifestError(
                "manifest_invalid",
                f"{source}: choices só vale para choice.",
            )

        if kind == "text":
            default = _option_text_default(entry, source, key)
            options.append(
                OptionSpec(
                    key=key,
                    label=label,
                    kind="text",
                    default=default,
                    help=help_text,
                )
            )
            continue

        if kind == "bool":
            default_bool = entry.get("default", False)
            if type(default_bool) is not bool:
                raise ManifestError(
                    "manifest_invalid",
                    f"{source}: default de '{key}' deve ser booleano.",
                )
            if "min" in entry or "max" in entry:
                raise ManifestError(
                    "manifest_invalid",
                    f"{source}: min/max só valem para int.",
                )
            options.append(
                OptionSpec(
                    key=key,
                    label=label,
                    kind="bool",
                    default=default_bool,
                    help=help_text,
                )
            )
            continue

        minimum, maximum = _option_bounds(entry, source, key)
        default_int = entry.get("default", 0)
        if type(default_int) is not int:
            raise ManifestError(
                "manifest_invalid",
                f"{source}: default de '{key}' deve ser inteiro.",
            )
        if minimum is not None and default_int < minimum:
            raise ManifestError(
                "manifest_invalid",
                f"{source}: default de '{key}' abaixo do mínimo.",
            )
        if maximum is not None and default_int > maximum:
            raise ManifestError(
                "manifest_invalid",
                f"{source}: default de '{key}' acima do máximo.",
            )
        options.append(
            OptionSpec(
                key=key,
                label=label,
                kind="int",
                default=default_int,
                help=help_text,
                min=minimum,
                max=maximum,
            )
        )
    return options


def _choices(entry: dict[str, Any], source: str, key: str) -> tuple[str, ...]:
    raw = entry.get("choices")
    if not isinstance(raw, list) or not 2 <= len(raw) <= 50:
        raise ManifestError(
            "manifest_invalid",
            f"{source}: '{key}' exige de 2 a 50 choices.",
        )
    choices: list[str] = []
    for item in raw:
        if not isinstance(item, str) or not 1 <= len(item) <= 60:
            raise ManifestError(
                "manifest_invalid",
                f"{source}: choice inválido em '{key}'.",
            )
        if item in choices:
            raise ManifestError(
                "manifest_invalid",
                f"{source}: choice repetido em '{key}': {item}.",
            )
        choices.append(item)
    return tuple(choices)


def _option_text_default(entry: dict[str, Any], source: str, key: str) -> str:
    default = entry.get("default", "")
    if not isinstance(default, str):
        raise ManifestError(
            "manifest_invalid",
            f"{source}: default de '{key}' deve ser texto.",
        )
    if len(default) > MAX_TEXT_LENGTH:
        raise ManifestError(
            "manifest_invalid",
            f"{source}: default de '{key}' passa de {MAX_TEXT_LENGTH} caracteres.",
        )
    return default


def _option_bounds(
    entry: dict[str, Any],
    source: str,
    key: str,
) -> tuple[int | None, int | None]:
    minimum = entry.get("min")
    maximum = entry.get("max")
    if minimum is not None and type(minimum) is not int:
        raise ManifestError(
            "manifest_invalid",
            f"{source}: min de '{key}' deve ser inteiro.",
        )
    if maximum is not None and type(maximum) is not int:
        raise ManifestError(
            "manifest_invalid",
            f"{source}: max de '{key}' deve ser inteiro.",
        )
    if minimum is not None and maximum is not None and minimum > maximum:
        raise ManifestError(
            "manifest_invalid",
            f"{source}: min de '{key}' maior que max.",
        )
    return minimum, maximum


def _dependency_list(plugin: dict[str, Any], source: str) -> list[str]:
    raw = plugin.get("dependencies", [])
    if not isinstance(raw, list):
        raise ManifestError(
            "manifest_invalid",
            f"{source}: 'dependencies' deve ser lista.",
        )
    if len(raw) > MAX_DEPENDENCIES:
        raise ManifestError(
            "manifest_invalid",
            f"{source}: no máximo {MAX_DEPENDENCIES} dependências.",
        )
    dependencies: list[str] = []
    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, str) or not _DIST_RE.fullmatch(item):
            raise ManifestError(
                "manifest_invalid",
                f"{source}: dependência inválida: {item!r}.",
            )
        folded = item.casefold()
        if folded in seen:
            raise ManifestError(
                "manifest_invalid",
                f"{source}: dependência repetida: {item}.",
            )
        seen.add(folded)
        dependencies.append(item)
    return dependencies


def _text_list(
    table: dict[str, Any],
    key: str,
    source: str,
    *,
    section: str,
    max_items: int,
    max_len: int,
) -> list[str]:
    raw = table.get(key, [])
    if not isinstance(raw, list):
        raise ManifestError(
            "manifest_invalid",
            f"{source}: '{key}' em {section} deve ser lista.",
        )
    if len(raw) > max_items:
        raise ManifestError(
            "manifest_invalid",
            f"{source}: no máximo {max_items} itens em '{key}'.",
        )
    values: list[str] = []
    for item in raw:
        if not isinstance(item, str) or not 1 <= len(item) <= max_len:
            raise ManifestError(
                "manifest_invalid",
                f"{source}: item inválido em '{key}'.",
            )
        if any(ord(char) < 32 for char in item):
            raise ManifestError(
                "manifest_invalid",
                f"{source}: controle em '{key}'.",
            )
        values.append(item)
    return values


def _table(
    raw: Any,
    section: str,
    source: str,
    *,
    required: bool,
) -> dict[str, Any]:
    if raw is None:
        if required:
            raise ManifestError(
                "manifest_invalid",
                f"{source}: falta a tabela {section}.",
            )
        return {}
    if not isinstance(raw, dict):
        raise ManifestError(
            "manifest_invalid",
            f"{source}: {section} deve ser tabela.",
        )
    return raw


def _check_keys(
    table: dict[str, Any],
    allowed: frozenset[str],
    section: str,
    source: str,
) -> None:
    unknown = sorted(set(table) - allowed)
    if unknown:
        raise ManifestError(
            "manifest_invalid",
            f"{source}: chave desconhecida em {section}: {', '.join(unknown)}.",
        )


def _required_text(
    table: dict[str, Any],
    key: str,
    source: str,
    *,
    max_len: int,
) -> str:
    value = _optional_text(table, key, source, max_len=max_len)
    if not value:
        raise ManifestError(
            "manifest_invalid",
            f"{source}: campo '{key}' obrigatório.",
        )
    return value


def _optional_text(
    table: dict[str, Any],
    key: str,
    source: str,
    *,
    max_len: int,
) -> str:
    if key not in table:
        return ""
    value = table[key]
    if not isinstance(value, str):
        raise ManifestError(
            "manifest_invalid",
            f"{source}: '{key}' deve ser texto.",
        )
    if len(value) > max_len:
        raise ManifestError(
            "manifest_invalid",
            f"{source}: '{key}' passa de {max_len} caracteres.",
        )
    if any(ord(char) < 32 for char in value):
        raise ManifestError(
            "manifest_invalid",
            f"{source}: '{key}' contém caractere de controle.",
        )
    return value


def _key(table: dict[str, Any], key: str, source: str, section: str) -> str:
    value = _required_text(table, key, source, max_len=32)
    if not _KEY_RE.fullmatch(value):
        raise ManifestError(
            "manifest_invalid",
            f"{source}: chave inválida em {section}: {value!r}.",
        )
    return value


def _bool(
    table: dict[str, Any],
    key: str,
    source: str,
    *,
    default: bool,
) -> bool:
    value = table.get(key, default)
    if type(value) is not bool:
        raise ManifestError(
            "manifest_invalid",
            f"{source}: '{key}' deve ser booleano.",
        )
    return value


def parse_semver(
    value: str,
    *,
    field: str,
    source: str,
) -> tuple[int, int, int]:
    """Converte ``X.Y.Z`` em tupla comparável."""
    match = _SEMVER_RE.fullmatch(value)
    if match is None:
        raise ManifestError(
            "manifest_invalid",
            f"{source}: '{field}' deve ser SemVer X.Y.Z.",
        )
    return tuple(int(part) for part in match.groups())
