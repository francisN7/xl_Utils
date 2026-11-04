"""Pure spreadsheet merge: concatenate sheets and label each row's origin."""

from collections.abc import Iterable, Mapping
from pathlib import Path

import pandas as pd

SheetEntry = tuple[Path, str, pd.DataFrame]


def merge_sheets(
    entries: Iterable[SheetEntry],
    column_map: Mapping[str, str] | None = None,
) -> pd.DataFrame:
    """Concatenate ``entries`` in order, adding an ``ORIGEM`` column first.

    Each entry is ``(source, sheet_name, frame)``. Empty frames are skipped;
    rows are never dropped. ``column_map`` renames source columns to canonical
    names before the concatenation, so columns with different headers can line
    up. Missing columns become ``NaN`` and new columns are appended at the end,
    in first-seen order. A source column already named ``ORIGEM`` is renamed so
    the generated label keeps its name.
    """
    mapping = dict(column_map or {})
    frames: list[pd.DataFrame] = []

    for source, sheet_name, frame in entries:
        if frame.empty:
            continue

        renamed = frame.copy(deep=False)
        renamed.columns = _mapped_columns(renamed.columns, mapping)
        renamed.insert(
            0,
            "ORIGEM",
            [
                f"{source.name} - {sheet_name} - {row}"
                for row in range(1, len(renamed) + 1)
            ],
        )
        frames.append(renamed)

    if not frames:
        raise ValueError("Nenhuma aba com dados para mesclar.")

    return pd.concat(frames, ignore_index=True, sort=False)


def _mapped_columns(
    columns: Iterable[object],
    mapping: Mapping[str, str],
) -> list[str]:
    """Apply the canonical names, protecting the generated ``ORIGEM`` column."""
    names = [mapping.get(str(column), str(column)) for column in columns]
    if "ORIGEM" not in names:
        return names

    reserved = {"ORIGEM"}
    protected: list[str] = []
    for name in names:
        if name == "ORIGEM":
            name = _free_name("ORIGEM_original", reserved)
        reserved.add(name)
        protected.append(name)
    return protected


def _free_name(base: str, reserved: set[str]) -> str:
    candidate = base
    counter = 2
    while candidate in reserved:
        candidate = f"{base}_{counter}"
        counter += 1
    return candidate
