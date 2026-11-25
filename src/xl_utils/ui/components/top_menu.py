"""Painel de perfil do canto superior direito: contas do Google Drive."""

from __future__ import annotations

import contextlib

import flet as ft

from xl_utils.shared.accounts import Account
from xl_utils.ui import theme
from xl_utils.ui.components.account_label import avatar, display_name, email_text
from xl_utils.ui.components.client_import import ClientImport
from xl_utils.ui.drive import DriveSession

PANEL_WIDTH = 280
# Nome no topo: curto para caber na faixa ``theme.TOP_MENU_RESERVE``.
TRIGGER_NAME_LIMIT = 16


class TopMenu:
    """Avatar e nome da conta selecionada; o clique abre o painel de perfis.

    O painel mostra a conta selecionada, as outras numa lista retrátil e, fixos
    embaixo, “Adicionar conta” e “Sair”. O ``PopupMenuItem`` do Flet não tem
    submenu; por isso o painel é um ``SubmenuButton`` dentro de um ``MenuBar``
    transparente (ADR 0029).
    """

    def __init__(
        self,
        session: DriveSession,
        *,
        importer: ClientImport | None = None,
    ) -> None:
        self._session = session
        self._importer = importer
        self._submenu = ft.SubmenuButton(alignment_offset=ft.Offset(0, 6))
        self._bar = ft.MenuBar(controls=[self._submenu])
        self._build()
        session.subscribe(self._refresh)

    @property
    def control(self) -> ft.Control:
        """Devolve o gatilho para o cabeçalho da janela montar à direita."""
        return self._bar

    @property
    def trigger(self) -> ft.Control:
        """Conteúdo do botão do topo (avatar e nome, ou “Entrar com Google”)."""
        return self._submenu.content

    @property
    def panel(self) -> list[ft.Control]:
        """Controles do painel aberto, na ordem em que aparecem."""
        return list(self._submenu.controls)

    def refresh(self) -> None:
        """Remonta com os tokens atuais do tema e o estado da sessão."""
        self._refresh()

    def _build(self) -> None:
        self._bar.style = ft.MenuStyle(
            bgcolor=ft.Colors.TRANSPARENT,
            shadow_color=ft.Colors.TRANSPARENT,
            elevation=0,
            padding=0,
        )
        self._submenu.style = ft.ButtonStyle(
            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            shape=ft.RoundedRectangleBorder(radius=20),
            overlay_color=theme.SELECTED_BG,
        )
        self._submenu.menu_style = ft.MenuStyle(
            bgcolor=theme.SURFACE,
            padding=ft.Padding.symmetric(vertical=6),
            shape=ft.RoundedRectangleBorder(radius=12),
            side=ft.BorderSide(1, theme.BORDER),
        )
        self._submenu.content = self._trigger()
        self._submenu.controls = self._panel()

    def _trigger(self) -> ft.Control:
        session = self._session
        if session.busy:
            return ft.Text(
                "Conectando ao Google…",
                size=theme.FONT_SM,
                color=theme.YELLOW,
            )
        account = session.active_account
        if account is None:
            return ft.Row(
                controls=[
                    ft.Icon(ft.Icons.ACCOUNT_CIRCLE, color=theme.SUBTLE_TEXT, size=22),
                    ft.Text("Entrar com Google", size=theme.FONT_SM, color=theme.TEXT),
                ],
                spacing=8,
                tight=True,
            )
        return ft.Row(
            controls=[
                avatar(account),
                ft.Text(
                    display_name(account, TRIGGER_NAME_LIMIT),
                    size=theme.FONT_SM,
                    color=theme.TEXT,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Icon(ft.Icons.ARROW_DROP_DOWN, color=theme.SUBTLE_TEXT, size=20),
            ],
            spacing=8,
            tight=True,
        )

    def _panel(self) -> list[ft.Control]:
        session = self._session
        controls: list[ft.Control] = []

        if session.busy:
            controls.append(
                _note("Conectando ao Google…", theme.YELLOW),
            )
            return controls

        if session.error:
            controls.append(_note(session.error, theme.RED))

        account = session.active_account
        if account is None:
            controls.append(
                self._action("Entrar com Google", ft.Icons.ACCOUNT_CIRCLE, self._login)
            )
            return controls

        controls.append(_header(account))
        others = [item for item in session.accounts if item.email != account.email]
        if others:
            controls.append(
                ft.ExpansionTile(
                    title=ft.Text("Outras contas", size=theme.FONT_SM),
                    controls=[self._other(item) for item in others],
                    expanded=False,
                    dense=True,
                    text_color=theme.TEXT,
                    collapsed_text_color=theme.SUBTLE_TEXT,
                    icon_color=theme.TEXT,
                    collapsed_icon_color=theme.SUBTLE_TEXT,
                    tile_padding=ft.Padding.symmetric(horizontal=12),
                    shape=ft.RoundedRectangleBorder(radius=0),
                    collapsed_shape=ft.RoundedRectangleBorder(radius=0),
                    width=PANEL_WIDTH,
                )
            )
        controls.append(ft.Divider(height=1, color=theme.BORDER))
        controls.append(
            self._action("Adicionar conta", ft.Icons.PERSON_ADD, self._login)
        )
        controls.append(self._action("Sair", ft.Icons.LOGOUT, self._logout))
        return controls

    def _other(self, account: Account) -> ft.MenuItemButton:
        return ft.MenuItemButton(
            content=email_text(account.email),
            leading=avatar(account, radius=12),
            on_click=lambda _event, email=account.email: self._switch(email),
            width=PANEL_WIDTH,
        )

    def _action(self, label: str, icon: ft.IconData, handler) -> ft.MenuItemButton:
        return ft.MenuItemButton(
            content=ft.Text(label, size=theme.FONT_SM, color=theme.TEXT),
            leading=ft.Icon(icon, color=theme.SUBTLE_TEXT, size=18),
            on_click=handler,
            width=PANEL_WIDTH,
        )

    def _page(self) -> ft.Page | None:
        try:
            page = self._bar.page
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
        self._build()
        with contextlib.suppress(RuntimeError):
            self._bar.update()


def _header(account: Account) -> ft.Control:
    """Conta selecionada: avatar grande, nome e e-mail."""
    return ft.Container(
        content=ft.Row(
            controls=[
                avatar(account, radius=20),
                ft.Column(
                    controls=[
                        ft.Text(
                            display_name(account),
                            size=theme.FONT_MD,
                            weight=ft.FontWeight.W_600,
                            color=theme.TEXT,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        _muted(email_text(account.email, size=theme.FONT_XS)),
                    ],
                    spacing=2,
                    tight=True,
                    expand=True,
                ),
            ],
            spacing=12,
        ),
        padding=ft.Padding.symmetric(horizontal=14, vertical=10),
        width=PANEL_WIDTH,
    )


def _muted(text: ft.Text) -> ft.Text:
    text.color = theme.MUTED
    return text


def _note(message: str, color: str) -> ft.Control:
    return ft.Container(
        content=ft.Text(message, size=theme.FONT_XS, color=color),
        padding=ft.Padding.symmetric(horizontal=14, vertical=8),
        width=PANEL_WIDTH,
    )
