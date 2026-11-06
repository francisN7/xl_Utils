"""Carrega os cabeçalhos padrão empacotados ou o override por máquina.

O JSON que viaja no pacote é a fonte padrão. Um override opcional em
``%LOCALAPPDATA%/xl_utils/headers.json`` permite ajustar rótulos sem rebuild;
segredos e estado de login nunca moram aqui (ver ADR 0015).
"""

from __future__ import annotations

import json
import os
from importlib import resources
from pathlib import Path
from typing import Any

from xl_utils.core.tools.link import ConfigError, LinkConfig, SheetSpec
from xl_utils.shared.settings import APP_DIR

HEADERS_FILE = "headers.json"
_SHEET_NAMES = ("AGENDA", "PROCESSOS", "FINANCEIRO", "CLIENTES")


def override_path() -> Path:
    """Devolve ``%LOCALAPPDATA%/xl_utils/headers.json`` ou o equivalente em casa."""
    local = os.environ.get("LOCALAPPDATA")
    base = Path(local) / APP_DIR if local else Path.home() / f".{APP_DIR}"
    return base / HEADERS_FILE


def load_link_config(path: Path | None = None) -> LinkConfig:
    """Carrega um caminho explícito, o override local ou o JSON empacotado."""
    if path is not None:
        return _load_path(path)

    override = override_path()
    if override.exists():
        return _load_path(override)
    return load_packaged_config()


def load_packaged_config() -> LinkConfig:
    """Lê o ``headers.json`` que acompanha a instalação, sem tocar no disco do app."""
    resource = resources.files("xl_utils.configs").joinpath(HEADERS_FILE)
    try:
        raw = resource.read_text(encoding="utf-8")
    except OSError as error:
        raise ConfigError(
            f"Não foi possível ler {HEADERS_FILE} empacotado: {error}"
        ) from error
    return _parse(raw, HEADERS_FILE)


def _load_path(path: Path) -> LinkConfig:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ConfigError(f"Não foi possível ler {path}: {error}") from error
    return _parse(raw, path.name)


def _parse(raw: str, source: str) -> LinkConfig:
    try:
        data = json.loads(raw)
    except ValueError as error:
        raise ConfigError(f"{source}: JSON inválido: {error}") from error
    return _build(data, source)


def _build(data: Any, source: str) -> LinkConfig:
    if not isinstance(data, dict):
        raise ConfigError(f"{source}: esperado um objeto JSON.")

    sheets_raw = data.get("sheets")
    columns = data.get("columns")
    if not isinstance(sheets_raw, dict):
        raise ConfigError(f"{source}: falta o objeto 'sheets'.")
    if not isinstance(columns, dict):
        raise ConfigError(f"{source}: falta o objeto 'columns'.")

    sheets: dict[str, SheetSpec] = {}
    for name in _SHEET_NAMES:
        entry = sheets_raw.get(name)
        if not isinstance(entry, dict):
            raise ConfigError(f"{source}: falta a planilha {name}.")
        sheets[name] = _sheet_spec(name, entry, source)

    vincula = columns.get("vincula")
    vincula_nome = columns.get("vincula_nome")
    if not isinstance(vincula, str) or not vincula.strip():
        raise ConfigError(f"{source}: coluna 'vincula' ausente.")
    if not isinstance(vincula_nome, str) or not vincula_nome.strip():
        raise ConfigError(f"{source}: coluna 'vincula_nome' ausente.")

    return LinkConfig(
        sheets=sheets,
        vincula_column=vincula,
        vincula_nome_column=vincula_nome,
    )


def _sheet_spec(name: str, entry: dict[str, Any], source: str) -> SheetSpec:
    standard = entry.get("standard")
    fields = entry.get("fields")
    required = entry.get("required")
    separator = entry.get("description_separator", "\n")

    if not isinstance(standard, list) or not all(
        isinstance(value, str) and value.strip() for value in standard
    ):
        raise ConfigError(f"{source}: 'standard' inválido em {name}.")
    if not standard:
        raise ConfigError(f"{source}: 'standard' vazio em {name}.")
    if not isinstance(fields, dict) or not all(
        isinstance(key, str) and isinstance(value, str) and value.strip()
        for key, value in fields.items()
    ):
        raise ConfigError(f"{source}: 'fields' inválido em {name}.")
    if (
        not isinstance(required, list)
        or not required
        or not all(isinstance(value, str) for value in required)
    ):
        raise ConfigError(f"{source}: 'required' inválido em {name}.")
    missing = [key for key in required if key not in fields]
    if missing:
        raise ConfigError(
            f"{source}: campo obrigatório ausente em {name}: {', '.join(missing)}."
        )
    if not isinstance(separator, str):
        raise ConfigError(f"{source}: 'description_separator' inválido em {name}.")

    return SheetSpec(
        name=name,
        standard=tuple(standard),
        fields=dict(fields),
        required=tuple(required),
        description_separator=separator,
    )
