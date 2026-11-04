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
    ) -> None:
        self._on_select = on_select
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
            label.color = theme.TEXT if active else "#C9CBDC"
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
            color="#C9CBDC",
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
        return ft.Container(
            content=ft.Row(
                controls=[
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
                    ft.Column(
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
                    ),
                ],
                spacing=10,
            ),
            padding=ft.Padding.only(left=8, top=6, bottom=20),
        )

    def _footer(self) -> ft.Control:
        return ft.Container(
            content=ft.Row(
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
            padding=ft.Padding.only(left=10, top=10),
        )

    def _refresh(self) -> None:
        with contextlib.suppress(RuntimeError):
            self.control.update()
