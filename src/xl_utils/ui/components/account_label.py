"""Rótulos de conta: e-mail curto, nome de exibição e avatar com a inicial."""

from __future__ import annotations

import flet as ft

from xl_utils.shared.accounts import Account
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


def initials(account: Account) -> str:
    """Até duas iniciais do nome; sem nome, do e-mail."""
    source = account.name or account.email
    parts = [part for part in source.replace("@", " ").split() if part]
    return "".join(part[0].upper() for part in parts[:2]) or "G"


def display_name(account: Account, limit: int = EMAIL_LIMIT) -> str:
    """Nome curto para o topo e o painel: o nome da conta ou o e-mail curto."""
    return short_email(account.name.strip() or account.email, limit)


def avatar(account: Account, *, radius: int = 14) -> ft.CircleAvatar:
    """Círculo com as iniciais da conta, nas cores do tema."""
    return ft.CircleAvatar(
        content=ft.Text(
            initials(account),
            size=max(10, int(radius * 0.8)),
            weight=ft.FontWeight.W_600,
            color=theme.BACKGROUND,
        ),
        bgcolor=theme.PURPLE,
        radius=radius,
    )
