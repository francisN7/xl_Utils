"""Result card: status, output path, log and spreadsheet preview."""

import contextlib
from pathlib import Path

import flet as ft
import pandas as pd
import pyperclip

from xl_utils.shared.system import open_folder
from xl_utils.ui import theme
from xl_utils.ui.components.preview_table import PreviewTable


class ResultPanel:
    """Visual state of one tool result."""

    def __init__(self) -> None:
        self._output: Path | None = None
        self.preview = PreviewTable()

        self._icon = ft.Icon(ft.Icons.INFO_OUTLINE, color=theme.MUTED, size=18)
        self._status = ft.Text(
            "Aguardando arquivo.",
            size=12,
            weight=ft.FontWeight.BOLD,
        )
        self._detail = ft.Text("", size=11, color=theme.MUTED)
        self._path = ft.Text(
            "",
            size=10,
            font_family="Consolas",
            color=theme.CYAN,
            selectable=True,
            visible=False,
        )
        self._open_button = ft.OutlinedButton(
            "Abrir pasta",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=self._open_folder,
            visible=False,
        )
        self._copy_button = ft.IconButton(
            icon=ft.Icons.CONTENT_COPY,
            icon_size=16,
            tooltip="Copiar log",
            on_click=self._copy_log,
        )
        self._log = ft.Text(
            "",
            size=10,
            font_family="Consolas",
            color="#C9CBDC",
            selectable=True,
        )
        self._log_box = ft.Container(
            content=self._log,
            bgcolor=theme.BACKGROUND_DEEP,
            border=ft.Border.all(1, theme.BORDER),
            border_radius=8,
            padding=10,
        )
        self._log_section = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            "Log",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=theme.MUTED,
                        ),
                        self._copy_button,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                self._log_box,
            ],
            spacing=4,
            visible=False,
        )

        self.control = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        self._icon,
                        ft.Column(
                            controls=[self._status, self._detail],
                            spacing=0,
                            expand=True,
                        ),
                    ],
                    spacing=10,
                ),
                self._path,
                ft.Row(
                    controls=[self._open_button],
                    alignment=ft.MainAxisAlignment.START,
                ),
                self._log_section,
                ft.Divider(height=1, color=theme.BORDER),
                self.preview.control,
            ],
            spacing=10,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

    def set_idle(self, message: str = "Selecione um arquivo para começar.") -> None:
        self._output = None
        self._icon.name = ft.Icons.INFO_OUTLINE
        self._icon.color = theme.MUTED
        self._status.value = message
        self._detail.value = ""
        self._path.value = ""
        self._path.visible = False
        self._open_button.visible = False
        self.set_log([])
        self.preview.set_frames(None)
        self._refresh()

    def set_info(self, message: str, detail: str = "") -> None:
        self._icon.name = ft.Icons.INFO_OUTLINE
        self._icon.color = theme.CYAN
        self._status.value = message
        self._detail.value = detail
        self._refresh()

    def set_running(self, message: str = "Executando...") -> None:
        self._icon.name = ft.Icons.HOURGLASS_EMPTY
        self._icon.color = theme.YELLOW
        self._status.value = message
        self._detail.value = ""
        self._refresh()

    def set_success(
        self,
        output_path: Path,
        frames: dict[str, pd.DataFrame],
        message: str,
        detail: str = "",
    ) -> None:
        self._output = Path(output_path)
        self._icon.name = ft.Icons.CHECK_CIRCLE
        self._icon.color = theme.GREEN
        self._status.value = message
        self._detail.value = detail
        self._path.value = str(self._output)
        self._path.visible = True
        self._open_button.visible = True
        self.preview.set_frames(frames)
        self._refresh()

    def set_error(self, message: str, detail: str = "") -> None:
        self._output = None
        self._icon.name = ft.Icons.ERROR_OUTLINE
        self._icon.color = theme.RED
        self._status.value = message
        self._detail.value = detail
        self._path.visible = False
        self._open_button.visible = False
        self.preview.set_frames(None)
        self._refresh()

    def set_log(self, lines: list[str]) -> None:
        self._log.value = "\n".join(lines)
        self._log_section.visible = bool(lines)
        self._refresh()

    def append_log(self, line: str) -> None:
        current = self._log.value or ""
        self._log.value = f"{current}\n{line}".strip()
        self._log_section.visible = True
        self._refresh()

    def _open_folder(self, _event=None) -> None:
        if self._output is not None:
            open_folder(self._output)

    def _copy_log(self, _event=None) -> None:
        if not self._log.value:
            return
        with contextlib.suppress(Exception):
            pyperclip.copy(self._log.value)

    def _refresh(self) -> None:
        with contextlib.suppress(RuntimeError):
            self.control.update()
