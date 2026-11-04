from pathlib import Path

from xl_utils.ui.state import ToolState


def test_select_files_resets_result_and_message() -> None:
    state = ToolState(
        files=[Path("antigo.xlsx")],
        result={"Sheet1": object()},  # type: ignore[dict-item]
        options={"rows_per_file": "500"},
        message="ok",
        error="falhou",
        running=True,
    )

    state.select_files([Path("novo.xlsx")])

    assert state.files == [Path("novo.xlsx")]
    assert state.result is None
    assert state.options == {"rows_per_file": "500"}
    assert state.message == ""
    assert state.error is None
    assert state.running is False


def test_select_files_discards_the_sheet_selection() -> None:
    state = ToolState(
        files=[Path("antigo.xlsx")],
        sheet_names={Path("antigo.xlsx"): ["Uma"]},
        selected_sheets={Path("antigo.xlsx"): {"Uma"}},
    )

    state.select_files([Path("novo.xlsx")])

    assert state.sheet_names == {}
    assert state.selected_sheets == {}


def test_set_sheet_names_applies_the_default_selection() -> None:
    state = ToolState(files=[Path("a.xlsx")])
    state.set_sheet_names({Path("a.xlsx"): ["Uma", "Outra"]})

    assert state.sheet_names == {Path("a.xlsx"): ["Uma", "Outra"]}
    assert state.selected_sheets == {Path("a.xlsx"): {"Uma", "Outra"}}
    assert state.sheet_count == 2
    assert state.selected_count == 2


def test_set_sheet_names_picks_the_first_sheet_for_many_files() -> None:
    state = ToolState(files=[Path("a.xlsx"), Path("b.xlsx")])
    state.set_sheet_names(
        {
            Path("a.xlsx"): ["Uma", "Outra"],
            Path("b.xlsx"): ["Terceira"],
        }
    )

    assert state.selected_sheets == {
        Path("a.xlsx"): {"Uma"},
        Path("b.xlsx"): {"Terceira"},
    }
    assert state.selected_count == 2
    assert state.sheet_count == 3


def test_reset_clears_everything() -> None:
    state = ToolState(
        files=[Path("a.xlsx")],
        options={"rows_per_file": "500"},
        message="ok",
    )

    state.reset()

    assert state.files == []
    assert state.result is None
    assert state.options == {}
