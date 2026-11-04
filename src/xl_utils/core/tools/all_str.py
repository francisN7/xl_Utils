"""Shared workbook pipeline: read everything as text and remove emojis."""

from pathlib import Path

import pandas as pd

from xl_utils.core.io import read_workbook
from xl_utils.core.mime import resolve_suffix
from xl_utils.core.text import remove_emojis


class WorkbookReadError(Exception):
    """Raised when a workbook cannot be read, even after a repair attempt."""


def prepare_workbook(path: Path) -> dict[str, pd.DataFrame]:
    """Read every sheet as text and remove emojis, keeping line breaks.

    The original file is never modified. When the normal read fails, a looser
    reader is tried once; if that also fails, ``WorkbookReadError`` is raised.
    """
    try:
        sheets = read_workbook(path, dtype=str)
    except Exception as error:  # noqa: BLE001 - any read failure gets one retry
        sheets = _read_with_repair(path, error)

    return {name: frame.map(remove_emojis) for name, frame in sheets.items()}


def _read_with_repair(
    path: Path,
    original: Exception,
) -> dict[str, pd.DataFrame]:
    try:
        return _repair_read(path)
    except Exception as error:  # noqa: BLE001 - report one typed failure
        raise WorkbookReadError(
            f"Não foi possível ler {path.name}: {original}"
        ) from error


def _repair_read(path: Path) -> dict[str, pd.DataFrame]:
    """Try a looser reader for the detected format, without shelling out."""
    suffix = resolve_suffix(path)

    match suffix:
        case ".xlsx" | ".xlsm":
            return _read_excel_openpyxl(path)
        case ".csv":
            return _read_csv_encodings(path)
        case ".html" | ".htm":
            return _read_html_flavors(path)
        case ".xls":
            return read_workbook(path, dtype=str)

    raise ValueError(f"Formato não suportado: {path.suffix or path.name!r}")


def _read_excel_openpyxl(path: Path) -> dict[str, pd.DataFrame]:
    sheets = pd.read_excel(
        path,
        sheet_name=None,
        dtype=str,
        engine="openpyxl",
        engine_kwargs={"read_only": True, "data_only": True},
    )
    return dict(sheets)


def _read_csv_encodings(path: Path) -> dict[str, pd.DataFrame]:
    last_error: Exception | None = None
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            frame = pd.read_csv(
                path,
                dtype=str,
                encoding=encoding,
                sep=None,
                engine="python",
            )
        except Exception as error:  # noqa: BLE001 - try the next encoding
            last_error = error
            continue
        return {"Planilha1": frame}

    assert last_error is not None
    raise last_error


def _read_html_flavors(path: Path) -> dict[str, pd.DataFrame]:
    last_error: Exception | None = None
    for flavor in ("lxml", None):
        try:
            frames = pd.read_html(path, flavor=flavor)
        except Exception as error:  # noqa: BLE001 - try the next parser
            last_error = error
            continue
        if frames:
            return {
                f"Página{index}": frame for index, frame in enumerate(frames, start=1)
            }

    if last_error is not None:
        raise last_error
    raise ValueError(f"Nenhuma tabela encontrada em {path.name}")
