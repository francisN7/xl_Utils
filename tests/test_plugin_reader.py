"""``request.reader``: leitura dos plugins pelo pipeline das nativas."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from xl_utils.core.tools.all_str import WorkbookReadError, prepare_workbook
from xl_utils.core.tools.sheets import filter_sheets
from xl_utils.shared import drive_cache
from xl_utils.shared.log import RunLog
from xl_utils.shared.plugins import reader as reader_module
from xl_utils.shared.plugins.api import ReadError, WorkbookReader
from xl_utils.shared.progress import NullReporter

FORMATS = ("xlsx_file", "xls_file", "csv_file", "html_file")


class StageSpy(NullReporter):
    def __init__(self) -> None:
        self.stages: list[str] = []

    def stage(self, text: str) -> None:
        self.stages.append(text)


def make_reader(
    sheets: dict[Path, tuple[str, ...]] | None = None,
    *,
    log: RunLog | None = None,
    progress: NullReporter | None = None,
) -> WorkbookReader:
    return WorkbookReader(
        sheets or {},
        log=RunLog() if log is None else log,
        progress=NullReporter() if progress is None else progress,
    )


def assert_same_book(
    left: dict[str, pd.DataFrame],
    right: dict[str, pd.DataFrame],
) -> None:
    assert list(left) == list(right)
    for name in left:
        pd.testing.assert_frame_equal(left[name], right[name])


@pytest.mark.parametrize("fixture", FORMATS)
def test_reads_like_the_native_tools(
    fixture: str,
    request: pytest.FixtureRequest,
) -> None:
    path: Path = request.getfixturevalue(fixture)
    native = prepare_workbook(path)
    first = next(iter(native))

    reader = make_reader({path: (first,)})

    assert_same_book(reader.read(path), filter_sheets(native, (first,)))
    assert_same_book(reader.read(path, all_sheets=True), native)


def test_text_keeps_leading_zeros_and_drops_emojis(tmp_path: Path) -> None:
    path = tmp_path / "emojis.csv"
    path.write_text("codigo,nome\n000123,Ana 😀\n", encoding="utf-8")

    frame = make_reader().read(path)["Planilha1"]

    assert frame.iloc[0]["codigo"] == "000123"
    assert "😀" not in frame.iloc[0]["nome"]


def test_selected_sheets_follow_the_workbook_order(tmp_path: Path) -> None:
    path = tmp_path / "abas.xlsx"
    with pd.ExcelWriter(path) as writer:
        for name in ("C", "A", "B"):
            pd.DataFrame({"x": [name]}).to_excel(writer, sheet_name=name, index=False)

    reader = make_reader({path: ("B", "C")})

    assert list(reader.read(path)) == ["C", "B"]
    assert list(reader.read(path, all_sheets=True)) == ["C", "A", "B"]


def test_path_without_selection_returns_every_sheet(xlsx_file: Path) -> None:
    assert list(make_reader().read(xlsx_file)) == ["Dados"]


def test_selection_matches_an_equivalent_path(xlsx_file: Path) -> None:
    other = xlsx_file.parent / "." / xlsx_file.name

    assert list(make_reader({xlsx_file: ("Dados",)}).read(other)) == ["Dados"]


def test_empty_selection_is_a_selection_error(xlsx_file: Path) -> None:
    with pytest.raises(ValueError, match="ao menos uma aba"):
        make_reader({xlsx_file: ()}).read(xlsx_file)


def test_unknown_sheet_is_a_selection_error(xlsx_file: Path) -> None:
    with pytest.raises(ValueError, match="Fantasma"):
        make_reader({xlsx_file: ("Fantasma",)}).read(xlsx_file)


def test_each_file_is_read_once_per_execution(
    xlsx_file: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[Path] = []

    def counting(path: Path) -> dict[str, pd.DataFrame]:
        calls.append(path)
        return prepare_workbook(path)

    monkeypatch.setattr(reader_module, "prepare_workbook", counting)
    reader = make_reader({xlsx_file: ("Dados",)})

    reader.read(xlsx_file)
    reader.read(xlsx_file, all_sheets=True)

    assert calls == [xlsx_file]


def test_changing_the_result_does_not_change_the_next_read(xlsx_file: Path) -> None:
    reader = make_reader()
    first = reader.read(xlsx_file)
    first["Dados"].loc[0, "nome"] = "Alterado"
    first["Dados"]["nova"] = "x"
    first.pop("Dados")

    again = reader.read(xlsx_file)["Dados"]

    assert again.iloc[0]["nome"] == "João"
    assert "nova" not in again.columns


def test_unreadable_file_raises_read_error(tmp_path: Path) -> None:
    path = tmp_path / "quebrado.xlsx"
    path.write_bytes(b"isto nao e uma planilha")

    with pytest.raises(ReadError, match="quebrado.xlsx") as error:
        make_reader().read(path)

    assert isinstance(error.value, WorkbookReadError)


def test_first_read_reports_stage_and_log_without_cells(xlsx_file: Path) -> None:
    log = RunLog()
    spy = StageSpy()
    reader = make_reader(log=log, progress=spy)

    reader.read(xlsx_file)
    reader.read(xlsx_file)

    assert spy.stages == ["Lendo entrada.xlsx"]
    text = log.to_text()
    assert text.count("entrada.xlsx: 1 aba(s)") == 1
    assert "João" not in text
    assert "000123" not in text


def test_drive_cache_file_reads_like_a_local_one(
    tmp_path: Path,
    xlsx_file: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(drive_cache, "cache_root", lambda: tmp_path / "cache")
    cached = drive_cache.store(
        drive_cache.new_session(),
        "AGENDA.xlsx",
        xlsx_file.read_bytes(),
    )
    assert drive_cache.is_cached(cached)

    reader = make_reader({cached: ("Dados",), xlsx_file: ("Dados",)})

    assert_same_book(reader.read(cached), reader.read(xlsx_file))
