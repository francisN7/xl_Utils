"""Merge the selected sheets of several files into one workbook."""

from collections.abc import Collection, Sequence
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from xl_utils.core.io import read_headers, save_workbook
from xl_utils.core.paths import default_output_dir
from xl_utils.core.tools.all_str import prepare_workbook
from xl_utils.core.tools.merge import ColumnGroup, ColumnRef, merge_sheets
from xl_utils.core.tools.sheets import filter_sheets

Source = tuple[Path, Collection[str] | None]


@dataclass(frozen=True, slots=True)
class MergeOutcome:
    """Result of one merge run."""

    sources: tuple[Path, ...]
    merged: pd.DataFrame
    output: Path
    sheets: int
    log: list[str]

    @property
    def rows(self) -> int:
        return len(self.merged)

    @property
    def columns(self) -> int:
        return len(self.merged.columns)


def inspect_columns(sources: Sequence[Source]) -> list[ColumnRef]:
    """Return the selected columns of every sheet, in reading order.

    The UI uses this to build the draggable column board. Files are read
    through their real format; the rows are not loaded for Excel and CSV.
    """
    refs: list[ColumnRef] = []
    for source, selected in sources:
        headers = filter_sheets(read_headers(source), selected)
        for sheet, names in headers.items():
            refs.extend(ColumnRef(source, sheet, name) for name in names)
    return refs


def run_merge(
    sources: Sequence[Source],
    groups: Sequence[ColumnGroup] | None = None,
) -> MergeOutcome:
    """Concatenate the selected sheets of ``sources`` into ``output/``."""
    if not sources:
        raise ValueError("Selecione ao menos um arquivo para mesclar.")

    loaded: list[tuple[Path, dict[str, pd.DataFrame]]] = []
    entries: list[tuple[Path, str, pd.DataFrame]] = []
    for source, selected in sources:
        sheets = filter_sheets(prepare_workbook(source), selected)
        loaded.append((source, sheets))
        entries.extend((source, name, frame) for name, frame in sheets.items())

    usable = sum(1 for _, _, frame in entries if not frame.empty)
    if usable == 0:
        raise ValueError("Nenhuma aba com dados para mesclar.")
    if usable < 2:
        raise ValueError(
            "Selecione ao menos duas abas — de arquivos diferentes ou do "
            "mesmo arquivo — para mesclar."
        )

    merged = merge_sheets(entries, groups)
    destination = default_output_dir(loaded[0][0]) / "Merge.xlsx"
    output = save_workbook({"Mesclado": merged}, destination)

    log: list[str] = []
    for source, sheets in loaded:
        if log:
            log.append("")
        columns: dict[str, None] = {}
        for frame in sheets.values():
            for name in frame.columns:
                columns.setdefault(str(name), None)
        log.extend(
            [
                f"Arquivo: {source.name}",
                f"Abas: {len(sheets)} ({', '.join(sheets)})",
                f"Linhas: {sum(len(frame) for frame in sheets.values())}",
                f"Colunas: {len(columns)}",
            ]
        )

    log.extend(
        [
            "",
            f"Abas mescladas: {usable}",
            f"Linhas mescladas: {len(merged)}",
            f"Colunas no resultado: {len(merged.columns)}",
            f"Saída: {output}",
        ]
    )

    return MergeOutcome(
        sources=tuple(source for source, _ in loaded),
        merged=merged,
        output=output,
        sheets=usable,
        log=log,
    )
