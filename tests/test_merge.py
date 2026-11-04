from pathlib import Path

import pandas as pd
import pytest

from xl_utils.controllers.merge import inspect_columns, run_merge
from xl_utils.core.io import read_workbook
from xl_utils.core.tools.merge import merge_sheets


def _frame(**columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns)


def _write(path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    with pd.ExcelWriter(path) as writer:
        for name, frame in sheets.items():
            frame.to_excel(writer, sheet_name=name, index=False)


def test_merge_sheets_preserves_order_and_labels_origin() -> None:
    entries = [
        (Path("a.xlsx"), "Uma", _frame(nome=["A1", "A2"])),
        (Path("a.xlsx"), "Outra", _frame(nome=["B1"])),
        (Path("b.xlsx"), "Dados", _frame(nome=["C1"])),
    ]

    merged = merge_sheets(entries)

    assert list(merged.columns) == ["ORIGEM", "nome"]
    assert merged["nome"].tolist() == ["A1", "A2", "B1", "C1"]
    assert merged["ORIGEM"].tolist() == [
        "a.xlsx - Uma - 1",
        "a.xlsx - Uma - 2",
        "a.xlsx - Outra - 1",
        "b.xlsx - Dados - 1",
    ]


def test_merge_sheets_fills_missing_columns_and_appends_extra() -> None:
    entries = [
        (Path("a.xlsx"), "Uma", _frame(id=["1"], nome=["A"])),
        (Path("b.xlsx"), "Uma", _frame(id=["2"], extra=["X"])),
    ]

    merged = merge_sheets(entries)

    assert list(merged.columns) == ["ORIGEM", "id", "nome", "extra"]
    assert merged.loc[0, "id"] == "1"
    assert pd.isna(merged.loc[1, "nome"])
    assert pd.isna(merged.loc[0, "extra"])
    assert merged.loc[1, "extra"] == "X"


def test_merge_sheets_uses_the_column_map_to_join_names() -> None:
    entries = [
        (Path("a.xlsx"), "Uma", _frame(documento=["111"])),
        (Path("b.xlsx"), "Uma", _frame(CPF=["222"])),
    ]

    merged = merge_sheets(
        entries,
        {"documento": "cpf", "CPF": "cpf"},
    )

    assert list(merged.columns) == ["ORIGEM", "cpf"]
    assert merged["cpf"].tolist() == ["111", "222"]


def test_merge_sheets_skips_empty_sheets_but_keeps_rows() -> None:
    entries = [
        (Path("a.xlsx"), "Vazia", _frame(nome=[])),
        (Path("a.xlsx"), "Cheia", _frame(nome=["A"])),
        (Path("b.xlsx"), "Tambem vazia", _frame(outra=[])),
    ]

    merged = merge_sheets(entries)

    assert merged["ORIGEM"].tolist() == ["a.xlsx - Cheia - 1"]
    assert merged["nome"].tolist() == ["A"]


def test_merge_sheets_rejects_entries_without_rows() -> None:
    with pytest.raises(ValueError, match="Nenhuma aba com dados"):
        merge_sheets([(Path("a.xlsx"), "Vazia", _frame(nome=[]))])


def test_merge_sheets_does_not_change_the_origin_frames() -> None:
    frame = _frame(nome=["A"])

    merge_sheets(
        [
            (Path("a.xlsx"), "Uma", frame),
            (Path("b.xlsx"), "Uma", _frame(nome=["B"])),
        ]
    )

    assert list(frame.columns) == ["nome"]
    assert frame["nome"].tolist() == ["A"]


def test_merge_sheets_protects_an_existing_origem_column() -> None:
    entries = [
        (Path("a.xlsx"), "Uma", _frame(ORIGEM=["antiga"], nome=["A"])),
        (Path("b.xlsx"), "Uma", _frame(nome=["B"])),
    ]

    merged = merge_sheets(entries)

    assert list(merged.columns) == ["ORIGEM", "ORIGEM_original", "nome"]
    assert merged["ORIGEM_original"].tolist()[0] == "antiga"


def test_inspect_columns_keeps_order_and_only_selected_sheets(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a.xlsx"
    _write(
        first,
        {
            "Uma": _frame(id=["1"], nome=["A"]),
            "Outra": _frame(ignorada=["x"]),
        },
    )
    second = tmp_path / "b.xlsx"
    _write(second, {"Dados": _frame(id=["2"], cpf=["0001"])})

    columns = inspect_columns(
        [
            (first, {"Uma"}),
            (second, None),
        ]
    )

    assert columns == ["id", "nome", "cpf"]


def test_inspect_columns_reads_csv_headers(tmp_path: Path) -> None:
    source = tmp_path / "entrada.csv"
    source.write_text("nome;documento\nA;1\n", encoding="utf-8-sig")

    assert inspect_columns([(source, None)]) == ["nome;documento"]


def test_run_merge_writes_one_workbook_and_keeps_the_sources(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a.xlsx"
    second = tmp_path / "b.xlsx"
    _write(first, {"Uma": _frame(nome=["A1", "A2"])})
    _write(second, {"Dados": _frame(nome=["B1"])})
    before = (first.read_bytes(), second.read_bytes())

    outcome = run_merge([(first, None), (second, None)])

    assert (first.read_bytes(), second.read_bytes()) == before
    assert outcome.output == tmp_path / "output" / "Merge.xlsx"
    assert outcome.rows == 3
    assert outcome.sheets == 2
    assert outcome.merged["ORIGEM"].tolist() == [
        "a.xlsx - Uma - 1",
        "a.xlsx - Uma - 2",
        "b.xlsx - Dados - 1",
    ]
    saved = read_workbook(outcome.output, dtype=str)
    assert list(saved) == ["Mesclado"]
    assert saved["Mesclado"]["ORIGEM"].tolist() == outcome.merged["ORIGEM"].tolist()
    assert any("Arquivo: a.xlsx" in line for line in outcome.log)
    assert any("Arquivo: b.xlsx" in line for line in outcome.log)


def test_run_merge_accepts_two_sheets_of_one_file(tmp_path: Path) -> None:
    source = tmp_path / "a.xlsx"
    _write(
        source,
        {
            "Uma": _frame(nome=["A"]),
            "Outra": _frame(nome=["B"]),
        },
    )

    outcome = run_merge([(source, None)])

    assert outcome.sheets == 2
    assert outcome.merged["nome"].tolist() == ["A", "B"]


def test_run_merge_rejects_a_single_usable_sheet(tmp_path: Path) -> None:
    source = tmp_path / "a.xlsx"
    _write(source, {"Uma": _frame(nome=["A"])})

    with pytest.raises(ValueError, match="ao menos duas abas"):
        run_merge([(source, None)])
    assert not (tmp_path / "output").exists()


def test_run_merge_rejects_an_empty_selection(tmp_path: Path) -> None:
    source = tmp_path / "a.xlsx"
    _write(source, {"Uma": _frame(nome=["A"])})

    with pytest.raises(ValueError, match="ao menos uma aba"):
        run_merge([(source, set())])


def test_run_merge_rejects_an_empty_sheet_beside_a_filled_one(
    tmp_path: Path,
) -> None:
    source = tmp_path / "a.xlsx"
    _write(
        source,
        {
            "Vazia": _frame(nome=[]),
            "Cheia": _frame(nome=["A"]),
        },
    )

    with pytest.raises(ValueError, match="ao menos duas abas"):
        run_merge([(source, None)])


def test_run_merge_does_not_overwrite_an_existing_output(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a.xlsx"
    second = tmp_path / "b.xlsx"
    _write(first, {"Uma": _frame(nome=["A"])})
    _write(second, {"Uma": _frame(nome=["B"])})

    one = run_merge([(first, None), (second, None)])
    two = run_merge([(first, None), (second, None)])

    assert one.output.name == "Merge.xlsx"
    assert two.output.name == "Merge_001.xlsx"
    assert one.output.is_file()
    assert two.output.is_file()
