"""Start screen with one card per tool."""

from collections.abc import Callable

import flet as ft

from xl_utils.ui import theme
from xl_utils.ui.pages.registry import TOOLS


def build_home(on_open: Callable[[str], None]) -> ft.Control:
    """Build the hub that links to every tool."""
    cards = [
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Icon(
                                    tool.icon,
                                    size=20,
                                    color=theme.PURPLE,
                                ),
                                bgcolor="#332B45",
                                border_radius=8,
                                padding=8,
                            ),
                            ft.Text(
                                tool.label,
                                size=theme.FONT_MD,
                                weight=ft.FontWeight.BOLD,
                                expand=True,
                            ),
                            ft.Icon(
                                ft.Icons.ARROW_FORWARD,
                                size=16,
                                color=theme.MUTED,
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Text(
                        tool.description,
                        size=theme.FONT_SM,
                        color=theme.MUTED,
                    ),
                    ft.Container(expand=True),
                    ft.Text(
                        "Abrir ferramenta →",
                        size=theme.FONT_SM,
                        weight=ft.FontWeight.BOLD,
                        color=theme.PURPLE,
                    ),
                ],
                spacing=10,
                expand=True,
            ),
            on_click=lambda _event, tool_id=tool.id: on_open(tool_id),
            bgcolor=theme.SURFACE,
            border=ft.Border.all(1, theme.BORDER),
            border_radius=12,
            padding=16,
            height=200,
            ink=True,
            col={"sm": 12, "md": 6, "lg": 3},
        )
        for tool in TOOLS
    ]

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(
                            "O que você precisa fazer hoje?",
                            size=theme.FONT_HERO,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            "Escolha uma ferramenta. O estado de cada uma é "
                            "preservado enquanto você navega.",
                            size=theme.FONT_SM,
                            color=theme.MUTED,
                        ),
                    ],
                    spacing=4,
                ),
                ft.ResponsiveRow(
                    controls=cards,
                    spacing=12,
                    run_spacing=12,
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.Text(
                    "Toda leitura passa pelo pipeline de texto seguro: nada de "
                    "notação científica, zeros perdidos ou emojis.",
                    size=theme.FONT_XS,
                    color=theme.MUTED,
                    italic=True,
                ),
            ],
            spacing=20,
            scroll=ft.ScrollMode.HIDDEN,
            expand=True,
        ),
        padding=24,
        expand=True,
    )
