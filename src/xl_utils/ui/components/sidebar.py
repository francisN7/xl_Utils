"""Barra lateral Dracula própria, montada para alinhar ícones e rótulos."""

import contextlib
from collections.abc import Callable, Sequence

import flet as ft

from xl_utils.ui import theme
from xl_utils.ui.pages.registry import ToolPage


class Sidebar:
    """Barra lateral de largura fixa com Início e um item por ferramenta."""

    def __init__(
        self,
        tools: Sequence[ToolPage],
        on_select: Callable[[int], None],
        *,
        selected: int = 0,
        theme_mode: str = "dark",
        on_theme_change: Callable[[str], None] | None = None,
        menu: ft.Control | None = None,
    ) -> None:
        self._on_select = on_select
        self._theme_mode = theme_mode
        self._on_theme_change = on_theme_change
        self._menu = menu
        self._items: list[tuple[ft.Container, ft.Icon, ft.Text]] = []

        navigation = ft.Column(
            controls=[
                self._item(0, ft.Icons.HOME, "Início"),
                *[
                    self._item(index + 1, tool.icon, tool.label)
                    for index, tool in enumerate(tools)
                ],
            ],
            spacing=2,
        )

        self.control = ft.Container(
            content=ft.Column(
                controls=[
                    self._logo(),
                    navigation,
                    ft.Container(expand=True),
                    self._footer(),
                ],
                spacing=0,
                expand=True,
            ),
            width=260,
            bgcolor=theme.BACKGROUND_DEEP,
            border=ft.Border.only(
                right=ft.BorderSide(1, theme.BORDER),
            ),
            padding=ft.Padding.only(
                left=10,
                right=10,
                top=12,
                bottom=12,
            ),
        )
        self.select(selected)

    def select(self, index: int) -> None:
        """Destaca um item e devolve o anterior ao estado neutro."""
        for position, (container, icon, label) in enumerate(self._items):
            active = position == index
            container.bgcolor = theme.SURFACE if active else None
            icon.color = theme.PURPLE if active else theme.MUTED
            label.color = theme.TEXT if active else theme.SUBTLE_TEXT
        self._refresh()

    def _item(
        self,
        index: int,
        icon: ft.IconData,
        label: str,
    ) -> ft.Container:
        icon_control = ft.Icon(icon, size=20, color=theme.MUTED)
        label_control = ft.Text(
            label,
            size=14,
            color=theme.SUBTLE_TEXT,
            expand=True,
        )
        container = ft.Container(
            content=ft.Row(
                controls=[icon_control, label_control],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(vertical=10, horizontal=10),
            border_radius=8,
            on_click=lambda _event, position=index: self._click(position),
            ink=True,
        )
        self._items.append((container, icon_control, label_control))
        return container

    def _click(self, index: int) -> None:
        self.select(index)
        self._on_select(index)

    def _logo(self) -> ft.Control:
        title = ft.Column(
            controls=[
                ft.Text(
                    "xl_Utils",
                    size=17,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "planilhas",
                    size=theme.FONT_XS,
                    color=theme.MUTED,
                ),
            ],
            spacing=0,
            expand=True,
        )
        controls = [
            ft.Container(
                content=ft.Text(
                    "x",
                    size=19,
                    weight=ft.FontWeight.BOLD,
                    color=theme.BACKGROUND_DEEP,
                ),
                width=36,
                height=36,
                bgcolor=theme.PURPLE,
                border_radius=9,
                alignment=ft.Alignment.CENTER,
            ),
            title,
        ]
        if self._menu is not None:
            controls.append(self._menu)
        return ft.Container(
            content=ft.Row(
                controls=controls,
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.only(left=8, top=6, bottom=20),
        )

    def _footer(self) -> ft.Control:
        self._theme_button = ft.TextButton(
            self._theme_action_label(),
            icon=self._theme_action_icon(),
            on_click=self._toggle_theme,
            style=ft.ButtonStyle(
                padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                text_style=ft.TextStyle(size=theme.FONT_SM),
                color=theme.SUBTLE_TEXT,
                icon_color=theme.MUTED,
            ),
        )
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                width=7,
                                height=7,
                                border_radius=999,
                                bgcolor=theme.GREEN,
                            ),
                            ft.Text(
                                "uv · Python 3.15",
                                size=theme.FONT_XS,
                                color=theme.MUTED,
                            ),
                        ],
                        spacing=7,
                    ),
                    self._theme_button,
                ],
                spacing=2,
            ),
            padding=ft.Padding.only(left=10, top=10),
        )

    def _theme_action_label(self) -> str:
        return "Tema claro" if self._theme_mode == "dark" else "Tema escuro"

    def _theme_action_icon(self) -> ft.IconData:
        return ft.Icons.LIGHT_MODE if self._theme_mode == "dark" else ft.Icons.DARK_MODE

    def _toggle_theme(self, _event: object = None) -> None:
        self._theme_mode = "light" if self._theme_mode == "dark" else "dark"
        self._theme_button.content = self._theme_action_label()
        self._theme_button.icon = self._theme_action_icon()
        if self._on_theme_change is not None:
            self._on_theme_change(self._theme_mode)
        self._refresh()

    def _refresh(self) -> None:
        with contextlib.suppress(RuntimeError):
            self.control.update()
