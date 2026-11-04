from pathlib import Path

import pandas as pd
import pytest

from xl_utils.controllers.all_str import run_all_str
from xl_utils.controllers.cnj import run_cnj
from xl_utils.controllers.cut import run_cut
from xl_utils.controllers.merge import run_merge
from xl_utils.core.io import list_sheets, read_workbook
from xl_utils.core.save import save_to_output
from xl_utils.core.tools.merge import ColumnGroup, ColumnRef

_FORMATS = ["xlsx_file", "csv_file", "html_file", "xls_file"]


@pytest.mark.parametrize("fixture_name", _FORMATS)
def test_all_str_runs_on_every_format(
    fixture_name: str,
    request: pytest.FixtureRequest,
    sample_rows: dict[str, list[str]],
) -> None:
    source = request.getfixturevalue(fixture_name)
    before = source.read_bytes()

    outcome = run_all_str(source)

    assert source.read_bytes() == before
    saved_path = save_to_output([outcome.item])[0]
    assert saved_path.parent == source.parent / "output"
    assert saved_path.is_file()
    assert outcome.rows == 3
    saved = next(iter(read_workbook(saved_path, dtype=str).values()))
    assert saved["codigo"].tolist() == sample_rows["codigo"]
    assert saved["cnj"].tolist() == sample_rows["cnj"]
    assert saved["nome"].tolist() == sample_rows["nome"]


@pytest.mark.parametrize("fixture_name", _FORMATS)
def test_cnj_runs_on_every_format(
    fixture_name: str,
    request: pytest.FixtureRequest,
    sample_rows: dict[str, list[str]],
) -> None:
    source = request.getfixturevalue(fixture_name)
    before = source.read_bytes()

    outcome = run_cnj(source)

    assert source.read_bytes() == before
    assert outcome.cnjs == sorted(sample_rows["cnj"])
    saved_path = save_to_output([outcome.item])[0]
    assert saved_path.parent == source.parent / "output"
    saved = read_workbook(saved_path, dtype=str)["PROCESSOS"]
    assert saved["PROCESSOS"].tolist() == sorted(sample_rows["cnj"])


@pytest.mark.parametrize("fixture_name", _FORMATS)
def test_cut_runs_on_every_format(
    fixture_name: str,
    request: pytest.FixtureRequest,
    sample_rows: dict[str, list[str]],
) -> None:
    source = request.getfixturevalue(fixture_name)
    before = source.read_bytes()

    outcome = run_cut(source, 2)

    assert source.read_bytes() == before
    assert outcome.files == 2
    assert outcome.rows == 3
    values: list[str] = []
    for output in save_to_output(outcome.items):
        assert output.parent == source.parent / "output"
        frame = next(iter(read_workbook(output, dtype=str).values()))
        values.extend(frame["codigo"].tolist())
    assert values == sample_rows["codigo"]


@pytest.mark.parametrize("fixture_name", _FORMATS)
def test_cut_by_parts_runs_on_every_format(
    fixture_name: str,
    request: pytest.FixtureRequest,
    sample_rows: dict[str, list[str]],
) -> None:
    source = request.getfixturevalue(fixture_name)
    before = source.read_bytes()

    outcome = run_cut(source, parts=2)

    assert source.read_bytes() == before
    assert outcome.files == 2
    values: list[str] = []
    lengths: list[int] = []
    for output in save_to_output(outcome.items):
        frame = next(iter(read_workbook(output, dtype=str).values()))
        lengths.append(len(frame))
        values.extend(frame["codigo"].tolist())
    assert lengths == [2, 1]
    assert values == sample_rows["codigo"]


def test_merge_runs_with_mixed_formats(
    xlsx_file: Path,
    csv_file: Path,
    html_file: Path,
    xls_file: Path,
    sample_rows: dict[str, list[str]],
) -> None:
    sources = [
        (xlsx_file, "Dados"),
        (csv_file, "Planilha1"),
        (html_file, "Página1"),
        (xls_file, "Planilha1"),
    ]
    before = {path: path.read_bytes() for path, _ in sources}

    outcome = run_merge([(path, None) for path, _ in sources])

    saved_path = save_to_output([outcome.item])[0]
    assert saved_path.parent == xlsx_file.parent / "output"
    assert saved_path.is_file()
    assert outcome.rows == 12
    assert outcome.merged["codigo"].tolist() == sample_rows["codigo"] * 4
    assert outcome.merged["ORIGEM"].tolist() == [
        f"{path.name} - {sheet} - {row}"
        for path, sheet in sources
        for row in range(1, 4)
    ]
    assert all(path.read_bytes() == data for path, data in before.items())
    saved = read_workbook(saved_path, dtype=str)["Mesclado"]
    assert saved["codigo"].tolist() == sample_rows["codigo"] * 4


def test_merge_aligns_columns_across_formats(tmp_path: Path) -> None:
    xlsx = tmp_path / "a.xlsx"
    csv = tmp_path / "b.csv"
    pd.DataFrame({"codigo": ["0001"], "documento": ["AAA"]}).to_excel(
        xlsx,
        index=False,
    )
    pd.DataFrame({"codigo": ["0002"], "cnj": ["BBB"]}).to_csv(
        csv,
        index=False,
    )
    xlsx_sheet = list_sheets(xlsx)[0]
    csv_sheet = list_sheets(csv)[0]
    groups = [
        ColumnGroup(
            (
                ColumnRef(xlsx, xlsx_sheet, "codigo"),
                ColumnRef(csv, csv_sheet, "codigo"),
            )
        ),
        ColumnGroup(
            (
                ColumnRef(csv, csv_sheet, "cnj"),
                ColumnRef(xlsx, xlsx_sheet, "documento"),
            )
        ),
    ]

    outcome = run_merge(
        [(xlsx, None), (csv, None)],
        groups,
    )

    assert list(outcome.merged.columns) == ["ORIGEM", "codigo", "cnj"]
    assert outcome.merged["codigo"].tolist() == ["0001", "0002"]
    assert outcome.merged["cnj"].tolist() == ["AAA", "BBB"]
    assert not outcome.merged["cnj"].isna().any()
