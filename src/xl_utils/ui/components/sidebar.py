"""Barra lateral Dracula própria, montada para alinhar ícones e rótulos."""

import contextlib
from collections.abc import Callable, Sequence

import flet as ft

from xl_utils.ui import theme
from xl_utils.ui.assets import asset_path
from xl_utils.ui.pages.registry import ToolPage

LOGO_SIZE = 36
HOME_ID = "home"


def _logo_mark() -> ft.Control:
    """Ícone do app em `assets/icon.png`; sem o arquivo, o quadrado com “x”."""
    icon = asset_path("icon.png")
    if icon is not None:
        return ft.Image(
            src=icon.read_bytes(),
            width=LOGO_SIZE,
            height=LOGO_SIZE,
            fit=ft.BoxFit.CONTAIN,
            border_radius=9,
        )
    return ft.Container(
        content=ft.Text(
            "x",
            size=19,
            weight=ft.FontWeight.BOLD,
            color=theme.BACKGROUND_DEEP,
        ),
        width=LOGO_SIZE,
        height=LOGO_SIZE,
        bgcolor=theme.PURPLE,
        border_radius=9,
        alignment=ft.Alignment.CENTER,
    )


class Sidebar:
    """Barra lateral de largura fixa: Início, ferramentas e páginas de rodapé.

    Os itens são identificados pelo `id` da página (`HOME_ID` para o Início),
    nunca pela posição, para que a ordem da lista não afete a navegação.
    """

    def __init__(
        self,
        tools: Sequence[ToolPage],
        on_select: Callable[[str], None],
        *,
        footer: Sequence[ToolPage] = (),
        selected: str = HOME_ID,
        theme_mode: str = "dark",
        on_theme_change: Callable[[str], None] | None = None,
    ) -> None:
        self._on_select = on_select
        self._theme_mode = theme_mode
        self._on_theme_change = on_theme_change
        self._footer_pages = tuple(footer)
        self._items: dict[str, tuple[ft.Container, ft.Icon, ft.Text]] = {}

        navigation = ft.Column(
            controls=[
                self._item(HOME_ID, ft.Icons.HOME, "Início"),
                *[self._item(tool.id, tool.icon, tool.label) for tool in tools],
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

    def select(self, page_id: str) -> None:
        """Destaca um item (lista ou rodapé) e devolve os demais ao neutro."""
        for item_id, (container, icon, label) in self._items.items():
            active = item_id == page_id
            container.bgcolor = theme.SURFACE if active else None
            icon.color = theme.PURPLE if active else theme.MUTED
            label.color = theme.TEXT if active else theme.SUBTLE_TEXT
        self._refresh()

    def _item(
        self,
        page_id: str,
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
            on_click=lambda _event, item_id=page_id: self._click(item_id),
            ink=True,
        )
        self._items[page_id] = (container, icon_control, label_control)
        return container

    def _click(self, page_id: str) -> None:
        self.select(page_id)
        self._on_select(page_id)

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
        controls = [_logo_mark(), title]
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
        footer_items = [
            self._item(page.id, page.icon, page.label) for page in self._footer_pages
        ]
        status = ft.Container(
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
        return ft.Column(controls=[*footer_items, status], spacing=2)

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
