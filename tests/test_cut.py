from pathlib import Path

import pandas as pd
import pytest

from xl_utils.controllers.cut import run_cut
from xl_utils.core.io import read_workbook
from xl_utils.core.paths import safe_file_part
from xl_utils.core.save import save_to_output
from xl_utils.core.tools.cut import split_frame, split_workbook


def _frame(rows: int, column: str = "numero") -> pd.DataFrame:
    return pd.DataFrame({column: [f"{number:04d}" for number in range(1, rows + 1)]})


def test_split_frame_exact_multiple() -> None:
    parts = split_frame(_frame(6), 3)

    assert [len(part) for part in parts] == [3, 3]
    assert [value for part in parts for value in part["numero"]] == [
        "0001",
        "0002",
        "0003",
        "0004",
        "0005",
        "0006",
    ]


def test_split_frame_keeps_the_remainder() -> None:
    parts = split_frame(_frame(7), 3)

    assert [len(part) for part in parts] == [3, 3, 1]
    assert parts[-1]["numero"].tolist() == ["0007"]


def test_split_frame_with_rows_above_total_returns_one_part() -> None:
    parts = split_frame(_frame(2), 10)

    assert len(parts) == 1
    assert parts[0]["numero"].tolist() == ["0001", "0002"]


def test_split_frame_of_empty_frame_returns_one_empty_part() -> None:
    parts = split_frame(_frame(0), 10)

    assert len(parts) == 1
    assert parts[0].empty
    assert list(parts[0].columns) == ["numero"]


@pytest.mark.parametrize("rows", [0, -1])
def test_split_frame_rejects_non_positive_rows(rows: int) -> None:
    with pytest.raises(ValueError, match="maior que zero"):
        split_frame(_frame(3), rows)


def test_split_workbook_cuts_every_sheet() -> None:
    parts = split_workbook({"Uma": _frame(5), "Outra": _frame(2)}, 2)

    assert list(parts) == ["Uma", "Outra"]
    assert [len(part) for part in parts["Uma"]] == [2, 2, 1]
    assert [len(part) for part in parts["Outra"]] == [2]


def test_safe_file_part_replaces_invalid_characters() -> None:
    assert safe_file_part('a/b:c*"d') == "a_b_c__d"
    assert safe_file_part("   ") == "Aba"


def test_run_cut_prepares_parts_and_keeps_the_source(tmp_path: Path) -> None:
    source = tmp_path / "entrada.xlsx"
    _frame(2500).to_excel(source, index=False)
    before = source.read_bytes()

    outcome = run_cut(source, 1000)

    assert source.read_bytes() == before
    assert outcome.files == 3
    assert outcome.rows == 2500
    assert outcome.suggested_names == [
        "entrada_Recorte_001.xlsx",
        "entrada_Recorte_002.xlsx",
        "entrada_Recorte_003.xlsx",
    ]
    assert outcome.preview["Sheet1"]["numero"].tolist()[:2] == [
        "0001",
        "0002",
    ]
    assert not (tmp_path / "output").exists()

    outputs = save_to_output(outcome.items)
    lengths = []
    values = []
    for output in outputs:
        frame = next(iter(read_workbook(output, dtype=str).values()))
        lengths.append(len(frame))
        values.extend(frame["numero"].tolist())

    assert lengths == [1000, 1000, 500]
    assert values == _frame(2500)["numero"].tolist()
    assert any("Arquivos prontos: 3" in line for line in outcome.log)


def test_run_cut_names_parts_by_sheet_when_there_are_many(
    tmp_path: Path,
) -> None:
    source = tmp_path / "entrada.xlsx"
    with pd.ExcelWriter(source) as writer:
        _frame(3).to_excel(writer, sheet_name="Uma", index=False)
        _frame(3).to_excel(writer, sheet_name="Outra", index=False)

    outcome = run_cut(source, 2)

    assert outcome.suggested_names == [
        "entrada_Uma_Recorte_001.xlsx",
        "entrada_Uma_Recorte_002.xlsx",
        "entrada_Outra_Recorte_001.xlsx",
        "entrada_Outra_Recorte_002.xlsx",
    ]


def test_run_cut_processes_only_the_selected_sheet(tmp_path: Path) -> None:
    source = tmp_path / "entrada.xlsx"
    with pd.ExcelWriter(source) as writer:
        _frame(3).to_excel(writer, sheet_name="Uma", index=False)
        _frame(3).to_excel(writer, sheet_name="Outra", index=False)

    outcome = run_cut(source, 2, selected={"Outra"})

    assert outcome.rows == 3
    assert outcome.suggested_names == [
        "entrada_Recorte_001.xlsx",
        "entrada_Recorte_002.xlsx",
    ]
    outputs = save_to_output(outcome.items)
    assert list(read_workbook(outputs[0], dtype=str)) == ["Outra"]


def test_run_cut_names_parts_by_sheet_for_many_selected(
    tmp_path: Path,
) -> None:
    source = tmp_path / "entrada.xlsx"
    with pd.ExcelWriter(source) as writer:
        _frame(2).to_excel(writer, sheet_name="Uma", index=False)
        _frame(2).to_excel(writer, sheet_name="Outra", index=False)

    outcome = run_cut(source, 1, selected={"Uma", "Outra"})

    assert outcome.suggested_names == [
        "entrada_Uma_Recorte_001.xlsx",
        "entrada_Uma_Recorte_002.xlsx",
        "entrada_Outra_Recorte_001.xlsx",
        "entrada_Outra_Recorte_002.xlsx",
    ]


def test_run_cut_rejects_an_empty_selection(tmp_path: Path) -> None:
    source = tmp_path / "entrada.xlsx"
    _frame(3).to_excel(source, index=False)

    with pytest.raises(ValueError, match="ao menos uma aba"):
        run_cut(source, 2, selected=set())


def test_run_cut_with_rows_above_total_writes_one_file(tmp_path: Path) -> None:
    source = tmp_path / "entrada.xlsx"
    _frame(5).to_excel(source, index=False)

    outcome = run_cut(source, 10)

    assert outcome.files == 1
    saved = next(
        iter(read_workbook(save_to_output(outcome.items)[0], dtype=str).values())
    )
    assert saved["numero"].tolist() == _frame(5)["numero"].tolist()


def test_run_cut_with_empty_sheet_writes_one_empty_file(
    tmp_path: Path,
) -> None:
    source = tmp_path / "vazia.xlsx"
    pd.DataFrame({"numero": []}).to_excel(source, index=False)

    outcome = run_cut(source, 10)

    assert outcome.files == 1
    saved = next(
        iter(read_workbook(save_to_output(outcome.items)[0], dtype=str).values())
    )
    assert saved.empty
    assert list(saved.columns) == ["numero"]


def test_run_cut_rejects_invalid_rows_without_creating_output(
    tmp_path: Path,
) -> None:
    source = tmp_path / "entrada.xlsx"
    _frame(5).to_excel(source, index=False)

    with pytest.raises(ValueError, match="maior que zero"):
        run_cut(source, 0)

    assert not (tmp_path / "output").exists()


def test_run_cut_does_not_overwrite_existing_files(tmp_path: Path) -> None:
    source = tmp_path / "entrada.xlsx"
    _frame(3).to_excel(source, index=False)

    first = run_cut(source, 2)
    second = run_cut(source, 2)
    first_paths = save_to_output(first.items)
    second_paths = save_to_output(second.items)

    assert first_paths[0] != second_paths[0]
    assert all(path.is_file() for path in first_paths + second_paths)
