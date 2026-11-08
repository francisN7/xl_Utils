"""Shell do aplicativo: barra lateral, hub inicial e páginas de ferramenta."""

import contextlib

import flet as ft

from xl_utils.shared import settings
from xl_utils.ui import theme
from xl_utils.ui.components.client_import import ClientImport
from xl_utils.ui.components.sidebar import Sidebar
from xl_utils.ui.components.top_menu import TopMenu
from xl_utils.ui.drive import DriveSession
from xl_utils.ui.pages import TOOLS
from xl_utils.ui.pages.home import build_home
from xl_utils.ui.theme import build_theme


def main(page: ft.Page) -> None:
    """Monta a janela principal."""
    mode = theme.apply(settings.load_theme())
    drive = DriveSession()
    client_import = ClientImport(drive)

    page.title = "xl_Utils"
    page.padding = 0
    page.bgcolor = theme.BACKGROUND
    page.theme_mode = ft.ThemeMode.LIGHT if mode == "light" else ft.ThemeMode.DARK
    page.theme = build_theme("light")
    page.dark_theme = build_theme("dark")
    page.window.width = 1200
    page.window.height = 800
    page.window.min_width = 980
    page.window.min_height = 640
    page.window.left = 80
    page.window.top = 60

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

    def change_theme(next_mode: str) -> None:
        nonlocal mode
        if next_mode == mode:
            return
        with contextlib.suppress(OSError):
            settings.save_theme(next_mode)
        mapping = theme.color_mapping(mode, next_mode)
        theme.apply(next_mode)
        mode = next_mode
        page.bgcolor = theme.BACKGROUND
        page.theme_mode = ft.ThemeMode.LIGHT if mode == "light" else ft.ThemeMode.DARK
        theme.restyle(sidebar.control, mapping)
        theme.restyle(menu_overlay, mapping)
        theme.restyle(home, mapping)
        for view in pages.values():
            theme.restyle(view, mapping)
        page.update()

    sidebar = Sidebar(
        TOOLS,
        handle_select,
        theme_mode=mode,
        on_theme_change=change_theme,
    )
    home = build_home(open_tool)
    top_menu = TopMenu(drive, importer=client_import)
    menu_overlay = ft.Container(
        content=top_menu.control,
        right=16,
        top=18,
    )
    body = ft.Stack(controls=[content, menu_overlay], expand=True)

    shell = ft.Row(
        controls=[sidebar.control, body],
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
    )
    page.add(shell)
    show(0)


def run() -> None:
    """Inicia o aplicativo desktop."""
    ft.run(main)
