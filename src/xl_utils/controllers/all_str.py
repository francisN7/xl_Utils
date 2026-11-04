"""Run the text pipeline and keep the result in memory for saving."""

from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from xl_utils.core.mime import resolve_suffix
from xl_utils.core.paths import default_output_dir
from xl_utils.core.save import SaveItem
from xl_utils.core.tools.all_str import prepare_workbook
from xl_utils.core.tools.sheets import filter_sheets
from xl_utils.shared.log import RunLog


@dataclass(frozen=True, slots=True)
class AllStrOutcome:
    """Result of one text-treatment run."""

    source: Path
    item: SaveItem
    log: RunLog

    @property
    def sheets(self) -> dict[str, pd.DataFrame]:
        return self.item.sheets

    @property
    def suggested_name(self) -> str:
        return self.item.suggested_name

    @property
    def rows(self) -> int:
        return sum(len(frame) for frame in self.sheets.values())


def run_all_str(
    source: Path,
    selected: Collection[str] | None = None,
) -> AllStrOutcome:
    """Read and clean the selected sheets, without writing anything."""
    sheets = filter_sheets(prepare_workbook(source), selected)
    name = f"{source.stem}.xlsx"
    item = SaveItem(
        suggested_name=name,
        sheets=sheets,
        output_dir=default_output_dir(source),
    )

    log = (
        RunLog()
        .info(f"Arquivo: {source.name}")
        .info(f"Tipo detectado: {resolve_suffix(source)}")
        .info(f"Abas: {len(sheets)}")
        .info(f"Linhas: {sum(len(frame) for frame in sheets.values())}")
        .success(f"Pronto para salvar: {name}")
    )
    return AllStrOutcome(source=source, item=item, log=log)
