"""Seletor do JSON do cliente OAuth, compartilhado pelo menu e pelo cartão."""

from __future__ import annotations

from pathlib import Path

import flet as ft

from xl_utils.ui.drive import DriveSession

CLIENT_EXTENSIONS = ["json"]


class ClientImport:
    """Abre o seletor nativo e entrega à sessão o JSON escolhido pelo usuário."""

    def __init__(self, session: DriveSession) -> None:
        self._session = session
        self._picker = ft.FilePicker()
        self._attached = False

    async def pick(self, page: ft.Page) -> None:
        """Pede o arquivo e importa; o seletor é anexado uma única vez."""
        if not self._attached:
            page.services.append(self._picker)
            self._attached = True
        files = await self._picker.pick_files(
            dialog_title="Selecione o JSON do cliente OAuth",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=CLIENT_EXTENSIONS,
            allow_multiple=False,
        )
        paths = [Path(file.path) for file in files if file.path]
        if paths:
            self._session.import_client(paths[0])
