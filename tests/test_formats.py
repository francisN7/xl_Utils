from pathlib import Path

import pytest

from xl_utils.core.io import list_sheets, read_headers, read_workbook
from xl_utils.core.tools.all_str import WorkbookReadError, prepare_workbook

_FORMATS = [
    ("xlsx_file", "Dados"),
    ("csv_file", "Planilha1"),
    ("html_file", "Página1"),
    ("xls_file", "Planilha1"),
]


@pytest.mark.parametrize(("fixture_name", "sheet_name"), _FORMATS)
def test_read_workbook_keeps_text_in_every_format(
    fixture_name: str,
    sheet_name: str,
    request: pytest.FixtureRequest,
    sample_rows: dict[str, list[str]],
) -> None:
    source = request.getfixturevalue(fixture_name)

    sheets = read_workbook(source, dtype=str)

    assert list(sheets) == [sheet_name]
    frame = sheets[sheet_name]
    assert frame["codigo"].tolist() == sample_rows["codigo"]
    assert frame["cnj"].tolist() == sample_rows["cnj"]
    assert frame["nome"].tolist() == sample_rows["nome"]


@pytest.mark.parametrize(("fixture_name", "sheet_name"), _FORMATS)
def test_list_sheets_finds_the_real_sheets(
    fixture_name: str,
    sheet_name: str,
    request: pytest.FixtureRequest,
) -> None:
    source = request.getfixturevalue(fixture_name)

    assert list_sheets(source) == [sheet_name]


@pytest.mark.parametrize(("fixture_name", "sheet_name"), _FORMATS)
def test_read_headers_returns_the_same_labels_as_the_rows(
    fixture_name: str,
    sheet_name: str,
    request: pytest.FixtureRequest,
) -> None:
    source = request.getfixturevalue(fixture_name)

    assert read_headers(source) == {sheet_name: ["codigo", "cnj", "nome"]}


@pytest.mark.parametrize(("fixture_name", "sheet_name"), _FORMATS)
def test_prepare_workbook_cleans_every_format(
    fixture_name: str,
    sheet_name: str,
    request: pytest.FixtureRequest,
    sample_rows: dict[str, list[str]],
) -> None:
    source = request.getfixturevalue(fixture_name)

    frame = prepare_workbook(source)[sheet_name]

    assert frame["codigo"].tolist() == sample_rows["codigo"]
    assert frame["cnj"].tolist() == sample_rows["cnj"]
    assert frame["nome"].tolist() == sample_rows["nome"]


def test_prepare_workbook_repairs_a_cp1252_csv(tmp_path: Path) -> None:
    source = tmp_path / "reparo.csv"
    source.write_bytes("codigo;nome\n000123;João\n".encode("cp1252"))

    frame = prepare_workbook(source)["Planilha1"]

    assert list(frame.columns) == ["codigo", "nome"]
    assert frame["codigo"].tolist() == ["000123"]
    assert frame["nome"].tolist() == ["João"]
    assert read_headers(source) == {"Planilha1": ["codigo", "nome"]}


def test_prepare_workbook_raises_a_typed_error_for_an_invalid_file(
    tmp_path: Path,
) -> None:
    source = tmp_path / "quebrada.xlsx"
    source.write_bytes(b"isto nao e um xlsx")

    with pytest.raises(WorkbookReadError, match="quebrada.xlsx"):
        prepare_workbook(source)
