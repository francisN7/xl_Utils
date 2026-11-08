"""Menu hamburger do canto superior: contas do Google Drive."""

from __future__ import annotations

import contextlib

import flet as ft

from xl_utils.ui import theme
from xl_utils.ui.drive import DriveSession


class TopMenu:
    """Botão hamburger que lista, troca e encerra as contas do Drive."""

    def __init__(self, session: DriveSession) -> None:
        self._session = session
        self._button = ft.PopupMenuButton(
            icon=ft.Icons.MENU,
            icon_color=theme.SUBTLE_TEXT,
            icon_size=20,
            tooltip="Conta do Google Drive",
            items=self._items(),
        )
        session.subscribe(self._refresh)

    @property
    def control(self) -> ft.Control:
        """Devolve o botão para a sidebar montar no cabeçalho."""
        return self._button

    def _items(self) -> list[ft.PopupMenuItem]:
        session = self._session
        items: list[ft.PopupMenuItem] = []

        if session.busy:
            items.append(
                ft.PopupMenuItem(
                    content=ft.Text(
                        "Conectando ao Google…",
                        size=theme.FONT_SM,
                        color=theme.YELLOW,
                    ),
                    disabled=True,
                )
            )
            return items

        if session.error:
            items.append(
                ft.PopupMenuItem(
                    content=ft.Text(
                        session.error,
                        size=theme.FONT_XS,
                        color=theme.RED,
                    ),
                    disabled=True,
                )
            )

        if not session.accounts:
            items.append(
                ft.PopupMenuItem(
                    content="Entrar no Google Drive",
                    icon=ft.Icons.LOGIN,
                    on_click=self._login,
                )
            )
            return items

        items.append(
            ft.PopupMenuItem(
                content=ft.Text(
                    "Conta do Drive",
                    size=theme.FONT_XS,
                    color=theme.MUTED,
                ),
                disabled=True,
            )
        )
        items.extend(
            ft.PopupMenuItem(
                content=account.email,
                checked=account.email == session.active,
                on_click=lambda _event, email=account.email: self._switch(email),
            )
            for account in session.accounts
        )
        items.append(
            ft.PopupMenuItem(
                content="Adicionar outra conta",
                icon=ft.Icons.PERSON_ADD,
                on_click=self._login,
            )
        )
        if session.active:
            items.append(
                ft.PopupMenuItem(
                    content="Sair da conta ativa",
                    icon=ft.Icons.LOGOUT,
                    on_click=self._logout,
                )
            )
        return items

    def _login(self, _event: object = None) -> None:
        try:
            page = self._button.page
        except RuntimeError:
            return
        if page is None or not hasattr(page, "run_task"):
            return
        page.run_task(self._session.connect)

    def _switch(self, email: str) -> None:
        self._session.switch(email)

    def _logout(self, _event: object = None) -> None:
        self._session.logout()

    def _refresh(self) -> None:
        self._button.items = self._items()
        with contextlib.suppress(RuntimeError):
            self._button.update()
