from pathlib import Path

import pandas as pd
import pytest

from xl_utils.core.io import list_sheets
from xl_utils.core.tools.sheets import default_selection, filter_sheets


def _sheets() -> dict[str, pd.DataFrame]:
    return {
        "Uma": pd.DataFrame({"a": [1]}),
        "Outra": pd.DataFrame({"b": [2]}),
        "Terceira": pd.DataFrame({"c": [3]}),
    }


def test_list_sheets_reads_excel_names_in_order(tmp_path: Path) -> None:
    source = tmp_path / "entrada.xlsx"
    with pd.ExcelWriter(source) as writer:
        pd.DataFrame({"a": [1]}).to_excel(writer, sheet_name="Uma", index=False)
        pd.DataFrame({"b": [2]}).to_excel(writer, sheet_name="Outra", index=False)

    assert list_sheets(source) == ["Uma", "Outra"]


def test_list_sheets_uses_the_synthetic_csv_name(tmp_path: Path) -> None:
    source = tmp_path / "entrada.csv"
    source.write_text("a;b\n1;2\n", encoding="utf-8")

    assert list_sheets(source) == ["Planilha1"]


def test_list_sheets_names_every_html_table(tmp_path: Path) -> None:
    source = tmp_path / "entrada.html"
    source.write_text(
        "<table><tr><th>a</th></tr><tr><td>1</td></tr></table>"
        "<table><tr><th>b</th></tr><tr><td>2</td></tr></table>",
        encoding="utf-8",
    )

    assert list_sheets(source) == ["Página1", "Página2"]


def test_list_sheets_wraps_read_errors(tmp_path: Path) -> None:
    source = tmp_path / "quebrada.xlsx"
    source.write_bytes(b"isto nao e um xlsx")

    with pytest.raises(ValueError, match="Não foi possível listar"):
        list_sheets(source)


def test_list_sheets_rejects_unsupported_format(tmp_path: Path) -> None:
    source = tmp_path / "entrada.zzz"
    source.write_text("nada de planilha", encoding="utf-8")

    with pytest.raises(ValueError, match="Formato não suportado"):
        list_sheets(source)


def test_filter_sheets_with_none_keeps_every_sheet() -> None:
    sheets = _sheets()

    assert list(filter_sheets(sheets, None)) == ["Uma", "Outra", "Terceira"]


def test_filter_sheets_keeps_original_order_and_frames() -> None:
    sheets = _sheets()

    filtered = filter_sheets(sheets, {"Terceira", "Uma"})

    assert list(filtered) == ["Uma", "Terceira"]
    assert filtered["Uma"] is sheets["Uma"]


def test_filter_sheets_rejects_an_empty_selection() -> None:
    with pytest.raises(ValueError, match="ao menos uma aba"):
        filter_sheets(_sheets(), set())


def test_filter_sheets_rejects_unknown_sheet_names() -> None:
    with pytest.raises(ValueError, match="não encontrada"):
        filter_sheets(_sheets(), {"Uma", "Sumiu"})


def test_default_selection_uses_every_sheet_for_a_single_file() -> None:
    selection = default_selection({Path("a.xlsx"): ["Uma", "Outra"]})

    assert selection == {Path("a.xlsx"): {"Uma", "Outra"}}


def test_default_selection_uses_the_first_sheet_for_many_files() -> None:
    selection = default_selection(
        {
            Path("a.xlsx"): ["Uma", "Outra"],
            Path("b.xlsx"): ["Terceira"],
        }
    )

    assert selection == {
        Path("a.xlsx"): {"Uma"},
        Path("b.xlsx"): {"Terceira"},
    }
