"""Cópia temporária das planilhas abertas do Drive, com o nome real.

O pipeline lê arquivos por caminho; para uma planilha do Drive, os bytes são
gravados em ``%LOCALAPPDATA%/xl_utils/drive/cache/<sessão>/`` com o nome que o
arquivo tem no Drive. A pasta é limpa no início do aplicativo, nunca no meio:
outra ferramenta pode estar usando um arquivo escolhido antes.
"""

from __future__ import annotations

import json
import os
import shutil
import uuid
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from xl_utils.core.paths import safe_file_part, unique_path
from xl_utils.shared.accounts import default_root as drive_root

CACHE_DIR = "cache"
FALLBACK_STEM = "Planilha"
FALLBACK_SUFFIX = ".xlsx"
ORIGIN_FILE = "_origins.json"


@dataclass(frozen=True, slots=True)
class DriveOrigin:
    """De onde a cópia local veio: arquivo, pasta e conta no Drive."""

    file_id: str
    name: str
    mime_type: str = ""
    parent: str = ""
    account: str = ""


def cache_root() -> Path:
    """Devolve ``%LOCALAPPDATA%/xl_utils/drive/cache`` ou o equivalente."""
    return drive_root() / CACHE_DIR


def reset(root: Path | None = None) -> None:
    """Apaga todas as cópias temporárias; chamado na abertura do app."""
    shutil.rmtree(root or cache_root(), ignore_errors=True)


def new_session(root: Path | None = None) -> Path:
    """Cria uma pasta exclusiva para os arquivos de uma escolha no Drive."""
    directory = (root or cache_root()) / uuid.uuid4().hex[:12]
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def store(
    directory: Path,
    name: str,
    data: bytes,
    *,
    origin: DriveOrigin | None = None,
) -> Path:
    """Grava os bytes com o nome real, sem deixar sobrescrever outro arquivo.

    Quando ``origin`` é informado, o arquivo passa a ter procedência conhecida:
    a próxima gravação consegue voltar para a pasta do arquivo original.
    """
    path = Path(name)
    raw_stem = path.stem.strip(" .")
    stem = safe_file_part(raw_stem) if raw_stem else FALLBACK_STEM
    suffix = path.suffix.lower() or FALLBACK_SUFFIX
    target = unique_path(directory, stem, suffix)
    target.write_bytes(data)
    if origin is not None:
        _remember(directory, target.name, origin)
    return target


def origin(path: Path) -> DriveOrigin | None:
    """Devolve a procedência da cópia local, se ela veio do Drive."""
    raw = _read(path.parent).get(path.name)
    if not isinstance(raw, dict):
        return None
    file_id = raw.get("file_id")
    if not isinstance(file_id, str) or not file_id:
        return None
    return DriveOrigin(
        file_id=file_id,
        name=_text(raw.get("name")),
        mime_type=_text(raw.get("mime_type")),
        parent=_text(raw.get("parent")),
        account=_text(raw.get("account")),
    )


def origins(paths: Iterable[Path]) -> list[DriveOrigin]:
    """Devolve as procedências conhecidas, sem repetir o mesmo arquivo."""
    found: list[DriveOrigin] = []
    seen: set[str] = set()
    for path in paths:
        item = origin(Path(path))
        if item is None or item.file_id in seen:
            continue
        seen.add(item.file_id)
        found.append(item)
    return found


def parents(paths: Iterable[Path]) -> tuple[str, ...]:
    """Devolve as pastas de origem distintas, na ordem em que aparecem."""
    folders: list[str] = []
    for item in origins(paths):
        if item.parent and item.parent not in folders:
            folders.append(item.parent)
    return tuple(folders)


def _remember(directory: Path, name: str, origin: DriveOrigin) -> None:
    data = _read(directory)
    data[name] = {
        "file_id": origin.file_id,
        "name": origin.name,
        "mime_type": origin.mime_type,
        "parent": origin.parent,
        "account": origin.account,
    }
    target = directory / ORIGIN_FILE
    temporary = target.with_name(f"{target.name}.tmp")
    temporary.write_text(
        json.dumps({"files": data}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.replace(temporary, target)


def _read(directory: Path) -> dict[str, Any]:
    try:
        data = json.loads((directory / ORIGIN_FILE).read_text(encoding="utf-8"))
    except OSError, ValueError:
        return {}
    files = data.get("files") if isinstance(data, dict) else None
    return files if isinstance(files, dict) else {}


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def is_cached(path: Path) -> bool:
    """Diz se o caminho é uma cópia temporária vinda do Drive."""
    try:
        return path.resolve().is_relative_to(cache_root().resolve())
    except OSError:
        return False
