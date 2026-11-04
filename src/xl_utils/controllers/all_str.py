"""Run the text pipeline and save the result beside the source file."""

from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from xl_utils.core.io import save_workbook
from xl_utils.core.mime import resolve_suffix
from xl_utils.core.paths import default_output_dir
from xl_utils.core.tools.all_str import prepare_workbook
from xl_utils.core.tools.sheets import filter_sheets


@dataclass(frozen=True, slots=True)
class AllStrOutcome:
    """Result of one text-treatment run."""

    source: Path
    output: Path
    sheets: dict[str, pd.DataFrame]
    log: list[str]

    @property
    def rows(self) -> int:
        return sum(len(frame) for frame in self.sheets.values())


def run_all_str(
    source: Path,
    selected: Collection[str] | None = None,
) -> AllStrOutcome:
    """Read, clean and save the selected sheets of ``source`` into ``output/``."""
    sheets = filter_sheets(prepare_workbook(source), selected)
    destination = default_output_dir(source) / f"{source.stem}.xlsx"
    output = save_workbook(sheets, destination)

    log = [
        f"Arquivo: {source.name}",
        f"Tipo detectado: {resolve_suffix(source)}",
        f"Abas: {len(sheets)}",
        f"Linhas: {sum(len(frame) for frame in sheets.values())}",
        f"Saída: {output}",
    ]
    return AllStrOutcome(
        source=source,
        output=output,
        sheets=sheets,
        log=log,
    )
