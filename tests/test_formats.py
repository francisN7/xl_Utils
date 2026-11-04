from pathlib import Path

import pandas as pd
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


@pytest.mark.parametrize("delimiter", [";", "\t", "|"])
def test_prepare_workbook_detects_the_csv_delimiter(
    tmp_path: Path,
    delimiter: str,
) -> None:
    source = tmp_path / "separado.csv"
    source.write_text(
        f"codigo{delimiter}nome{delimiter}valor\n000123{delimiter}Ana{delimiter}1,50\n",
        encoding="utf-8",
    )

    frame = prepare_workbook(source)["Planilha1"]

    assert list(frame.columns) == ["codigo", "nome", "valor"]
    assert frame["codigo"].tolist() == ["000123"]
    assert frame["valor"].tolist() == ["1,50"]
    assert read_headers(source) == {
        "Planilha1": ["codigo", "nome", "valor"],
    }


def test_prepare_workbook_keeps_na_like_text_in_csv(tmp_path: Path) -> None:
    source = tmp_path / "na.csv"
    source.write_text(
        "nome,obs\nAna,NA\nBruno,N/A\nCarla,\n",
        encoding="utf-8",
    )

    frame = prepare_workbook(source)["Planilha1"]

    assert frame["obs"].tolist() == ["NA", "N/A", ""]


def test_read_workbook_keeps_na_like_text_in_excel(tmp_path: Path) -> None:
    source = tmp_path / "na.xlsx"
    pd.DataFrame(
        {
            "nome": ["Ana", "Bruno", "Carla"],
            "obs": ["NA", "N/A", None],
        }
    ).to_excel(source, index=False)

    frame = read_workbook(source, dtype=str)["Sheet1"]

    assert frame["obs"].tolist() == ["NA", "N/A", ""]


def test_read_headers_keeps_a_column_named_na(tmp_path: Path) -> None:
    source = tmp_path / "coluna.csv"
    source.write_text("NA,nome\n1,Ana\n", encoding="utf-8")

    assert read_headers(source) == {"Planilha1": ["NA", "nome"]}


def test_html_with_two_level_header_keeps_text(tmp_path: Path) -> None:
    source = tmp_path / "tabela.html"
    source.write_text(
        "<table><tr><th colspan=2>Grupo</th></tr>"
        "<tr><th>cod</th><th>nome</th></tr>"
        "<tr><td>000123</td><td>Ana</td></tr></table>",
        encoding="utf-8",
    )

    frame = prepare_workbook(source)["Página1"]

    assert list(frame.columns) == ["Grupo - cod", "Grupo - nome"]
    assert frame["Grupo - cod"].tolist() == ["000123"]
    assert read_headers(source) == {
        "Página1": ["Grupo - cod", "Grupo - nome"],
    }


def test_invalid_xls_reports_no_alternative_reader(tmp_path: Path) -> None:
    source = tmp_path / "quebrado.xls"
    source.write_bytes(b"isto nao e um xls")

    with pytest.raises(WorkbookReadError, match="leitor alternativo"):
        prepare_workbook(source)
