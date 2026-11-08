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

    async def pick(self, page: ft.Page) -> bool:
        """Pede o arquivo e importa; devolve ``True`` se o cliente ficou pronto.

        O seletor é anexado uma única vez à página. A importação só acontece se
        o usuário escolher um arquivo; cancelar não altera o estado.
        """
        if not self._attached:
            page.services.append(self._picker)
            self._attached = True
        files = await self._picker.pick_files(
            dialog_title="Selecione o JSON do cliente OAuth (só na primeira vez)",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=CLIENT_EXTENSIONS,
            allow_multiple=False,
        )
        paths = [Path(file.path) for file in files if file.path]
        if not paths:
            return False
        self._session.import_client(paths[0])
        return self._session.configured
