"""Run the row cut and keep every part in memory for saving."""

from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from xl_utils.core.mime import resolve_suffix
from xl_utils.core.paths import default_output_dir
from xl_utils.core.save import SaveItem
from xl_utils.core.tools.all_str import prepare_workbook
from xl_utils.core.tools.cut import split_workbook
from xl_utils.core.tools.sheets import filter_sheets
from xl_utils.shared.log import RunLog

_INVALID_FILE_CHARS = frozenset('<>:"/\\|?*')
_MAX_FILE_PART = 80


@dataclass(frozen=True, slots=True)
class CutOutcome:
    """Result of one row-cut run."""

    source: Path
    items: list[SaveItem]
    parts: dict[str, list[pd.DataFrame]]
    preview: dict[str, pd.DataFrame]
    log: RunLog

    @property
    def files(self) -> int:
        return len(self.items)

    @property
    def suggested_names(self) -> list[str]:
        return [item.suggested_name for item in self.items]

    @property
    def rows(self) -> int:
        return sum(len(frame) for frames in self.parts.values() for frame in frames)


def run_cut(
    source: Path,
    rows_per_file: int,
    selected: Collection[str] | None = None,
) -> CutOutcome:
    """Cut the selected sheets of ``source``, without writing anything."""
    sheets = filter_sheets(prepare_workbook(source), selected)
    parts = split_workbook(sheets, rows_per_file)
    output_dir = default_output_dir(source)
    multiple_sheets = len(parts) > 1
    items: list[SaveItem] = []

    for sheet_name, frames in parts.items():
        for number, frame in enumerate(frames, start=1):
            if multiple_sheets:
                base = (
                    f"{source.stem}_{safe_file_part(sheet_name)}_Recorte_{number:03d}"
                )
            else:
                base = f"{source.stem}_Recorte_{number:03d}"
            items.append(
                SaveItem(
                    suggested_name=f"{base}.xlsx",
                    sheets={sheet_name: frame},
                    output_dir=output_dir,
                )
            )

    first_sheet = next(iter(parts), "")
    preview = {first_sheet: parts[first_sheet][0]} if first_sheet else {}
    total_rows = sum(len(frame) for frames in parts.values() for frame in frames)
    log = (
        RunLog()
        .info(f"Arquivo: {source.name}")
        .info(f"Tipo detectado: {resolve_suffix(source)}")
        .info(f"Abas: {len(parts)}")
        .info(f"Linhas: {total_rows}")
        .info(f"Linhas por arquivo: {rows_per_file}")
        .success(f"Arquivos prontos: {len(items)}")
    )
    log.extend(f"Pronto para salvar: {item.suggested_name}" for item in items)

    return CutOutcome(
        source=source,
        items=items,
        parts=parts,
        preview=preview,
        log=log,
    )


def safe_file_part(value: str) -> str:
    """Make a sheet name safe for use inside a Windows file name."""
    cleaned = "".join(
        "_" if char in _INVALID_FILE_CHARS or ord(char) < 32 else char for char in value
    ).strip(" .")
    return (cleaned or "Aba")[:_MAX_FILE_PART]
