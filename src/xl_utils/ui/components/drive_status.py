"""Cartão de estado do Drive na tela inicial: entrar, trocar e sair."""

from __future__ import annotations

import contextlib

import flet as ft

from xl_utils.ui import theme
from xl_utils.ui.drive import DriveSession


class DriveStatus:
    """Cartão do hub que mostra a conta ativa e as ações do Drive."""

    def __init__(self, session: DriveSession) -> None:
        self._session = session
        self._title = ft.Text("", size=theme.FONT_MD, weight=ft.FontWeight.BOLD)
        self._detail = ft.Text("", size=theme.FONT_SM, color=theme.MUTED)
        self._login = ft.OutlinedButton(
            "Entrar com Google",
            icon=ft.Icons.LOGIN,
            on_click=self._login_clicked,
        )
        self._switch = ft.TextButton(
            "Trocar de conta",
            icon=ft.Icons.SWAP_HORIZ,
            on_click=self._switch_clicked,
        )
        self._logout = ft.TextButton(
            "Sair",
            icon=ft.Icons.LOGOUT,
            on_click=self._logout_clicked,
        )
        self._control = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.ADD_TO_DRIVE,
                            size=20,
                            color=theme.PURPLE,
                        ),
                        bgcolor=theme.ICON_BG,
                        border_radius=8,
                        padding=8,
                    ),
                    ft.Column(
                        controls=[self._title, self._detail],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Row(
                        controls=[self._login, self._switch, self._logout],
                        spacing=4,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=theme.SURFACE,
            border=ft.Border.all(1, theme.BORDER),
            border_radius=12,
            padding=16,
        )
        session.subscribe(self._refresh)
        self._refresh()

    @property
    def control(self) -> ft.Control:
        """Devolve o cartão para o hub montar."""
        return self._control

    def _login_clicked(self, _event: object = None) -> None:
        try:
            page = self._control.page
        except RuntimeError:
            return
        if page is None or not hasattr(page, "run_task"):
            return
        page.run_task(self._session.connect)

    def _switch_clicked(self, _event: object = None) -> None:
        target = self._session.next_account()
        if target is not None:
            self._session.switch(target)

    def _logout_clicked(self, _event: object = None) -> None:
        self._session.logout()

    def _refresh(self) -> None:
        session = self._session
        self._title.value = session.status

        if session.error:
            self._detail.value = session.error
            self._detail.color = theme.RED
        elif session.busy:
            self._detail.value = "Autorize no navegador; esta tela volta sozinha."
            self._detail.color = theme.YELLOW
        elif session.active:
            account = session.active_account
            name = account.name if account is not None else ""
            self._detail.value = (
                f"Conectado como {name}." if name else "Conta ativa para o Drive."
            )
            self._detail.color = theme.MUTED
        elif session.accounts:
            self._detail.value = "Escolha a conta ativa no menu ou aqui."
            self._detail.color = theme.MUTED
        else:
            self._detail.value = (
                "Entre para ler e gravar planilhas no Drive nas próximas etapas."
            )
            self._detail.color = theme.MUTED

        self._login.content = (
            "Adicionar conta" if session.accounts else "Entrar com Google"
        )
        self._login.disabled = session.busy
        self._switch.visible = len(session.accounts) > 1 and not session.busy
        self._logout.visible = session.active is not None and not session.busy

        with contextlib.suppress(RuntimeError):
            self._control.update()
