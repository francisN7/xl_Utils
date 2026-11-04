"""Application shell: sidebar, home hub and tool pages."""

import flet as ft

from xl_utils.ui import theme
from xl_utils.ui.components.sidebar import Sidebar
from xl_utils.ui.pages import TOOLS
from xl_utils.ui.pages.home import build_home
from xl_utils.ui.theme import build_theme


def main(page: ft.Page) -> None:
    """Build the main window."""
    page.title = "xl_Utils"
    page.padding = 0
    page.bgcolor = theme.BACKGROUND
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = build_theme()
    page.dark_theme = build_theme()
    page.window.width = 1200
    page.window.height = 800
    page.window.min_width = 980
    page.window.min_height = 640

    content = ft.Container(expand=True)
    pages: dict[str, ft.Control] = {}

    def show(index: int) -> None:
        if index == 0:
            content.content = home
        else:
            tool = TOOLS[index - 1]
            content.content = pages.setdefault(tool.id, tool.build())
        content.update()

    def open_tool(tool_id: str) -> None:
        index = next(
            position + 1 for position, tool in enumerate(TOOLS) if tool.id == tool_id
        )
        sidebar.select(index)
        show(index)

    def handle_select(index: int) -> None:
        show(index)

    sidebar = Sidebar(TOOLS, handle_select)
    home = build_home(open_tool)

    page.add(
        ft.Row(
            controls=[sidebar.control, content],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )
    )
    show(0)


def run() -> None:
    """Start the desktop application."""
    ft.run(main)
