"""Run CNJ extraction and keep the unique list in memory for saving."""

from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from xl_utils.core.mime import resolve_suffix
from xl_utils.core.paths import default_output_dir
from xl_utils.core.save import SaveItem
from xl_utils.core.tools.all_str import prepare_workbook
from xl_utils.core.tools.cnj import collect_cnjs, count_cnjs
from xl_utils.core.tools.sheets import filter_sheets
from xl_utils.shared.log import RunLog


@dataclass(frozen=True, slots=True)
class CnjOutcome:
    """Result of one CNJ extraction run."""

    source: Path
    item: SaveItem
    cnjs: list[str]
    found: int
    log: RunLog

    @property
    def suggested_name(self) -> str:
        return self.item.suggested_name

    @property
    def sheets(self) -> dict[str, pd.DataFrame]:
        return self.item.sheets

    @property
    def duplicates(self) -> int:
        return self.found - len(self.cnjs)


def run_cnj(
    source: Path,
    selected: Collection[str] | None = None,
) -> CnjOutcome:
    """Extract CNJs from the selected sheets, without writing anything."""
    sheets = filter_sheets(prepare_workbook(source), selected)
    cnjs = collect_cnjs(sheets)
    found = count_cnjs(sheets)

    name = f"{source.stem} lista cnj.xlsx"
    item = SaveItem(
        suggested_name=name,
        sheets={"PROCESSOS": pd.DataFrame({"PROCESSOS": cnjs})},
        output_dir=default_output_dir(source),
    )

    log = (
        RunLog()
        .info(f"Arquivo: {source.name}")
        .info(f"Tipo detectado: {resolve_suffix(source)}")
        .info(f"Abas lidas: {len(sheets)} ({', '.join(sheets)})")
        .info(f"CNJs encontrados: {found}")
        .info(f"Duplicados removidos: {found - len(cnjs)}")
        .info(f"CNJs únicos: {len(cnjs)}")
        .success(f"Pronto para salvar: {name}")
    )
    return CnjOutcome(
        source=source,
        item=item,
        cnjs=cnjs,
        found=found,
        log=log,
    )
