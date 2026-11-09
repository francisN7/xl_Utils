"""Menu hamburger do canto superior direito: perfis do Google Drive."""

from __future__ import annotations

import contextlib

import flet as ft

from xl_utils.ui import theme
from xl_utils.ui.components.account_label import email_text
from xl_utils.ui.components.client_import import ClientImport
from xl_utils.ui.drive import DriveSession


class TopMenu:
    """Botão hamburger que lista, troca e encerra os perfis do Drive."""

    def __init__(
        self,
        session: DriveSession,
        *,
        importer: ClientImport | None = None,
    ) -> None:
        self._session = session
        self._importer = importer
        self._button = ft.PopupMenuButton(
            icon=ft.Icons.MENU,
            icon_color=theme.SUBTLE_TEXT,
            icon_size=20,
            tooltip="Perfis do Google Drive",
            items=self._items(),
        )
        session.subscribe(self._refresh)

    @property
    def control(self) -> ft.Control:
        """Devolve o botão para o cabeçalho da janela montar à direita."""
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
                    content="Entrar com Google",
                    icon=ft.Icons.ACCOUNT_CIRCLE,
                    on_click=self._login,
                )
            )
            return items

        items.append(
            ft.PopupMenuItem(
                content=ft.Text(
                    "Perfis do Google Drive",
                    size=theme.FONT_XS,
                    color=theme.MUTED,
                ),
                disabled=True,
            )
        )
        items.extend(
            ft.PopupMenuItem(
                content=email_text(account.email),
                icon=ft.Icons.ACCOUNT_CIRCLE,
                checked=account.email == session.active,
                on_click=lambda _event, email=account.email: self._switch(email),
            )
            for account in session.accounts
        )
        items.append(
            ft.PopupMenuItem(
                content="Adicionar conta",
                icon=ft.Icons.PERSON_ADD,
                on_click=self._login,
            )
        )
        if session.active:
            items.append(
                ft.PopupMenuItem(
                    content="Sair desta conta",
                    icon=ft.Icons.LOGOUT,
                    on_click=self._logout,
                )
            )
        return items

    def _page(self) -> ft.Page | None:
        try:
            page = self._button.page
        except RuntimeError:
            return None
        if page is None or not hasattr(page, "run_task"):
            return None
        return page

    def _login(self, _event: object = None) -> None:
        page = self._page()
        if page is None:
            return
        if not self._session.configured and self._importer is not None:
            page.run_task(self._login_with_client, page)
            return
        page.run_task(self._session.connect)

    async def _login_with_client(self, page: ft.Page) -> None:
        """Pede o cliente uma única vez e, se importado, abre o navegador."""
        if self._importer is None:
            return
        if await self._importer.pick(page):
            await self._session.connect()

    def _switch(self, email: str) -> None:
        self._session.switch(email)

    def _logout(self, _event: object = None) -> None:
        self._session.logout()

    def _refresh(self) -> None:
        self._button.items = self._items()
        with contextlib.suppress(RuntimeError):
            self._button.update()
