"""Diálogo “Configurar conta”: foto e apelido da conta selecionada.

A engrenagem do painel de perfis abre este diálogo. Tudo fica num rascunho
até o usuário clicar em Salvar; Cancelar fecha sem gravar nada (ADR 0031).
"""

from __future__ import annotations

import asyncio
import contextlib
from pathlib import Path

import flet as ft

from xl_utils.shared.accounts import Account
from xl_utils.shared.profiles import (
    NICKNAME_LIMIT,
    PHOTO_EXTENSIONS,
    PHOTO_MAX_BYTES,
    ProfileError,
    clean_nickname,
    normalize_photo,
)
from xl_utils.ui import theme
from xl_utils.ui.components.account_label import avatar, email_text, short_email
from xl_utils.ui.drive import DriveSession

DIALOG_WIDTH = 360
# Folga entre o diálogo e a borda da janela; com zoom de 125% a largura fixa cortava.
DIALOG_MARGIN = 96
DIALOG_MIN_WIDTH = 240
PREVIEW_RADIUS = 40


class AccountSettings:
    """Abre o diálogo da conta e grava foto e apelido só ao salvar."""

    def __init__(self, session: DriveSession) -> None:
        self._session = session
        self._picker = ft.FilePicker()
        self._attached = False
        self._account: Account | None = None
        self._photo: bytes | None = None
        self._dialog: ft.AlertDialog | None = None
        self._preview = ft.Container()
        self._message = ft.Text()
        self._remove_button = ft.TextButton()
        self._nickname = ft.TextField()

    @property
    def dialog(self) -> ft.AlertDialog | None:
        """Diálogo aberto por último (ou ``None``)."""
        return self._dialog

    @property
    def photo(self) -> bytes | None:
        """Foto do rascunho, já recortada e reduzida."""
        return self._photo

    @property
    def nickname_field(self) -> ft.TextField:
        """Campo do apelido no rascunho."""
        return self._nickname

    def open(self, page: ft.Page, account: Account) -> None:
        """Monta o rascunho com o perfil atual da conta e mostra o diálogo.

        Os controles nascem a cada abertura: nada do diálogo anterior é reusado.
        """
        profile = self._session.profile_for(account.email)
        self._account = account
        self._photo = profile.photo
        self._preview = ft.Container(alignment=ft.Alignment.CENTER)
        self._message = ft.Text("", size=theme.FONT_XS, visible=False)
        self._remove_button = ft.TextButton(
            "Remover foto",
            icon=ft.Icons.DELETE_OUTLINE,
            on_click=lambda _event: self.remove_photo(),
        )
        self._nickname = ft.TextField(
            label="Apelido",
            value=profile.nickname,
            hint_text=account.name.strip() or short_email(account.email),
            helper="Vazio usa o nome do Google.",
            max_length=NICKNAME_LIMIT,
            on_submit=lambda _event: self.save(page),
        )
        choose_button = ft.OutlinedButton(
            "Escolher foto",
            icon=ft.Icons.IMAGE_OUTLINED,
            on_click=lambda _event: page.run_task(self.choose, page),
        )
        self._sync_photo()
        self._dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Configurar conta"),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        self._preview,
                        ft.Container(
                            content=_muted(
                                email_text(account.email, size=theme.FONT_XS)
                            ),
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Row(
                            controls=[choose_button, self._remove_button],
                            alignment=ft.MainAxisAlignment.CENTER,
                            wrap=True,
                        ),
                        self._message,
                        self._nickname,
                    ],
                    spacing=12,
                    tight=True,
                ),
                width=_dialog_width(page),
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _event: self.cancel(page)),
                ft.FilledButton("Salvar", on_click=lambda _event: self.save(page)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(self._dialog)

    async def choose(self, page: ft.Page) -> None:
        """Pede a imagem, recorta e reduz fora da UI thread e atualiza a prévia."""
        if not self._attached:
            page.services.append(self._picker)
            self._attached = True
        files = await self._picker.pick_files(
            dialog_title="Escolha a foto da conta",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=PHOTO_EXTENSIONS,
            allow_multiple=False,
            with_data=True,
        )
        if not files:
            return
        picked = files[0]
        if picked.size and picked.size > PHOTO_MAX_BYTES:
            limit = PHOTO_MAX_BYTES // (1024 * 1024)
            self._show_message(f"A foto passa de {limit} MB; escolha uma menor.")
            self._update()
            return
        try:
            photo = await asyncio.to_thread(_read_photo, picked.bytes, picked.path)
        except ProfileError as error:
            self._show_message(str(error))
        except OSError:
            self._show_message("Não deu para abrir o arquivo escolhido.")
        else:
            self._photo = photo
            self._show_message("")
            self._sync_photo()
        self._update()

    def remove_photo(self) -> None:
        """Tira a foto do rascunho; o avatar volta às iniciais."""
        self._photo = None
        self._show_message("")
        self._sync_photo()
        self._update()

    def save(self, page: ft.Page) -> None:
        """Grava o rascunho na conta aberta e fecha o diálogo."""
        if self._account is None:
            return
        page.pop_dialog()
        self._session.save_profile(
            self._account.email,
            clean_nickname(self._nickname.value),
            self._photo,
        )

    def cancel(self, page: ft.Page) -> None:
        """Fecha sem gravar nada."""
        page.pop_dialog()

    def _sync_photo(self) -> None:
        if self._account is None:
            return
        self._preview.content = avatar(
            self._account,
            radius=PREVIEW_RADIUS,
            photo=self._photo,
        )
        self._remove_button.disabled = self._photo is None

    def _show_message(self, text: str) -> None:
        self._message.value = text
        self._message.color = theme.RED
        self._message.visible = bool(text)

    def _update(self) -> None:
        if self._dialog is None:
            return
        with contextlib.suppress(RuntimeError, AssertionError):
            self._dialog.update()


def _read_photo(data: bytes | None, path: str | None) -> bytes:
    """Bytes vindos do seletor; se não vierem, lê do caminho escolhido."""
    if not data and path:
        data = Path(path).read_bytes()
    return normalize_photo(data or b"")


def _dialog_width(page: ft.Page) -> int:
    """Largura que cabe na janela atual, sem passar de ``DIALOG_WIDTH``."""
    width = getattr(page, "width", None) or DIALOG_WIDTH + DIALOG_MARGIN
    return int(max(DIALOG_MIN_WIDTH, min(DIALOG_WIDTH, width - DIALOG_MARGIN)))


def _muted(text: ft.Text) -> ft.Text:
    text.color = theme.MUTED
    return text
