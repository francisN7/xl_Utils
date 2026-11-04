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


def list_sheets(path: Path) -> list[str]:
    """Return the sheet names of a supported file, in their original order.

    Excel only reads the workbook metadata. CSV has a single synthetic sheet
    and HTML has to be parsed, because each table becomes a sheet.
    """
    suffix = resolve_suffix(path)

    if suffix == ".csv":
        return ["Planilha1"]
    if suffix in {".html", ".htm"}:
        return _list_html_sheets(path)
    if suffix in {".xlsx", ".xlsm", ".xls"}:
        engine = "xlrd" if suffix == ".xls" else "openpyxl"
        return _excel_sheet_names(path, engine=engine)

    raise ValueError(f"Formato não suportado: {path.suffix or path.name!r}")


def read_headers(path: Path) -> dict[str, list[str]]:
    """Return the column labels of every sheet without loading the rows.

    Excel reads only the headers; CSV tries the same encodings as the repair
    path; HTML has no header-only mode, so its tables are parsed fully. Labels
    are always returned as text, matching the UI column mapping.
    """
    suffix = resolve_suffix(path)

    try:
        match suffix:
            case ".xlsx" | ".xlsm" | ".xls":
                engine = "xlrd" if suffix == ".xls" else "openpyxl"
                frames = pd.read_excel(path, sheet_name=None, nrows=0, engine=engine)
                return {
                    str(name): [str(column) for column in frame.columns]
                    for name, frame in frames.items()
                }
            case ".csv":
                return {"Planilha1": _csv_headers(path)}
            case ".html" | ".htm":
                frames = pd.read_html(path)
                return {
                    f"Página{index}": [str(column) for column in frame.columns]
                    for index, frame in enumerate(frames, start=1)
                }
    except Exception as error:  # noqa: BLE001 - report one clear failure
        raise ValueError(
            f"Não foi possível ler as colunas de {path.name}: {error}"
        ) from error

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


def _excel_sheet_names(path: Path, *, engine: str) -> list[str]:
    try:
        with pd.ExcelFile(path, engine=engine) as workbook:
            return [str(name) for name in workbook.sheet_names]
    except Exception as error:  # noqa: BLE001 - report one clear failure
        raise ValueError(
            f"Não foi possível listar as abas de {path.name}: {error}"
        ) from error


def _list_html_sheets(path: Path) -> list[str]:
    try:
        return list(read_workbook(path, dtype=str))
    except Exception as error:  # noqa: BLE001 - report one clear failure
        raise ValueError(
            f"Não foi possível listar as abas de {path.name}: {error}"
        ) from error


def _csv_headers(path: Path) -> list[str]:
    last_error: Exception | None = None
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            frame = pd.read_csv(path, nrows=0, encoding=encoding)
        except Exception as error:  # noqa: BLE001 - try the next encoding
            last_error = error
            continue
        return [str(column) for column in frame.columns]

    assert last_error is not None
    raise last_error


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
