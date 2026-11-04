"""Filesystem helpers for output paths."""

from pathlib import Path


def unique_path(directory: Path, stem: str, suffix: str = ".xlsx") -> Path:
    """Create ``directory`` and return a path that does not exist yet."""
    directory.mkdir(parents=True, exist_ok=True)
    candidate = directory / f"{stem}{suffix}"
    counter = 1
    while candidate.exists():
        candidate = directory / f"{stem}_{counter:03}{suffix}"
        counter += 1
    return candidate


def default_output_dir(source: Path, name: str = "output") -> Path:
    """Return the default output folder next to a source file."""
    return source.parent / name
