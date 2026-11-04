"""Synthetic spreadsheets shared by the format and integration tests."""

from pathlib import Path

import pandas as pd
import pytest

FIXTURES = Path(__file__).parent / "fixtures"

_SHEET_NAME = "Dados"


@pytest.fixture(scope="session")
def sample_rows() -> dict[str, list[str]]:
    """Return the same fictional rows used by every test format."""
    return {
        "codigo": ["000123", "000045", "000007"],
        "cnj": [
            "0001234-56.2024.8.26.0100",
            "0009876-54.2023.8.26.0100",
            "0001111-11.2022.8.26.0100",
        ],
        "nome": ["João", "Conceição", "Ana"],
    }


@pytest.fixture
def xlsx_file(
    tmp_path: Path,
    sample_rows: dict[str, list[str]],
) -> Path:
    source = tmp_path / "entrada.xlsx"
    pd.DataFrame(sample_rows).to_excel(
        source,
        index=False,
        sheet_name=_SHEET_NAME,
    )
    return source


@pytest.fixture
def csv_file(
    tmp_path: Path,
    sample_rows: dict[str, list[str]],
) -> Path:
    source = tmp_path / "entrada.csv"
    pd.DataFrame(sample_rows).to_csv(source, index=False, encoding="utf-8")
    return source


@pytest.fixture
def html_file(
    tmp_path: Path,
    sample_rows: dict[str, list[str]],
) -> Path:
    source = tmp_path / "entrada.html"
    table = pd.DataFrame(sample_rows).to_html(index=False)
    source.write_text(
        '<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>'
        f"{table}</body></html>",
        encoding="utf-8",
    )
    return source


@pytest.fixture
def xls_file(tmp_path: Path) -> Path:
    source = tmp_path / "entrada.xls"
    source.write_bytes((FIXTURES / "minimo.xls").read_bytes())
    return source
