"""In-memory results and the write step that follows the user's choice."""

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from xl_utils.core.io import save_workbook


class SaveError(Exception):
    """Raised when the chosen destination cannot receive the workbook."""


@dataclass(frozen=True, slots=True)
class SaveItem:
    """One workbook kept in memory until the user chooses where to save it."""

    suggested_name: str
    sheets: dict[str, pd.DataFrame]
    output_dir: Path


def save_chosen(
    items: Sequence[SaveItem],
    destination: Path | None,
) -> list[Path] | None:
    """Save one item at the chosen file or many items inside the chosen folder.

    ``None`` means the user cancelled the native dialog: nothing is written.
    Existing files are never overwritten; the returned paths are the real ones.
    """
    items = list(items)
    if destination is None or not items:
        return None if destination is None else []

    if len(items) == 1:
        targets = [destination.with_suffix(".xlsx")]
    else:
        targets = [destination / item.suggested_name for item in items]
    return [
        save_item(item, target) for item, target in zip(items, targets, strict=True)
    ]


def save_to_output(items: Sequence[SaveItem]) -> list[Path]:
    """Save every item inside the ``output/`` folder of its own origin."""
    return [save_item(item, item.output_dir / item.suggested_name) for item in items]


def save_item(item: SaveItem, destination: Path) -> Path:
    """Write one item and return the real path, without overwriting."""
    target = destination.with_suffix(".xlsx")
    try:
        return save_workbook(item.sheets, target)
    except Exception as error:  # noqa: BLE001 - one typed failure for the UI
        raise SaveError(f"Não foi possível salvar {target.name}: {error}") from error
