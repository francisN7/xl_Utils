from pathlib import Path

from xl_utils.core.tools.merge import ColumnRef
from xl_utils.ui import theme
from xl_utils.ui.components.tool_layout import OverlayHost
from xl_utils.ui.pages.merge import MergeOptions
from xl_utils.ui.state import ToolState


def _refs() -> list[ColumnRef]:
    return [
        ColumnRef(Path("a.xlsx"), "Uma", "NOME"),
        ColumnRef(Path("b.xlsx"), "Uma", "NOME"),
        ColumnRef(Path("b.xlsx"), "Uma", "ID"),
    ]


def _panel(
    monkeypatch,
    refs: list[ColumnRef],
) -> tuple[ToolState, OverlayHost, MergeOptions]:
    state = ToolState()
    state.files = [Path("a.xlsx"), Path("b.xlsx")]
    state.sheet_names = {path: ["Uma"] for path in state.files}
    state.selected_sheets = {path: {"Uma"} for path in state.files}
    monkeypatch.setattr(
        "xl_utils.ui.pages.merge.inspect_columns",
        lambda _sources: list(refs),
    )
    overlay = OverlayHost()
    return state, overlay, MergeOptions(state, overlay)


def test_maximize_stays_hidden_without_columns(monkeypatch) -> None:
    state, overlay, panel = _panel(monkeypatch, [])

    assert state.files
    assert not panel._maximize_button.visible
    assert not overlay.control.visible


def test_maximize_covers_the_page_and_confirm_restores(monkeypatch) -> None:
    _state, overlay, panel = _panel(monkeypatch, _refs())
    before = [list(group) for group in panel._groups]

    assert panel._maximize_button.visible
    assert not panel._confirm.visible
    assert not overlay.control.visible

    panel._maximize()

    assert overlay.control.visible
    assert overlay._slot.content is panel._panel
    assert panel._confirm.visible
    assert len(panel._full_board.controls) == len(panel._board.controls)

    panel._confirm.on_click(None)

    assert not overlay.control.visible
    assert not panel._confirm.visible
    assert panel._groups == before


def test_restore_button_and_theme_change_keep_the_groups(monkeypatch) -> None:
    _state, overlay, panel = _panel(monkeypatch, _refs())
    panel._maximize()

    mapping = theme.color_mapping("dark", "light")
    theme.apply("light")
    try:
        theme.restyle(overlay.control, mapping)

        assert overlay.control.visible
        assert overlay.control.bgcolor == theme.LIGHT["BACKGROUND"]
        assert panel._confirm.visible
    finally:
        theme.apply("dark")

    panel._restore_button.on_click(None)

    assert not overlay.control.visible
    assert not panel._confirm.visible


def test_moving_a_chip_in_fullscreen_survives_the_return(monkeypatch) -> None:
    _state, overlay, panel = _panel(monkeypatch, _refs())
    nome_a, nome_b = panel._groups[0]

    panel._maximize()
    panel._move(nome_b, 0, 0)

    assert panel._groups[0] == [nome_b, nome_a]
    assert overlay.control.visible

    panel._restore()

    assert not overlay.control.visible
    assert panel._groups[0] == [nome_b, nome_a]


def test_refresh_without_columns_leaves_fullscreen(monkeypatch) -> None:
    _state, overlay, panel = _panel(monkeypatch, _refs())
    panel._maximize()
    assert overlay.control.visible

    monkeypatch.setattr(
        "xl_utils.ui.pages.merge.inspect_columns",
        lambda _sources: [],
    )
    panel.refresh()

    assert not overlay.control.visible
    assert not panel._confirm.visible
    assert not panel._maximize_button.visible
