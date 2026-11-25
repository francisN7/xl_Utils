"""Navegação da sidebar por `id`, com Plugins fixo no rodapé."""

import flet as ft

from xl_utils.ui import theme
from xl_utils.ui.components.sidebar import HOME_ID, Sidebar
from xl_utils.ui.pages.registry import FOOTER_PAGES, TOOLS


def _sidebar(selected: list[str]) -> Sidebar:
    return Sidebar(TOOLS, selected.append, footer=FOOTER_PAGES)


def _active(sidebar: Sidebar) -> list[str]:
    return [
        page_id
        for page_id, (container, _icon, _label) in sidebar._items.items()
        if container.bgcolor == theme.SURFACE
    ]


def _labels(control: ft.Control) -> list[str]:
    found: list[str] = []
    if isinstance(control, ft.Text) and isinstance(control.value, str):
        found.append(control.value)
    for child in getattr(control, "controls", None) or []:
        found.extend(_labels(child))
    content = getattr(control, "content", None)
    if isinstance(content, ft.Control):
        found.extend(_labels(content))
    return found


def test_plugins_sits_in_the_footer_above_the_runtime_line() -> None:
    sidebar = _sidebar([])

    footer = sidebar.control.content.controls[-1]
    labels = _labels(footer)

    assert labels.index("Plugins") < labels.index("uv · Python 3.15")
    navigation = sidebar.control.content.controls[1]
    assert "Plugins" not in _labels(navigation)


def test_footer_click_opens_plugins_and_marks_only_it() -> None:
    selected: list[str] = []
    sidebar = _sidebar(selected)
    assert _active(sidebar) == [HOME_ID]

    sidebar._click("plugins")

    assert selected == ["plugins"]
    assert _active(sidebar) == ["plugins"]

    sidebar._click("cut")

    assert selected == ["plugins", "cut"]
    assert _active(sidebar) == ["cut"]


def test_select_by_tool_id_ignores_list_position() -> None:
    sidebar = _sidebar([])

    for tool in (*TOOLS, *FOOTER_PAGES):
        sidebar.select(tool.id)
        assert _active(sidebar) == [tool.id]

    sidebar.select(HOME_ID)
    assert _active(sidebar) == [HOME_ID]
