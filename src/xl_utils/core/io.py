"""Reading and writing spreadsheets as plain pandas objects."""

from collections.abc import Mapping
from pathlib import Path

import pandas as pd

from xl_utils.core.mime import resolve_suffix
from xl_utils.core.paths import unique_path

_INVALID_SHEET_CHARS = frozenset("[]:*?/\\")
_MAX_SHEET_NAME = 31


def read_workbook(
    path: Path,
    *,
    dtype: str | None = str,
) -> dict[str, pd.DataFrame]:
    """Read every sheet of a supported file into a dataframe mapping.

    Text is the default on purpose: it preserves leading zeros, CNJ/CPF codes
    and values that Excel would otherwise turn into scientific notation.
    """
    suffix = resolve_suffix(path)

    match suffix:
        case ".xlsx" | ".xlsm":
            return _read_excel(path, dtype=dtype, engine="openpyxl")
        case ".xls":
            return _read_excel(path, dtype=dtype, engine="xlrd")
        case ".csv":
            return {"Planilha1": pd.read_csv(path, dtype=dtype)}
        case ".html" | ".htm":
            return {
                f"Página{index}": frame
                for index, frame in enumerate(pd.read_html(path), start=1)
            }

    raise ValueError(f"Formato não suportado: {path.suffix or path.name!r}")


def save_workbook(sheets: Mapping[str, pd.DataFrame], destination: Path) -> Path:
    """Write a dataframe mapping to one xlsx file and return its path."""
    destination = unique_path(
        destination.parent,
        destination.stem,
        destination.suffix or ".xlsx",
    )
    used_names: set[str] = set()

    with pd.ExcelWriter(destination, engine="xlsxwriter") as writer:
        for name, frame in sheets.items():
            frame.to_excel(
                writer,
                sheet_name=_safe_sheet_name(name, used_names),
                index=False,
            )

    return destination


def _read_excel(
    path: Path,
    *,
    dtype: str | None,
    engine: str,
) -> dict[str, pd.DataFrame]:
    sheets = pd.read_excel(
        path,
        sheet_name=None,
        dtype=dtype,
        engine=engine,
    )
    return dict(sheets)


def _safe_sheet_name(name: str, used_names: set[str]) -> str:
    cleaned = "".join(
        "_" if char in _INVALID_SHEET_CHARS else char for char in name
    ).strip()
    cleaned = (cleaned or "Planilha")[:_MAX_SHEET_NAME]

    candidate = cleaned
    counter = 1
    while candidate.lower() in used_names:
        suffix = f"_{counter}"
        candidate = f"{cleaned[: _MAX_SHEET_NAME - len(suffix)]}{suffix}"
        counter += 1

    used_names.add(candidate.lower())
    return candidate
