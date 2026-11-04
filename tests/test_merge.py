from pathlib import Path

import pandas as pd
import pytest

from xl_utils.controllers.merge import inspect_columns, run_merge
from xl_utils.core.io import read_workbook
from xl_utils.core.save import save_to_output
from xl_utils.core.tools.merge import (
    ColumnGroup,
    ColumnRef,
    group_by_name,
    merge_sheets,
    move_column,
)


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


def test_merge_sheets_joins_names_with_an_explicit_group() -> None:
    entries = [
        (Path("a.xlsx"), "Uma", _frame(documento=["111"])),
        (Path("b.xlsx"), "Uma", _frame(CPF=["222"])),
    ]
    groups = [
        ColumnGroup(
            (
                ColumnRef(Path("a.xlsx"), "Uma", "documento"),
                ColumnRef(Path("b.xlsx"), "Uma", "CPF"),
            )
        )
    ]

    merged = merge_sheets(entries, groups)

    assert list(merged.columns) == ["ORIGEM", "documento"]
    assert merged["documento"].tolist() == ["111", "222"]


def test_group_by_name_joins_equal_columns() -> None:
    refs = [
        ColumnRef(Path("a.xlsx"), "Uma", "TAREFA"),
        ColumnRef(Path("a.xlsx"), "Uma", "CLASSE"),
        ColumnRef(Path("b.xlsx"), "Uma", "TAREFA"),
    ]

    groups = group_by_name(refs)

    assert [group.header for group in groups] == ["TAREFA", "CLASSE"]
    assert groups[0].columns == (refs[0], refs[2])


def test_merge_sheets_can_split_equal_names_into_two_columns() -> None:
    entries = [
        (Path("a.xlsx"), "Uma", _frame(TAREFA=["A"])),
        (Path("b.xlsx"), "Uma", _frame(TAREFA=["B"])),
    ]
    groups = [
        ColumnGroup((ColumnRef(Path("a.xlsx"), "Uma", "TAREFA"),)),
        ColumnGroup((ColumnRef(Path("b.xlsx"), "Uma", "TAREFA"),)),
    ]

    merged = merge_sheets(entries, groups)

    assert list(merged.columns) == ["ORIGEM", "TAREFA", "TAREFA_2"]
    assert merged["TAREFA"].iloc[0] == "A"
    assert pd.isna(merged["TAREFA"].iloc[1])
    assert pd.isna(merged["TAREFA_2"].iloc[0])
    assert merged["TAREFA_2"].iloc[1] == "B"


def test_move_column_reorders_and_changes_the_header() -> None:
    a = ColumnRef(Path("a.xlsx"), "Uma", "a")
    b = ColumnRef(Path("b.xlsx"), "Uma", "b")
    c = ColumnRef(Path("c.xlsx"), "Uma", "c")
    groups = [[a, b], [c]]

    moved = move_column(groups, b, 0, 0)

    assert moved == [[b, a], [c]]
    assert move_column(moved, c, 0, 0) == [[c, b, a], []]


def test_move_column_fills_an_empty_group() -> None:
    a = ColumnRef(Path("a.xlsx"), "Uma", "a")

    assert move_column([[], [a]], a, 0, 0) == [[a], []]


def test_move_column_rejects_two_columns_of_one_sheet() -> None:
    first = ColumnRef(Path("a.xlsx"), "Uma", "a")
    second = ColumnRef(Path("a.xlsx"), "Uma", "b")

    with pytest.raises(ValueError, match="uma coluna por saída"):
        move_column([[first], [second]], second, 0, 0)


def test_move_column_rejects_an_invalid_target() -> None:
    a = ColumnRef(Path("a.xlsx"), "Uma", "a")

    with pytest.raises(ValueError, match="destino inválida"):
        move_column([[a]], a, 2, 0)


def test_merge_sheets_rejects_two_columns_of_one_sheet_in_a_group() -> None:
    entries = [
        (Path("a.xlsx"), "Uma", _frame(um=["1"], outro=["2"])),
        (Path("b.xlsx"), "Uma", _frame(um=["3"])),
    ]
    groups = [
        ColumnGroup(
            (
                ColumnRef(Path("a.xlsx"), "Uma", "um"),
                ColumnRef(Path("a.xlsx"), "Uma", "outro"),
            )
        )
    ]

    with pytest.raises(ValueError, match="duas colunas"):
        merge_sheets(entries, groups)


def test_merge_sheets_matches_numeric_headers_as_text() -> None:
    entries = [
        (Path("a.xlsx"), "Uma", pd.DataFrame({2024: ["A"]})),
        (Path("b.xlsx"), "Uma", pd.DataFrame({2024: ["B"]})),
    ]

    merged = merge_sheets(entries)

    assert list(merged.columns) == ["ORIGEM", "2024"]
    assert merged["2024"].tolist() == ["A", "B"]


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

    assert columns == [
        ColumnRef(first, "Uma", "id"),
        ColumnRef(first, "Uma", "nome"),
        ColumnRef(second, "Dados", "id"),
        ColumnRef(second, "Dados", "cpf"),
    ]


def test_inspect_columns_reads_csv_headers(tmp_path: Path) -> None:
    source = tmp_path / "entrada.csv"
    source.write_text("nome;documento\nA;1\n", encoding="utf-8-sig")

    assert inspect_columns([(source, None)]) == [
        ColumnRef(source, "Planilha1", "nome"),
        ColumnRef(source, "Planilha1", "documento"),
    ]


def test_run_merge_prepares_one_workbook_and_keeps_the_sources(
    tmp_path: Path,
) -> None:
    first = tmp_path / "a.xlsx"
    second = tmp_path / "b.xlsx"
    _write(first, {"Uma": _frame(nome=["A1", "A2"])})
    _write(second, {"Dados": _frame(nome=["B1"])})
    before = (first.read_bytes(), second.read_bytes())

    outcome = run_merge([(first, None), (second, None)])

    assert (first.read_bytes(), second.read_bytes()) == before
    assert not (tmp_path / "output").exists()
    assert outcome.suggested_name == "Merge.xlsx"
    assert outcome.item.output_dir == tmp_path / "output"
    assert outcome.rows == 3
    assert outcome.sheets == 2
    assert outcome.merged["ORIGEM"].tolist() == [
        "a.xlsx - Uma - 1",
        "a.xlsx - Uma - 2",
        "b.xlsx - Dados - 1",
    ]

    saved_path = save_to_output([outcome.item])[0]
    assert saved_path == tmp_path / "output" / "Merge.xlsx"
    saved = read_workbook(saved_path, dtype=str)
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
    one_path = save_to_output([one.item])[0]
    two_path = save_to_output([two.item])[0]

    assert one_path.name == "Merge.xlsx"
    assert two_path.name == "Merge_001.xlsx"
    assert one_path.is_file()
    assert two_path.is_file()
