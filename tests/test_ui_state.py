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
