"""Shell do aplicativo: barra lateral, hub inicial e páginas de ferramenta."""

import argparse
import contextlib
from collections.abc import Sequence

import flet as ft

from xl_utils.shared import drive_cache, settings
from xl_utils.ui import theme
from xl_utils.ui.assets import window_icon
from xl_utils.ui.components.client_import import ClientImport
from xl_utils.ui.components.sidebar import HOME_ID, Sidebar
from xl_utils.ui.components.top_menu import TopMenu
from xl_utils.ui.drive import DriveSession
from xl_utils.ui.pages import FOOTER_PAGES, PAGES, TOOLS
from xl_utils.ui.pages.home import build_home
from xl_utils.ui.theme import build_theme


def main(page: ft.Page) -> None:
    """Monta a janela principal."""
    mode = theme.apply(settings.load_theme())
    drive_cache.reset()
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
    icon = window_icon()
    if icon is not None:
        page.window.icon = str(icon)

    content = ft.Container(expand=True)
    pages: dict[str, ft.Control] = {}
    pages_by_id = {tool.id: tool for tool in PAGES}

    def show(page_id: str) -> None:
        if page_id == HOME_ID:
            content.content = home
        else:
            if page_id not in pages:
                pages[page_id] = pages_by_id[page_id].build(drive)
            content.content = pages[page_id]
        content.update()

    def open_tool(tool_id: str) -> None:
        sidebar.select(tool_id)
        show(tool_id)

    def handle_select(page_id: str) -> None:
        show(page_id)

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
        footer=FOOTER_PAGES,
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
    show(HOME_ID)


WEB_HOST = "127.0.0.1"
WEB_PORT = 8550


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Lê as opções de linha de comando do app."""
    parser = argparse.ArgumentParser(prog="xl-utils")
    parser.add_argument(
        "--web",
        action="store_true",
        help="Serve a interface no navegador (só para conferência visual).",
    )
    parser.add_argument("--port", type=int, default=WEB_PORT, help="Porta do modo web.")
    return parser.parse_args(argv)


def run(argv: Sequence[str] | None = None) -> None:
    """Inicia o app desktop ou, com ``--web``, serve a mesma UI no navegador."""
    args = parse_args(argv)
    if args.web:
        ft.run(main, view=ft.AppView.WEB_BROWSER, host=WEB_HOST, port=args.port)
    else:
        ft.run(main)
