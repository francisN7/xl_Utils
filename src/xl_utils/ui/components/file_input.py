"""Seletor de arquivo clicável usado por todas as ferramentas."""

import contextlib
from collections.abc import Callable, Sequence
from pathlib import Path

import flet as ft

from xl_utils.core.mime import FormatCheck
from xl_utils.ui import theme

ALLOWED_EXTENSIONS = ["xlsx", "xlsm", "xls", "csv", "html", "htm"]


class FileInput:
    """Área no estilo dropzone que abre o seletor nativo ao clique."""

    def __init__(
        self,
        on_change: Callable[[list[Path]], None],
        *,
        multiple: bool = False,
    ) -> None:
        self._on_change = on_change
        self._multiple = multiple
        self._files: list[Path] = []
        self._formats: dict[Path, FormatCheck] = {}
        self._picker = ft.FilePicker()
        self._picker_attached = False

        self._dropzone_text = ft.Text(
            "Clique para selecionar as planilhas"
            if multiple
            else "Clique para selecionar a planilha",
            size=theme.FONT_SM,
            weight=ft.FontWeight.BOLD,
        )
        self._file_rows = ft.Column(spacing=6)
        self._hint = ft.Text(
            "Nenhum arquivo selecionado.",
            size=theme.FONT_XS,
            color=theme.MUTED,
        )

        self._dropzone = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.UPLOAD_FILE, size=26, color=theme.PURPLE),
                    self._dropzone_text,
                    ft.Text(
                        "seletor nativo · .xlsx, .xls, .csv, .html",
                        size=theme.FONT_XS,
                        color=theme.MUTED,
                    ),
                ],
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            on_click=self._open_picker,
            border=ft.Border.all(1, theme.BORDER),
            border_radius=12,
            padding=22,
            bgcolor=theme.BACKGROUND_DEEP,
            ink=True,
        )

        self.control = ft.Column(
            controls=[self._dropzone, self._file_rows, self._hint],
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

    def _open_picker(self, _event=None) -> None:
        try:
            page = self.control.page
        except RuntimeError:
            return
        if not self._picker_attached:
            page.services.append(self._picker)
            self._picker_attached = True
        page.run_task(self._pick)

    async def _pick(self) -> None:
        files = await self._picker.pick_files(
            dialog_title="Selecione a planilha",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=ALLOWED_EXTENSIONS,
            allow_multiple=self._multiple,
        )
        paths = [Path(file.path) for file in files if file.path]
        if paths:
            self.set_files(paths)

    def set_files(self, paths: list[Path]) -> None:
        if self._multiple:
            for path in paths:
                if path not in self._files:
                    self._files.append(path)
        else:
            self._files = list(paths[:1])
        self._render()
        self._on_change(list(self._files))

    def set_formats(self, checks: Sequence[FormatCheck]) -> None:
        """Guarda a checagem de formato de cada arquivo e atualiza a lista."""
        self._formats = {check.path: check for check in checks}
        self._render()

    def _remove(self, path: Path) -> None:
        self._files = [item for item in self._files if item != path]
        self._render()
        self._on_change(list(self._files))

    def _render(self) -> None:
        self._file_rows.controls = [self._file_row(path) for path in self._files]
        if self._files:
            self._hint.value = f"{len(self._files)} arquivo(s) selecionado(s)."
            self._dropzone_text.value = (
                "Adicionar outro arquivo" if self._multiple else "Trocar a planilha"
            )
        else:
            self._hint.value = "Nenhum arquivo selecionado."
            self._dropzone_text.value = (
                "Clique para selecionar as planilhas"
                if self._multiple
                else "Clique para selecionar a planilha"
            )
        self._dropzone.visible = self._multiple or not self._files
        self._refresh()

    def _file_row(self, path: Path) -> ft.Control:
        try:
            size = path.stat().st_size
        except OSError:
            size = 0

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            path.suffix.upper().lstrip(".") or "FILE",
                            size=theme.FONT_XS,
                            weight=ft.FontWeight.BOLD,
                            color=theme.GREEN,
                        ),
                        bgcolor=theme.SUCCESS_BG,
                        border_radius=5,
                        padding=6,
                    ),
                    ft.Column(
                        controls=self._file_details(path, size),
                        spacing=0,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        icon_size=16,
                        tooltip="Remover",
                        on_click=lambda _event, item=path: self._remove(item),
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=theme.BACKGROUND_DEEP,
            border=ft.Border.all(1, theme.BORDER),
            border_radius=8,
            padding=9,
        )

    def _file_details(self, path: Path, size: int) -> list[ft.Control]:
        details: list[ft.Control] = [
            ft.Text(path.name, size=theme.FONT_SM),
            ft.Text(
                _format_size(size),
                size=theme.FONT_XS,
                color=theme.MUTED,
            ),
        ]
        check = self._formats.get(path)
        if check is not None and not check.identified:
            details.append(
                ft.Text(
                    f"Não foi possível identificar o formato ({check.reason})",
                    size=theme.FONT_XS,
                    color=theme.RED,
                )
            )
        elif check is not None and check.diverges:
            details.append(
                ft.Text(
                    check.reason,
                    size=theme.FONT_XS,
                    color=theme.ORANGE,
                )
            )
        return details

    def _refresh(self) -> None:
        with contextlib.suppress(RuntimeError):
            self.control.update()


def _format_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"
