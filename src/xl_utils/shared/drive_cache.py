"""Cópia temporária das planilhas abertas do Drive, com o nome real.

O pipeline lê arquivos por caminho; para uma planilha do Drive, os bytes são
gravados em ``%LOCALAPPDATA%/xl_utils/drive/cache/<sessão>/`` com o nome que o
arquivo tem no Drive. A pasta é limpa no início do aplicativo, nunca no meio:
outra ferramenta pode estar usando um arquivo escolhido antes.
"""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from xl_utils.core.paths import safe_file_part, unique_path
from xl_utils.shared.accounts import default_root as drive_root

CACHE_DIR = "cache"
FALLBACK_STEM = "Planilha"
FALLBACK_SUFFIX = ".xlsx"


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


def store(directory: Path, name: str, data: bytes) -> Path:
    """Grava os bytes com o nome real, sem deixar sobrescrever outro arquivo."""
    path = Path(name)
    raw_stem = path.stem.strip(" .")
    stem = safe_file_part(raw_stem) if raw_stem else FALLBACK_STEM
    suffix = path.suffix.lower() or FALLBACK_SUFFIX
    target = unique_path(directory, stem, suffix)
    target.write_bytes(data)
    return target


def is_cached(path: Path) -> bool:
    """Diz se o caminho é uma cópia temporária vinda do Drive."""
    try:
        return path.resolve().is_relative_to(cache_root().resolve())
    except OSError:
        return False
