"""E-mail curto para menus e diálogos, com o valor completo no tooltip."""

from __future__ import annotations

import flet as ft

from xl_utils.ui import theme

EMAIL_LIMIT = 28
HOVER_DELAY = ft.Duration(seconds=3)
HOVER_DURATION = ft.Duration(seconds=10)


def short_email(email: str, limit: int = EMAIL_LIMIT) -> str:
    """Encurta o e-mail preservando o começo; o fim vira reticências."""
    if len(email) <= limit:
        return email
    return f"{email[: limit - 1]}…"


def email_text(email: str, *, size: int = theme.FONT_SM) -> ft.Text:
    """Texto de e-mail truncado; o valor completo aparece no tooltip atrasado."""
    short = short_email(email)
    tooltip = None
    if short != email:
        tooltip = ft.Tooltip(
            message=email,
            wait_duration=HOVER_DELAY,
            show_duration=HOVER_DURATION,
        )
    return ft.Text(
        short,
        size=size,
        max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS,
        tooltip=tooltip,
    )
