"""Pure spreadsheet cutting by a fixed number of rows."""

from collections.abc import Mapping

import pandas as pd


def split_frame(frame: pd.DataFrame, rows_per_file: int) -> list[pd.DataFrame]:
    """Split ``frame`` into sequential chunks of ``rows_per_file`` rows.

    The last chunk keeps the remainder. An empty frame yields one empty chunk,
    so the caller still has a file to save.
    """
    if rows_per_file <= 0:
        raise ValueError("O número de linhas por arquivo deve ser maior que zero.")

    if len(frame) == 0:
        return [frame]

    return [
        frame.iloc[start : start + rows_per_file]
        for start in range(0, len(frame), rows_per_file)
    ]


def split_workbook(
    sheets: Mapping[str, pd.DataFrame],
    rows_per_file: int,
) -> dict[str, list[pd.DataFrame]]:
    """Split every sheet, preserving the original sheet order."""
    return {name: split_frame(frame, rows_per_file) for name, frame in sheets.items()}
